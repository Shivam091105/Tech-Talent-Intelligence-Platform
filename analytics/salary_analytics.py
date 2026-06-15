"""
Salary Analytics — business logic for salary intelligence.
"""

import pandas as pd
from database import queries
from config.logging_config import setup_logger

logger = setup_logger("analytics.salary")


def get_salary_distribution(country=None, source_dataset=None) -> pd.DataFrame:
    """Get all salary values for histogram plotting."""
    return queries.get_salary_distribution(country=country, source_dataset=source_dataset)


def get_top_paying_skills(limit: int = 15, country=None, source_dataset=None) -> pd.DataFrame:
    """Get highest-paying skills by average salary."""
    return queries.get_salary_by_skill(limit=limit, country=country, source_dataset=source_dataset)


def get_salary_by_city(limit: int = 15, country=None, source_dataset=None) -> pd.DataFrame:
    """Get average salary by city."""
    return queries.get_salary_by_city(limit=limit, country=country, source_dataset=source_dataset)


def get_salary_by_experience(country=None, source_dataset=None) -> pd.DataFrame:
    """Get salary distribution per experience level for box plots."""
    return queries.get_salary_by_experience(country=country, source_dataset=source_dataset)


def get_salary_by_work_mode(country=None, source_dataset=None) -> pd.DataFrame:
    """Get average salary by work mode (remote/onsite/hybrid)."""
    return queries.get_salary_by_work_mode(country=country, source_dataset=source_dataset)
