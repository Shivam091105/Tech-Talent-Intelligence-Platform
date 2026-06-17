"""
All analytical SQL queries as Python functions.
Each function returns a Pandas DataFrame ready for visualization.
Queries are parameterized to support dashboard filters (e.g., country, source_dataset).
"""

from database.connection import execute_query_df

# ===========================================================================
# Helper: Build optional WHERE clause for filters
# ===========================================================================

def _build_filters(country: str = None, source_dataset: str = None) -> tuple:
    """
    Build WHERE clause fragments and params dict for common dashboard filters.

    Returns:
        (where_clause: str, params: dict)
    """
    conditions = []
    params = {}

    if country:
        conditions.append("l.country = :country")
        params["country"] = country

    if source_dataset:
        conditions.append("j.source_dataset = :source_dataset")
        params["source_dataset"] = source_dataset

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    return where, params


# ===========================================================================
# Executive Dashboard Queries
# ===========================================================================

def get_total_jobs(country=None, source_dataset=None):
    """Total number of job postings."""
    where, params = _build_filters(country, source_dataset)
    # Need location join if country filter is used
    join = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT COUNT(*) AS total_jobs
        FROM jobs j
        {join}
        {where}
    """
    if not country:
        query = query.replace(":country", "").replace("l.country =", "")
    return execute_query_df(query, params)


def get_avg_salary(country=None, source_dataset=None):
    """Overall average salary in USD."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT ROUND(AVG(s.avg_salary_usd)::numeric, 2) AS avg_salary
        FROM salaries s
        JOIN jobs j ON s.job_id = j.job_id
        {join_loc}
        {where}
    """
    return execute_query_df(query, params)


def get_top_skill(country=None, source_dataset=None):
    """Most in-demand skill by job count."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT sk.skill_name, COUNT(DISTINCT js.job_id) AS job_count
        FROM skills sk
        JOIN job_skills js ON sk.skill_id = js.skill_id
        JOIN jobs j ON js.job_id = j.job_id
        {join_loc}
        {where}
        GROUP BY sk.skill_name
        ORDER BY job_count DESC
        LIMIT 1
    """
    return execute_query_df(query, params)


def get_top_hiring_city(country=None, source_dataset=None):
    """City with the most job postings."""
    where, params = _build_filters(country, source_dataset)
    if not country:
        # Still need location join
        pass
    query = f"""
        SELECT l.city, COUNT(*) AS job_count
        FROM jobs j
        JOIN locations l ON j.location_id = l.location_id
        {("WHERE " + " AND ".join([c for c in [
            "l.country = :country" if country else None,
            "j.source_dataset = :source_dataset" if source_dataset else None
        ] if c])) if (country or source_dataset) else ""}
        GROUP BY l.city
        ORDER BY job_count DESC
        LIMIT 1
    """
    return execute_query_df(query, params)


def get_jobs_by_work_mode(country=None, source_dataset=None):
    """Job count grouped by work mode (remote/onsite/hybrid)."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT COALESCE(j.work_mode, 'Unknown') AS work_mode, COUNT(*) AS job_count
        FROM jobs j
        {join_loc}
        {where}
        GROUP BY j.work_mode
        ORDER BY job_count DESC
    """
    return execute_query_df(query, params)


def get_salary_distribution(country=None, source_dataset=None):
    """All salary values for histogram plotting."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT s.avg_salary_usd
        FROM salaries s
        JOIN jobs j ON s.job_id = j.job_id
        {join_loc}
        {where}
        WHERE s.avg_salary_usd IS NOT NULL AND s.avg_salary_usd > 0
    """
    # Fix double WHERE
    query = query.replace("WHERE\n        WHERE", "WHERE").replace("WHERE s.avg_salary_usd", "AND s.avg_salary_usd" if (country or source_dataset) else "WHERE s.avg_salary_usd")
    return execute_query_df(query, params)


def get_jobs_by_experience(country=None, source_dataset=None):
    """Job count by experience level."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT el.level_name, COUNT(*) AS job_count
        FROM jobs j
        JOIN experience_levels el ON j.experience_level_id = el.level_id
        {join_loc}
        {where}
        GROUP BY el.level_name, el.min_years
        ORDER BY el.min_years
    """
    return execute_query_df(query, params)


# ===========================================================================
# Skill Intelligence Queries
# ===========================================================================

def get_top_skills(limit: int = 20, country=None, source_dataset=None):
    """Top N skills ranked by job count."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    params["limit"] = limit
    query = f"""
        SELECT sk.skill_name, sk.skill_category, sk.skill_domain,
               COUNT(DISTINCT js.job_id) AS job_count,
               ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary
        FROM skills sk
        JOIN job_skills js ON sk.skill_id = js.skill_id
        JOIN jobs j ON js.job_id = j.job_id
        LEFT JOIN salaries sal ON j.job_id = sal.job_id
        {join_loc}
        {where}
        GROUP BY sk.skill_name, sk.skill_category, sk.skill_domain
        ORDER BY job_count DESC
        LIMIT :limit
    """
    return execute_query_df(query, params)


