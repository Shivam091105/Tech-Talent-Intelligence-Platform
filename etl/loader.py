"""
PostgreSQL Loader — inserts validated records into the normalized database schema.
Handles all reference table upserts and junction table population.
"""

from sqlalchemy import text

from database.connection import get_engine
from config.logging_config import setup_logger

logger = setup_logger("etl.loader")


def load_to_database(validated_records: list) -> dict:
    """
    Load validated JobRecord instances into the PostgreSQL database.

    Insertion order (respecting foreign keys):
        1. companies
        2. locations
        3. skills (from dictionary)
        4. jobs (references companies, locations, experience_levels)
        5. salaries (references jobs)
        6. job_skills (references jobs, skills)

    Returns:
        dict with counts of records loaded per table.
    """
    engine = get_engine()
    stats = {
        "companies": 0, "locations": 0, "skills": 0,
        "jobs": 0, "salaries": 0, "job_skills": 0,
    }

    # Cache for reference table lookups (avoid repeated queries)
    company_cache = {}   # company_name → company_id
    location_cache = {}  # (city, country) → location_id
    skill_cache = {}     # skill_name → skill_id
    exp_cache = {}       # level_name → level_id

    with engine.connect() as conn:
        # ------------------------------------------------------------------
        # Pre-load experience_levels cache (seeded in schema.sql)
        # ------------------------------------------------------------------
        rows = conn.execute(text("SELECT level_id, level_name FROM experience_levels")).fetchall()
        exp_cache = {row[1]: row[0] for row in rows}
        logger.info("Loaded %d experience levels from database", len(exp_cache))

        # ------------------------------------------------------------------
        # Pre-load skills from dictionary into skills table
        # ------------------------------------------------------------------
        import json
        from config.settings import DICTIONARIES_DIR

        skills_dict_path = DICTIONARIES_DIR / "skills_dictionary.json"
        with open(skills_dict_path, "r", encoding="utf-8") as f:
            skills_dict = json.load(f)

        for skill_name, info in skills_dict.items():
            category = info.get("category", "tool")
            result = conn.execute(
                text("""
                    INSERT INTO skills (skill_name, skill_category)
                    VALUES (:name, :category)
                    ON CONFLICT (skill_name) DO NOTHING
                    RETURNING skill_id
                """),
                {"name": skill_name, "category": category}
            ).fetchone()

            if result:
                skill_cache[skill_name] = result[0]
                stats["skills"] += 1

        # Load any skills already in DB
        existing_skills = conn.execute(text("SELECT skill_id, skill_name FROM skills")).fetchall()
        for row in existing_skills:
            skill_cache[row[1]] = row[0]

        conn.commit()
        logger.info("Loaded %d skills into database", stats["skills"])

        # ------------------------------------------------------------------
        # Process each job record
        # ------------------------------------------------------------------
        for record in validated_records:
            try:
                # --- Company ---
                comp_name = record.company_name
                if comp_name not in company_cache:
                    result = conn.execute(
                        text("""
                            INSERT INTO companies (company_name, company_type, company_rating)
                            VALUES (:name, :type, :rating)
                            ON CONFLICT (company_name) DO UPDATE SET
                                company_type = COALESCE(EXCLUDED.company_type, companies.company_type),
                                company_rating = COALESCE(EXCLUDED.company_rating, companies.company_rating)
                            RETURNING company_id
                        """),
                        {
                            "name": comp_name,
                            "type": record.company_type,
                            "rating": record.company_rating,
                        }
                    ).fetchone()
                    company_cache[comp_name] = result[0]
                    stats["companies"] += 1

                company_id = company_cache[comp_name]

                # --- Location ---
                loc_key = (record.city, record.country)
                if loc_key not in location_cache:
                    result = conn.execute(
                        text("""
                            INSERT INTO locations (city, state, country)
                            VALUES (:city, :state, :country)
                            ON CONFLICT (city, country) DO UPDATE SET
                                state = COALESCE(EXCLUDED.state, locations.state)
                            RETURNING location_id
                        """),
                        {
                            "city": record.city,
                            "state": record.state,
                            "country": record.country,
                        }
                    ).fetchone()
                    location_cache[loc_key] = result[0]
                    stats["locations"] += 1

                location_id = location_cache[loc_key]

                # --- Experience Level ---
                exp_level_id = exp_cache.get(record.experience_level, exp_cache.get("Entry"))

                # --- Job ---
                # Parse posted_date
                posted_date = None
                if record.posted_date and record.posted_date != "None":
                    try:
                        from dateutil import parser as dateparser
                        posted_date = dateparser.parse(record.posted_date).date()
                    except Exception:
                        posted_date = None

                result = conn.execute(
                    text("""
                        INSERT INTO jobs (job_title, company_id, location_id, experience_level_id,
                                         work_mode, employment_type, posted_date, source_dataset)
                        VALUES (:title, :company_id, :location_id, :exp_id,
                                :work_mode, :emp_type, :posted_date, :source)
                        RETURNING job_id
                    """),
                    {
                        "title": record.job_title,
                        "company_id": company_id,
                        "location_id": location_id,
                        "exp_id": exp_level_id,
                        "work_mode": record.work_mode,
                        "emp_type": record.employment_type,
                        "posted_date": posted_date,
                        "source": record.source_dataset,
                    }
                ).fetchone()
                job_id = result[0]
                stats["jobs"] += 1

                # --- Salary ---
                if record.avg_salary_usd is not None:
                    conn.execute(
                        text("""
                            INSERT INTO salaries (job_id, min_salary_usd, max_salary_usd, avg_salary_usd)
                            VALUES (:job_id, :min_sal, :max_sal, :avg_sal)
                            ON CONFLICT (job_id) DO NOTHING
                        """),
                        {
                            "job_id": job_id,
                            "min_sal": record.min_salary_usd,
                            "max_sal": record.max_salary_usd,
                            "avg_sal": record.avg_salary_usd,
                        }
                    )
                    stats["salaries"] += 1

                # --- Job Skills (junction table) ---
                for skill_name in record.extracted_skills:
                    skill_id = skill_cache.get(skill_name)
                    if skill_id:
                        conn.execute(
                            text("""
                                INSERT INTO job_skills (job_id, skill_id)
                                VALUES (:job_id, :skill_id)
                                ON CONFLICT DO NOTHING
                            """),
                            {"job_id": job_id, "skill_id": skill_id}
                        )
                        stats["job_skills"] += 1

            except Exception as e:
                logger.warning("Error loading record '%s': %s", record.job_title[:50], e)
                continue

        conn.commit()

    logger.info("=" * 60)
    logger.info("Database loading complete:")
    for table, count in stats.items():
        logger.info("  %-15s : %d records", table, count)
    logger.info("=" * 60)

    return stats
