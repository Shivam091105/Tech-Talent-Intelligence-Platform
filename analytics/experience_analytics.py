"""
Experience Analytics — business logic for career-level analysis.
"""

import pandas as pd
from database import queries
from config.logging_config import setup_logger

logger = setup_logger("analytics.experience")


def get_experience_distribution(country=None, source_dataset=None) -> pd.DataFrame:
    """Get job count by experience level."""
    return queries.get_experience_distribution(country=country, source_dataset=source_dataset)


def get_salary_by_experience(country=None, source_dataset=None) -> pd.DataFrame:
    """Get salary data per experience level for box plots."""
    return queries.get_salary_by_experience_level(country=country, source_dataset=source_dataset)


def get_skills_by_experience(limit_skills: int = 10, country=None, source_dataset=None) -> pd.DataFrame:
    """Get top skills for each experience level."""
    return queries.get_skills_by_experience(
        limit_skills=limit_skills, country=country, source_dataset=source_dataset
    )


def get_work_mode_by_experience(country=None, source_dataset=None) -> pd.DataFrame:
    """Get work mode breakdown per experience level."""
    return queries.get_work_mode_by_experience(country=country, source_dataset=source_dataset)