def get_skills_by_category(country=None, source_dataset=None):
    """Skill counts grouped by category (for treemap)."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT sk.skill_category, sk.skill_name,
               COUNT(DISTINCT js.job_id) AS job_count
        FROM skills sk
        JOIN job_skills js ON sk.skill_id = js.skill_id
        JOIN jobs j ON js.job_id = j.job_id
        {join_loc}
        {where}
        GROUP BY sk.skill_category, sk.skill_name
        ORDER BY sk.skill_category, job_count DESC
    """
    return execute_query_df(query, params)


def get_skills_by_domain(country=None, source_dataset=None):
    """Skill counts grouped by domain for deeper taxonomy treemap."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT sk.skill_domain, sk.skill_category, sk.skill_name,
               COUNT(DISTINCT js.job_id) AS job_count
        FROM skills sk
        JOIN job_skills js ON sk.skill_id = js.skill_id
        JOIN jobs j ON js.job_id = j.job_id
        {join_loc}
        {where}
        WHERE sk.skill_domain IS NOT NULL
        GROUP BY sk.skill_domain, sk.skill_category, sk.skill_name
        ORDER BY sk.skill_domain, job_count DESC
    """
    # Fix double WHERE
    query = query.replace("WHERE\n        WHERE", "WHERE").replace("WHERE sk.skill_domain", "AND sk.skill_domain" if (country or source_dataset) else "WHERE sk.skill_domain")
    return execute_query_df(query, params)


def get_skill_cooccurrence(top_n: int = 15, country=None, source_dataset=None):
    """
    Get co-occurrence counts for top N skills.
    Returns pairs of skills and their co-occurrence count.
    """
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    params["top_n"] = top_n
    query = f"""
        WITH top_skills AS (
            SELECT sk.skill_id, sk.skill_name
            FROM skills sk
            JOIN job_skills js ON sk.skill_id = js.skill_id
            JOIN jobs j ON js.job_id = j.job_id
            {join_loc}
            {where}
            GROUP BY sk.skill_id, sk.skill_name
            ORDER BY COUNT(DISTINCT js.job_id) DESC
            LIMIT :top_n
        )
        SELECT ts1.skill_name AS skill_1,
               ts2.skill_name AS skill_2,
               COUNT(DISTINCT js1.job_id) AS co_occurrence
        FROM job_skills js1
        JOIN job_skills js2 ON js1.job_id = js2.job_id AND js1.skill_id < js2.skill_id
        JOIN top_skills ts1 ON js1.skill_id = ts1.skill_id
        JOIN top_skills ts2 ON js2.skill_id = ts2.skill_id
        GROUP BY ts1.skill_name, ts2.skill_name
        ORDER BY co_occurrence DESC
    """
    return execute_query_df(query, params)


