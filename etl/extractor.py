"""
CSV Extractor — reads multiple Kaggle datasets and harmonizes them into
a single DataFrame with a unified schema.

Supported datasets:
    1. India Tech Jobs 2024-26
    2. Global AI Job Market 2025
    3. Software Engineer Jobs & Salaries 2024
"""

import pandas as pd
from pathlib import Path

from config.settings import RAW_DATA_DIR
from config.logging_config import setup_logger

logger = setup_logger("etl.extractor")


# ---------------------------------------------------------------------------
# Column mapping per dataset → unified schema
# ---------------------------------------------------------------------------
# Each dataset has different column names; we map them to a common schema.

UNIFIED_COLUMNS = [
    "job_title", "company_name", "company_type", "company_rating",
    "location", "experience_text", "work_mode", "employment_type",
    "skills_text", "salary_raw", "salary_currency", "posted_date",
    "source_dataset",
]


def _read_india_tech_jobs(file_path: Path) -> pd.DataFrame:
    """
    Read and map 'India Tech Jobs 2024-26' dataset.
    Expected columns vary — we handle common variants.
    """
    df = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")
    logger.info("Read India Tech Jobs: %d rows, columns: %s", len(df), list(df.columns))

    # Normalize column names to lowercase
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    mapped = pd.DataFrame()
    mapped["job_title"] = df.get("job_title", df.get("role", df.get("title", pd.Series(dtype=str))))
    mapped["company_name"] = df.get("company", df.get("company_name", pd.Series(dtype=str)))
    mapped["company_type"] = df.get("company_type", pd.Series(dtype=str))
    mapped["company_rating"] = df.get("rating", df.get("company_rating", pd.Series(dtype=float)))
    mapped["location"] = df.get("location", df.get("city", pd.Series(dtype=str)))
    mapped["experience_text"] = df.get("experience_level", df.get("experience", df.get("min_experience", pd.Series(dtype=str))))
    mapped["work_mode"] = df.get("work_mode", df.get("work_type", df.get("work_setting", pd.Series(dtype=str))))
    mapped["employment_type"] = df.get("employment_type", df.get("job_type", pd.Series(dtype=str)))
    mapped["skills_text"] = df.get("skills", df.get("required_skills", df.get("key_skills", pd.Series(dtype=str))))
    mapped["salary_raw"] = df.get("salary", df.get("salary_in_lpa", df.get("avg_salary", pd.Series(dtype=str))))
    mapped["salary_currency"] = "INR"
    mapped["posted_date"] = df.get("posted_date", df.get("date_posted", pd.Series(dtype=str)))
    mapped["source_dataset"] = "india_tech_jobs"

    return mapped


def _read_global_ai_jobs(file_path: Path) -> pd.DataFrame:
    """Read and map 'Global AI Job Market 2025' dataset."""
    df = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")
    logger.info("Read Global AI Jobs: %d rows, columns: %s", len(df), list(df.columns))

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    mapped = pd.DataFrame()
    mapped["job_title"] = df.get("job_title", df.get("title", pd.Series(dtype=str)))
    mapped["company_name"] = df.get("company_name", df.get("company", pd.Series(dtype=str)))
    mapped["company_type"] = df.get("company_type", df.get("company_size", pd.Series(dtype=str)))
    mapped["company_rating"] = df.get("rating", pd.Series(dtype=float))
    mapped["location"] = df.get("company_location", df.get("location", pd.Series(dtype=str)))
    mapped["experience_text"] = df.get("experience_level", df.get("experience", pd.Series(dtype=str)))
    mapped["work_mode"] = df.get("remote_ratio", df.get("work_setting", df.get("work_mode", pd.Series(dtype=str))))
    mapped["employment_type"] = df.get("employment_type", df.get("job_type", pd.Series(dtype=str)))
    mapped["skills_text"] = df.get("required_skills", df.get("skills", pd.Series(dtype=str)))
    mapped["salary_raw"] = df.get("salary_in_usd", df.get("salary_usd", df.get("salary", pd.Series(dtype=str))))
    mapped["salary_currency"] = "USD"
    mapped["posted_date"] = df.get("posted_date", df.get("work_year", pd.Series(dtype=str)))
    mapped["source_dataset"] = "global_ai_jobs"

    return mapped


