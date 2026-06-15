"""
Location Analytics — business logic for geographic hiring insights.
"""

import pandas as pd
from database import queries
from config.logging_config import setup_logger

logger = setup_logger("analytics.location")


def get_top_hiring_cities(limit: int = 15, country=None, source_dataset=None) -> pd.DataFrame:
    """Get cities with the most job postings."""
    return queries.get_top_hiring_cities(limit=limit, country=country, source_dataset=source_dataset)


def get_work_mode_distribution(country=None, source_dataset=None) -> pd.DataFrame:
    """Get remote vs onsite vs hybrid breakdown."""
    return queries.get_work_mode_distribution(country=country, source_dataset=source_dataset)


def get_top_skills_per_city(cities=None, limit_skills: int = 5, country=None, source_dataset=None) -> pd.DataFrame:
    """Get top demanded skills for each city."""
    return queries.get_top_skills_per_city(
        cities=cities, limit_skills=limit_skills,
        country=country, source_dataset=source_dataset
    )