def get_skill_vs_salary(limit: int = 20, country=None, source_dataset=None):
    """Skill demand count vs average salary (for scatter plot)."""
    return get_top_skills(limit=limit, country=country, source_dataset=source_dataset)


# ===========================================================================
# Salary Intelligence Queries
# ===========================================================================

def get_salary_by_skill(limit: int = 15, country=None, source_dataset=None):
    """Top paying skills by average salary."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    params["limit"] = limit
    # Only include skills with enough data points
    query = f"""
        SELECT sk.skill_name,
               ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary,
               COUNT(DISTINCT js.job_id) AS job_count
        FROM skills sk
        JOIN job_skills js ON sk.skill_id = js.skill_id
        JOIN jobs j ON js.job_id = j.job_id
        JOIN salaries sal ON j.job_id = sal.job_id
        {join_loc}
        {where}
        GROUP BY sk.skill_name
        HAVING COUNT(DISTINCT js.job_id) >= 5
        ORDER BY avg_salary DESC
        LIMIT :limit
    """
    return execute_query_df(query, params)


def get_salary_by_city(limit: int = 15, country=None, source_dataset=None):
    """Average salary by city."""
    params = {}
    conditions = []

    if country:
        conditions.append("l.country = :country")
        params["country"] = country
    if source_dataset:
        conditions.append("j.source_dataset = :source_dataset")
        params["source_dataset"] = source_dataset

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params["limit"] = limit

    query = f"""
        SELECT l.city, l.country,
               ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary,
               COUNT(*) AS job_count
        FROM jobs j
        JOIN locations l ON j.location_id = l.location_id
        JOIN salaries sal ON j.job_id = sal.job_id
        {where}
        GROUP BY l.city, l.country
        HAVING COUNT(*) >= 3
        ORDER BY avg_salary DESC
        LIMIT :limit
    """
    return execute_query_df(query, params)


def get_salary_by_experience(country=None, source_dataset=None):
    """Salary distribution by experience level (for box plot)."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT el.level_name, sal.avg_salary_usd, el.min_years
        FROM jobs j
        JOIN experience_levels el ON j.experience_level_id = el.level_id
        JOIN salaries sal ON j.job_id = sal.job_id
        {join_loc}
        {where}
        ORDER BY el.min_years
    """
    return execute_query_df(query, params)


def get_salary_by_work_mode(country=None, source_dataset=None):
    """Average salary by work mode."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT COALESCE(j.work_mode, 'Unknown') AS work_mode,
               ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary,
               COUNT(*) AS job_count
        FROM jobs j
        JOIN salaries sal ON j.job_id = sal.job_id
        {join_loc}
        {where}
        GROUP BY j.work_mode
        ORDER BY avg_salary DESC
    """
    return execute_query_df(query, params)


# ===========================================================================
# Location Intelligence Queries
# ===========================================================================

def get_top_hiring_cities(limit: int = 15, country=None, source_dataset=None):
    """Top hiring cities by job count."""
    params = {}
    conditions = []

    if country:
        conditions.append("l.country = :country")
        params["country"] = country
    if source_dataset:
        conditions.append("j.source_dataset = :source_dataset")
        params["source_dataset"] = source_dataset

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params["limit"] = limit

    query = f"""
        SELECT l.city, l.country,
               COUNT(*) AS job_count,
               ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary
        FROM jobs j
        JOIN locations l ON j.location_id = l.location_id
        LEFT JOIN salaries sal ON j.job_id = sal.job_id
        {where}
        GROUP BY l.city, l.country
        ORDER BY job_count DESC
        LIMIT :limit
    """
    return execute_query_df(query, params)


def get_work_mode_distribution(country=None, source_dataset=None):
    """Remote vs onsite vs hybrid breakdown."""
    return get_jobs_by_work_mode(country=country, source_dataset=source_dataset)


def get_top_skills_per_city(cities: list = None, limit_skills: int = 5, country=None, source_dataset=None):
    """Top skills for specified cities."""
    params = {}
    conditions = []

    if country:
        conditions.append("l.country = :country")
        params["country"] = country
    if source_dataset:
        conditions.append("j.source_dataset = :source_dataset")
        params["source_dataset"] = source_dataset

    where_extra = " AND ".join(conditions)
    if where_extra:
        where_extra = "AND " + where_extra

    # Default to top 5 cities
    city_subquery = ""
    if cities:
        city_list = ", ".join(f"'{c}'" for c in cities)
        city_subquery = f"AND l.city IN ({city_list})"
    else:
        city_subquery = """
            AND l.city IN (
                SELECT l2.city FROM jobs j2
                JOIN locations l2 ON j2.location_id = l2.location_id
                GROUP BY l2.city ORDER BY COUNT(*) DESC LIMIT 5
            )
        """

    params["limit_skills"] = limit_skills
    query = f"""
        SELECT l.city, sk.skill_name, COUNT(DISTINCT js.job_id) AS job_count
        FROM jobs j
        JOIN locations l ON j.location_id = l.location_id
        JOIN job_skills js ON j.job_id = js.job_id
        JOIN skills sk ON js.skill_id = sk.skill_id
        LEFT JOIN salaries sal ON j.job_id = sal.job_id
        WHERE 1=1 {city_subquery} {where_extra}
        GROUP BY l.city, sk.skill_name
        ORDER BY l.city, job_count DESC
    """
    return execute_query_df(query, params)


# ===========================================================================
# Experience Intelligence Queries
# ===========================================================================

def get_experience_distribution(country=None, source_dataset=None):
    """Jobs by experience level."""
    return get_jobs_by_experience(country=country, source_dataset=source_dataset)


def get_salary_by_experience_level(country=None, source_dataset=None):
    """Salary box plot data by experience level."""
    return get_salary_by_experience(country=country, source_dataset=source_dataset)


def get_skills_by_experience(limit_skills: int = 10, country=None, source_dataset=None):
    """Top skills for each experience level."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    params["limit_skills"] = limit_skills
    query = f"""
        WITH ranked_skills AS (
            SELECT el.level_name, sk.skill_name,
                   COUNT(DISTINCT js.job_id) AS job_count,
                   el.min_years,
                   ROW_NUMBER() OVER (PARTITION BY el.level_name ORDER BY COUNT(DISTINCT js.job_id) DESC) AS rn
            FROM jobs j
            JOIN experience_levels el ON j.experience_level_id = el.level_id
            JOIN job_skills js ON j.job_id = js.job_id
            JOIN skills sk ON js.skill_id = sk.skill_id
            {join_loc}
            {where}
            GROUP BY el.level_name, sk.skill_name, el.min_years
        )
        SELECT level_name, skill_name, job_count, min_years
        FROM ranked_skills
        WHERE rn <= :limit_skills
        ORDER BY min_years, job_count DESC
    """
    return execute_query_df(query, params)


