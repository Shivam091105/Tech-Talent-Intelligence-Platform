"""
Skill Analytics — business logic for skill demand analysis.
"""

import pandas as pd
import numpy as np
from itertools import combinations

from database import queries
from config.logging_config import setup_logger

logger = setup_logger("analytics.skill")


def get_top_skills(limit: int = 20, country=None, source_dataset=None) -> pd.DataFrame:
    """Get top skills ranked by demand (job count)."""
    return queries.get_top_skills(limit=limit, country=country, source_dataset=source_dataset)


def get_skills_by_category(country=None, source_dataset=None) -> pd.DataFrame:
    """Get skill counts grouped by category for treemap visualization."""
    return queries.get_skills_by_category(country=country, source_dataset=source_dataset)


def get_skill_cooccurrence_matrix(top_n: int = 15, country=None, source_dataset=None) -> pd.DataFrame:
    """
    Build a co-occurrence matrix for the top N skills.
    Returns a square DataFrame suitable for heatmap plotting.
    """
    pairs_df = queries.get_skill_cooccurrence(top_n=top_n, country=country, source_dataset=source_dataset)

    if pairs_df.empty:
        return pd.DataFrame()

    # Get unique skills from the pairs
    all_skills = sorted(set(pairs_df["skill_1"].tolist() + pairs_df["skill_2"].tolist()))

    # Build symmetric matrix
    matrix = pd.DataFrame(0, index=all_skills, columns=all_skills)
    for _, row in pairs_df.iterrows():
        matrix.loc[row["skill_1"], row["skill_2"]] = row["co_occurrence"]
        matrix.loc[row["skill_2"], row["skill_1"]] = row["co_occurrence"]

    # Fill diagonal with self-count (optional: leave as 0)
    return matrix


def get_skill_demand_vs_salary(limit: int = 20, country=None, source_dataset=None) -> pd.DataFrame:
    """Get skill demand vs salary data for scatter plot."""
    return queries.get_skill_vs_salary(limit=limit, country=country, source_dataset=source_dataset)
