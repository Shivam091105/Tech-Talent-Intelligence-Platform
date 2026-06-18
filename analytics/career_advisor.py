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

    Matching skills are taken from the top-N market skills for the given
    experience level (unchanged from before).

    Recommended skills to learn are driven by co-occurrence: skills that
    actually appear alongside the user's skills in real job postings at
    that experience level — ranked by how often they co-occur and then
    by overall market demand. This means a Python user sees pandas/SQL/
    scikit-learn, not a random list of unrelated top skills.

    Args:
        user_skills: List of skill names the user currently has.
        experience_level: User's experience level (Entry/Mid/Senior/Lead).
        limit: Number of top market skills to compare against for the
               match score; also the cap on recommended skills returned.

    Returns:
        dict with:
            - matching_skills: skills user has that are in top market demand
            - missing_skills: contextually recommended skills to learn
            - match_percentage: % of top market skills the user already has
            - market_skills: full market demand data for the level
    """
    # ------------------------------------------------------------------ #
    # 1. Market benchmark — used for "Skills You Have" + match %          #
    # ------------------------------------------------------------------ #
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

    matching = market_skill_names & user_skill_names
    match_pct = (len(matching) / len(market_skill_names) * 100) if market_skill_names else 0

    matching_details = (
        market_df[market_df["skill_name"].str.lower().isin(matching)]
        .to_dict("records")
    )

    # ------------------------------------------------------------------ #
    # 2. Contextual recommendations — co-occurring skills                  #
    # ------------------------------------------------------------------ #
    # Ask the DB: "given these jobs that need the user's skills at this
    # level, which OTHER skills appear most frequently?"
    co_df = queries.get_co_occurring_skills(
        skill_names=user_skills,
        level_name=experience_level,
        limit=limit,
    )

    if not co_df.empty:
        # co_df already excludes the user's own skills and is ordered by
        # co_occurrence_count DESC, job_count DESC from the query.
        # Cap to 10 so "Skills to learn" count in the table matches what
        # is actually displayed in the UI — no more misleading "20".
        missing_details = co_df.head(10).to_dict("records")
    else:
        # Fallback: user's skills appear in no jobs at this level, or DB
        # is empty — fall back to the old "top market minus user" list.
        missing = market_skill_names - user_skill_names
        missing_details = (
            market_df[market_df["skill_name"].str.lower().isin(missing)]
            .sort_values("job_count", ascending=False)
            .head(10)
            .to_dict("records")
        )

    logger.info(
        "Skill gap analysis: %d matching, %d recommended (%.0f%% match) — "
        "recommendation source: %s",
        len(matching_details),
        len(missing_details),
        match_pct,
        "co-occurrence" if not co_df.empty else "market-fallback",
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