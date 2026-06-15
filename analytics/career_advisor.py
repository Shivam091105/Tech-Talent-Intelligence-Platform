"""
Career Advisor — rule-based skill gap analysis.

No ML here — just compares user's skills against market demand data
and provides actionable recommendations.
"""

import pandas as pd
from database import queries
from config.logging_config import setup_logger

logger = setup_logger("analytics.career_advisor")


def analyze_skill_gap(
    user_skills: list,
    experience_level: str = "Entry",
    limit: int = 20,
) -> dict:
    """
    Perform a rule-based skill gap analysis.

    Args:
        user_skills: List of skill names the user currently has.
        experience_level: User's experience level (Entry/Mid/Senior/Lead).
        limit: Number of top market skills to compare against.

    Returns:
        dict with:
            - matching_skills: skills user has that are in demand
            - missing_skills: skills user lacks (ranked by demand)
            - match_percentage: % of top market skills the user has
            - market_skills: full market demand data
    """
    # Get top demanded skills for this experience level
    market_df = queries.get_top_skills_for_level(level_name=experience_level, limit=limit)

    if market_df.empty:
        return {
            "matching_skills": [],
            "missing_skills": [],
            "match_percentage": 0,
            "market_skills": market_df,
        }

    market_skill_names = set(market_df["skill_name"].str.lower().tolist())
    user_skill_names = set(s.lower() for s in user_skills)

    # Find matches and gaps
    matching = market_skill_names & user_skill_names
    missing = market_skill_names - user_skill_names

    # Build detailed results with demand data
    matching_details = market_df[market_df["skill_name"].str.lower().isin(matching)].to_dict("records")
    missing_details = market_df[market_df["skill_name"].str.lower().isin(missing)].to_dict("records")

    # Sort missing by job_count descending (highest demand first)
    missing_details = sorted(missing_details, key=lambda x: x.get("job_count", 0), reverse=True)

    match_pct = (len(matching) / len(market_skill_names) * 100) if market_skill_names else 0

    logger.info(
        "Skill gap analysis: %d matching, %d missing (%.0f%% match)",
        len(matching), len(missing), match_pct,
    )

    return {
        "matching_skills": matching_details,
        "missing_skills": missing_details,
        "match_percentage": round(match_pct, 1),
        "market_skills": market_df,
    }


def find_matching_roles(user_skills: list, limit: int = 10) -> pd.DataFrame:
    """Find job roles that best match the user's skill set."""
    return queries.get_matching_roles(skill_names=user_skills, limit=limit)


def get_all_skills() -> pd.DataFrame:
    """Get all available skills for the user selection widget."""
    return queries.get_all_skills_list()
