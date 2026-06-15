"""
Pydantic data validation models for ETL pipeline.
Validates each record before inserting into PostgreSQL.
"""

from typing import Optional, List
from pydantic import BaseModel, field_validator


class JobRecord(BaseModel):
    """Validated job record ready for database insertion."""

    job_title: str
    company_name: Optional[str] = "Unknown"
    company_type: Optional[str] = None
    company_rating: Optional[float] = None
    city: str = "Unknown"
    state: Optional[str] = None
    country: str = "Unknown"
    experience_level: str = "Entry"
    work_mode: Optional[str] = None
    employment_type: Optional[str] = None
    avg_salary_usd: Optional[float] = None
    min_salary_usd: Optional[float] = None
    max_salary_usd: Optional[float] = None
    extracted_skills: List[str] = []
    posted_date: Optional[str] = None
    source_dataset: str

    @field_validator("job_title")
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("job_title cannot be empty")
        return v.strip()[:255]

    @field_validator("company_name")
    @classmethod
    def clean_company(cls, v):
        if not v or str(v).strip() in ("", "nan", "None"):
            return "Unknown"
        return str(v).strip()[:255]

    @field_validator("experience_level")
    @classmethod
    def valid_level(cls, v):
        valid = {"Entry", "Mid", "Senior", "Lead"}
        return v if v in valid else "Entry"

    @field_validator("work_mode")
    @classmethod
    def valid_work_mode(cls, v):
        if v is None:
            return None
        valid = {"remote", "onsite", "hybrid"}
        return v.lower() if v.lower() in valid else None

    @field_validator("avg_salary_usd")
    @classmethod
    def salary_range(cls, v):
        if v is not None and (v < 0 or v > 500000):
            return None
        return v

    @field_validator("company_rating")
    @classmethod
    def rating_range(cls, v):
        if v is not None and (v < 0 or v > 5.0):
            return None
        return v


def validate_records(df) -> list:
    """
    Validate each row in the DataFrame using the JobRecord model.

    Returns:
        List of validated JobRecord instances. Invalid records are logged and skipped.
    """
    import pandas as pd
    from config.logging_config import setup_logger

    logger = setup_logger("etl.validators")

    valid_records = []
    error_count = 0

    for idx, row in df.iterrows():
        try:
            record = JobRecord(
                job_title=row.get("job_title"),
                company_name=row.get("company_name"),
                company_type=row.get("company_type"),
                company_rating=row.get("company_rating") if pd.notna(row.get("company_rating")) else None,
                city=row.get("city", "Unknown"),
                state=row.get("state") if pd.notna(row.get("state")) else None,
                country=row.get("country", "Unknown"),
                experience_level=row.get("experience_level", "Entry"),
                work_mode=row.get("work_mode") if pd.notna(row.get("work_mode")) else None,
                employment_type=row.get("employment_type") if pd.notna(row.get("employment_type")) else None,
                avg_salary_usd=row.get("avg_salary_usd") if pd.notna(row.get("avg_salary_usd")) else None,
                extracted_skills=row.get("extracted_skills", []),
                posted_date=str(row.get("posted_date")) if pd.notna(row.get("posted_date")) else None,
                source_dataset=row.get("source_dataset", "unknown"),
            )
            valid_records.append(record)
        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Only log first 5 errors
                logger.warning("Validation error at row %d: %s", idx, e)

    logger.info("Validation: %d valid, %d errors (out of %d)", len(valid_records), error_count, len(df))
    return valid_records
