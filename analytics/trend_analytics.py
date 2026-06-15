"""
Trend Analytics — technology comparison and trend tracking.
"""

import pandas as pd
from database import queries
from config.logging_config import setup_logger

logger = setup_logger("analytics.trends")

# Default technologies to compare
DEFAULT_TECHNOLOGIES = [
    "python", "java", "javascript", "react", "angular",
    "aws", "docker", "kubernetes", "sql", "node.js",
    "typescript", "go", "spring", "django", "tensorflow",
]


def compare_technologies(skills_list: list = None, country=None, source_dataset=None) -> pd.DataFrame:
    """Compare specific technologies by demand and salary."""
    if skills_list is None:
        skills_list = DEFAULT_TECHNOLOGIES
    return queries.get_technology_comparison(
        skills_list=skills_list, country=country, source_dataset=source_dataset
    )


def get_category_breakdown(country=None, source_dataset=None) -> pd.DataFrame:
    """Get skills grouped by category for sunburst/treemap."""
    return queries.get_skills_by_category_summary(country=country, source_dataset=source_dataset)


def get_skill_ranking(limit: int = 30, country=None, source_dataset=None) -> pd.DataFrame:
    """Get comprehensive skill ranking by demand."""
    return queries.get_top_skills(limit=limit, country=country, source_dataset=source_dataset)