def get_work_mode_by_experience(country=None, source_dataset=None):
    """Work mode breakdown for each experience level."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    query = f"""
        SELECT el.level_name, COALESCE(j.work_mode, 'Unknown') AS work_mode,
               COUNT(*) AS job_count, el.min_years
        FROM jobs j
        JOIN experience_levels el ON j.experience_level_id = el.level_id
        {join_loc}
        {where}
        GROUP BY el.level_name, j.work_mode, el.min_years
        ORDER BY el.min_years, job_count DESC
    """
    return execute_query_df(query, params)


# ===========================================================================
# Technology Trend Queries
# ===========================================================================

def get_technology_comparison(skills_list: list, country=None, source_dataset=None):
    """Compare specific technologies by job count and salary."""
    where, params = _build_filters(country, source_dataset)
    join_loc = "JOIN locations l ON j.location_id = l.location_id" if country else ""
    skill_placeholders = ", ".join(f"'{s}'" for s in skills_list)

    query = f"""
        SELECT sk.skill_name, sk.skill_category,
               COUNT(DISTINCT js.job_id) AS job_count,
               ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary
        FROM skills sk
        JOIN job_skills js ON sk.skill_id = js.skill_id
        JOIN jobs j ON js.job_id = j.job_id
        LEFT JOIN salaries sal ON j.job_id = sal.job_id
        {join_loc}
        WHERE LOWER(sk.skill_name) IN ({skill_placeholders.lower()})
        {"AND " + " AND ".join([c.replace("WHERE ", "") for c in [where] if c]) if where else ""}
        GROUP BY sk.skill_name, sk.skill_category
        ORDER BY job_count DESC
    """
    return execute_query_df(query, params)


def get_skills_by_category_summary(country=None, source_dataset=None):
    """Skill category summary for sunburst/treemap."""
    return get_skills_by_category(country=country, source_dataset=source_dataset)


# ===========================================================================
# Career Advisor Queries
# ===========================================================================

def get_all_skills_list():
    """Get all skills for the career advisor multi-select."""
    query = """
        SELECT sk.skill_name, sk.skill_category,
               COUNT(DISTINCT js.job_id) AS job_count
        FROM skills sk
        JOIN job_skills js ON sk.skill_id = js.skill_id
        GROUP BY sk.skill_name, sk.skill_category
        ORDER BY job_count DESC
    """
    return execute_query_df(query)


def get_top_skills_for_level(level_name: str, limit: int = 20):
    """Top demanded skills for a specific experience level."""
    query = """
        SELECT sk.skill_name, sk.skill_category,
               COUNT(DISTINCT js.job_id) AS job_count,
               ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary
        FROM skills sk
        JOIN job_skills js ON sk.skill_id = js.skill_id
        JOIN jobs j ON js.job_id = j.job_id
        JOIN experience_levels el ON j.experience_level_id = el.level_id
        LEFT JOIN salaries sal ON j.job_id = sal.job_id
        WHERE el.level_name = :level_name
        GROUP BY sk.skill_name, sk.skill_category
        ORDER BY job_count DESC
        LIMIT :limit
    """
    return execute_query_df(query, {"level_name": level_name, "limit": limit})


def get_matching_roles(skill_names: list, limit: int = 10):
    """Find job titles that best match a set of skills."""
    if not skill_names:
        return execute_query_df("SELECT 1 WHERE false")

    skill_list = ", ".join(f"'{s.lower()}'" for s in skill_names)
    query = f"""
        SELECT j.job_title, COUNT(DISTINCT js.skill_id) AS matching_skills,
               ROUND(AVG(sal.avg_salary_usd)::numeric, 2) AS avg_salary,
               COUNT(DISTINCT j.job_id) AS job_count
        FROM jobs j
        JOIN job_skills js ON j.job_id = js.job_id
        JOIN skills sk ON js.skill_id = sk.skill_id
        LEFT JOIN salaries sal ON j.job_id = sal.job_id
        WHERE LOWER(sk.skill_name) IN ({skill_list})
        GROUP BY j.job_title
        ORDER BY matching_skills DESC, job_count DESC
        LIMIT :limit
    """
    return execute_query_df(query, {"limit": limit})


# ===========================================================================
# Utility Queries
# ===========================================================================

def get_unique_countries():
    """Get list of all countries for the filter dropdown."""
    query = """
        SELECT DISTINCT l.country
        FROM locations l
        JOIN jobs j ON l.location_id = j.location_id
        ORDER BY l.country
    """
    return execute_query_df(query)


def get_source_datasets():
    """Get list of all source datasets for the filter dropdown."""
    query = """
        SELECT DISTINCT source_dataset
        FROM jobs
        ORDER BY source_dataset
    """
    return execute_query_df(query)