def _read_se_salaries(file_path: Path) -> pd.DataFrame:
    """Read and map 'Software Engineer Jobs & Salaries 2024' dataset."""
    df = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")
    logger.info("Read SE Salaries: %d rows, columns: %s", len(df), list(df.columns))

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    mapped = pd.DataFrame()
    mapped["job_title"] = df.get("job_title", df.get("title", pd.Series(dtype=str)))
    mapped["company_name"] = df.get("company_name", df.get("company", pd.Series(dtype=str)))
    mapped["company_type"] = df.get("company_type", pd.Series(dtype=str))
    mapped["company_rating"] = df.get("rating", df.get("company_rating", pd.Series(dtype=float)))
    mapped["location"] = df.get("location", df.get("job_location", pd.Series(dtype=str)))
    mapped["experience_text"] = df.get("experience_level", df.get("experience", pd.Series(dtype=str)))
    mapped["work_mode"] = df.get("work_mode", df.get("remote", pd.Series(dtype=str)))
    mapped["employment_type"] = df.get("employment_type", df.get("job_type", pd.Series(dtype=str)))
    mapped["skills_text"] = df.get("skills", df.get("required_skills", df.get("job_description", pd.Series(dtype=str))))
    mapped["salary_raw"] = df.get("salary_estimate", df.get("avg_salary", df.get("salary", pd.Series(dtype=str))))
    mapped["salary_currency"] = "USD"
    mapped["posted_date"] = df.get("posted_date", df.get("date_posted", pd.Series(dtype=str)))
    mapped["source_dataset"] = "se_salaries"

    return mapped


# ---------------------------------------------------------------------------
# Dataset auto-detection and mapping
# ---------------------------------------------------------------------------

# Map partial filename matches to reader functions
DATASET_READERS = {
    "india": _read_india_tech_jobs,
    "global": _read_global_ai_jobs,
    "ai_job": _read_global_ai_jobs,
    "software": _read_se_salaries,
    "salary": _read_se_salaries,
    "glassdoor": _read_se_salaries,
}


def _detect_reader(filename: str):
    """Auto-detect which reader function to use based on filename."""
    fname = filename.lower()
    for keyword, reader in DATASET_READERS.items():
        if keyword in fname:
            return reader
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_all(data_dir: Path = None) -> pd.DataFrame:
    """
    Read all CSV files from the raw data directory, harmonize schemas,
    and return a single concatenated DataFrame.

    Args:
        data_dir: Path to directory containing CSV files. Defaults to data/raw/.

    Returns:
        pd.DataFrame with unified column schema.
    """
    data_dir = data_dir or RAW_DATA_DIR

    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        logger.error("No CSV files found in %s", data_dir)
        raise FileNotFoundError(f"No CSV files in {data_dir}. Download datasets first.")

    logger.info("Found %d CSV file(s) in %s", len(csv_files), data_dir)

    all_dfs = []
    for csv_path in csv_files:
        reader = _detect_reader(csv_path.name)
        if reader is None:
            logger.warning("Unknown dataset format: %s — skipping", csv_path.name)
            continue

        try:
            df = reader(csv_path)
            all_dfs.append(df)
            logger.info("  ✓ %s: %d rows extracted", csv_path.name, len(df))
        except Exception as e:
            logger.error("  ✗ Error reading %s: %s", csv_path.name, e)

    if not all_dfs:
        raise ValueError("No datasets could be read. Check file names and formats.")

    combined = pd.concat(all_dfs, ignore_index=True)
    logger.info("Combined dataset: %d total rows", len(combined))
    return combined
