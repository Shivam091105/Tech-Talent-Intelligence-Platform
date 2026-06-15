"""
Data Transformer — cleans, normalizes, and enriches the raw extracted data.

Responsibilities:
    1. Clean: remove nulls, duplicates, fix types
    2. Normalize salaries to USD annual
    3. Extract skills from text using dictionary + regex
    4. Standardize locations using alias mapping
    5. Categorize experience levels
"""

import re
import json
import numpy as np
import pandas as pd
from pathlib import Path

from config.settings import EXCHANGE_RATES, EXPERIENCE_LEVELS, DICTIONARIES_DIR
from config.logging_config import setup_logger

logger = setup_logger("etl.transformer")


# ===========================================================================
# Load dictionaries
# ===========================================================================

def _load_skills_dictionary() -> dict:
    """Load skills dictionary from JSON file."""
    path = DICTIONARIES_DIR / "skills_dictionary.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_location_mapping() -> dict:
    """Load location mapping from JSON file."""
    path = DICTIONARIES_DIR / "location_mapping.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ===========================================================================
# Step 1: Data Cleaning
# ===========================================================================

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw DataFrame:
    - Drop rows without job_title
    - Remove exact duplicate rows
    - Strip whitespace from string columns
    - Standardize empty strings to NaN
    """
    initial_count = len(df)

    # Drop rows where job_title is missing (unusable records)
    df = df.dropna(subset=["job_title"])

    # Strip whitespace from all string columns
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(["", "nan", "None", "N/A", "n/a", "NA"], np.nan)

    # Remove exact duplicates
    df = df.drop_duplicates(subset=["job_title", "company_name", "location"], keep="first")

    removed = initial_count - len(df)
    logger.info("Cleaning: %d rows → %d rows (%d removed)", initial_count, len(df), removed)
    return df.reset_index(drop=True)


# ===========================================================================
# Step 2: Salary Normalization
# ===========================================================================

def _parse_salary_value(raw_val) -> float:
    """
    Parse a salary value from various formats:
    - "50000" → 50000.0
    - "$50K-$80K" → 65000.0 (midpoint)
    - "5.5" (LPA) → 5.5
    - "50,000 - 80,000" → 65000.0
    """
    if pd.isna(raw_val):
        return np.nan

    raw_str = str(raw_val).strip()

    # Remove currency symbols and commas
    raw_str = re.sub(r"[$₹€£,]", "", raw_str)

    # Handle "K" suffix (e.g., "50K" → 50000)
    raw_str = re.sub(r"(\d+\.?\d*)\s*[kK]", lambda m: str(float(m.group(1)) * 1000), raw_str)

    # Handle ranges: take midpoint
    range_match = re.search(r"(\d+\.?\d*)\s*[-–to]+\s*(\d+\.?\d*)", raw_str)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        return (low + high) / 2

    # Try direct float conversion
    number_match = re.search(r"(\d+\.?\d*)", raw_str)
    if number_match:
        return float(number_match.group(1))

    return np.nan


def normalize_salaries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize salary values to USD annual:
    - Parse raw salary strings
    - Convert INR (LPA) to USD annual
    - Convert other currencies using fixed exchange rates
    """
    df = df.copy()

    # Parse raw salary values
    df["salary_parsed"] = df["salary_raw"].apply(_parse_salary_value)

    # Convert to USD annual
    def _to_usd_annual(row):
        val = row["salary_parsed"]
        currency = str(row.get("salary_currency", "USD")).upper()

        if pd.isna(val):
            return np.nan

        # Indian salaries are often in LPA (Lakhs Per Annum)
        if currency == "INR":
            if val < 200:  # Likely in LPA (e.g., 5.5 = 5.5 LPA)
                val = val * 100000  # Convert to INR annual
            # Convert INR to USD
            return round(val / EXCHANGE_RATES.get("INR", 83.0), 2)

        # Other currencies
        rate = EXCHANGE_RATES.get(currency, 1.0)
        usd_val = val / rate if rate != 1.0 else val

        # If value seems like monthly salary (< 10000 USD), annualize
        if usd_val < 10000:
            usd_val *= 12

        return round(usd_val, 2)

    df["avg_salary_usd"] = df.apply(_to_usd_annual, axis=1)

    # Basic sanity: remove extreme outliers
    df.loc[df["avg_salary_usd"] > 500000, "avg_salary_usd"] = np.nan
    df.loc[df["avg_salary_usd"] < 1000, "avg_salary_usd"] = np.nan

    valid_salaries = df["avg_salary_usd"].notna().sum()
    logger.info("Salary normalization: %d valid salary values (out of %d)", valid_salaries, len(df))

    return df


# ===========================================================================
# Step 3: Skill Extraction
# ===========================================================================

def extract_skills(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract skills from the skills_text column using dictionary + regex matching.
    Adds a 'extracted_skills' column with a list of matched skill names.
    """
    skills_dict = _load_skills_dictionary()
    df = df.copy()

    # Build regex patterns for each skill + aliases
    skill_patterns = {}
    for skill_name, info in skills_dict.items():
        all_terms = [re.escape(skill_name)] + [re.escape(a) for a in info.get("aliases", [])]
        # Match as whole words (case-insensitive)
        pattern = re.compile(r"\b(" + "|".join(all_terms) + r")\b", re.IGNORECASE)
        skill_patterns[skill_name] = pattern

    def _match_skills(text):
        if pd.isna(text) or str(text).strip() == "":
            return []
        text = str(text)
        found = []
        for skill_name, pattern in skill_patterns.items():
            if pattern.search(text):
                found.append(skill_name)
        return found

    df["extracted_skills"] = df["skills_text"].apply(_match_skills)

    total_skills = df["extracted_skills"].apply(len).sum()
    avg_skills = df["extracted_skills"].apply(len).mean()
    logger.info("Skill extraction: %d total skill matches (avg %.1f per job)", total_skills, avg_skills)

    return df


# ===========================================================================
# Step 4: Location Standardization
# ===========================================================================

def standardize_locations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize location values using the location mapping dictionary.
    Produces 'city', 'state', and 'country' columns.
    """
    loc_mapping = _load_location_mapping()
    city_aliases = loc_mapping.get("city_aliases", {})
    city_to_country = loc_mapping.get("city_to_country", {})

    df = df.copy()

    def _standardize(raw_location):
        if pd.isna(raw_location):
            return ("Unknown", None, "Unknown")

        raw = str(raw_location).strip()

        # Check for "Remote" keyword
        if re.search(r"\bremote\b", raw, re.IGNORECASE):
            return ("Remote", None, "Global")

        # Try alias lookup (lowercase)
        raw_lower = raw.lower()
        if raw_lower in city_aliases:
            canonical_city = city_aliases[raw_lower]
        else:
            # Try to extract city name — take first part before comma
            parts = [p.strip() for p in raw.split(",")]
            canonical_city = parts[0].title()

            # Check alias for just the city part
            if canonical_city.lower() in city_aliases:
                canonical_city = city_aliases[canonical_city.lower()]

        # Look up country
        country = city_to_country.get(canonical_city, "Unknown")

        # Try to extract state from comma-separated parts
        state = None
        parts = [p.strip() for p in raw.split(",")]
        if len(parts) >= 2:
            state = parts[1].strip()

        return (canonical_city, state, country)

    location_data = df["location"].apply(_standardize)
    df["city"] = location_data.apply(lambda x: x[0])
    df["state"] = location_data.apply(lambda x: x[1])
    df["country"] = location_data.apply(lambda x: x[2])

    unique_cities = df["city"].nunique()
    unique_countries = df["country"].nunique()
    logger.info("Location standardization: %d unique cities, %d unique countries", unique_cities, unique_countries)

    return df


# ===========================================================================
# Step 5: Experience Categorization
# ===========================================================================

def categorize_experience(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize experience text into levels: Entry, Mid, Senior, Lead.
    """
    df = df.copy()

    def _categorize(exp_text):
        if pd.isna(exp_text):
            return "Entry"  # Default for missing values

        text = str(exp_text).strip().lower()

        # Direct level name matching
        if any(w in text for w in ["entry", "junior", "fresher", "intern", "graduate", "trainee"]):
            return "Entry"
        if any(w in text for w in ["lead", "principal", "director", "head", "vp", "chief", "executive"]):
            return "Lead"
        if any(w in text for w in ["senior", "sr.", "sr ", "staff", "expert"]):
            return "Senior"
        if any(w in text for w in ["mid", "intermediate", "associate", "regular"]):
            return "Mid"

        # Try to extract years
        year_match = re.search(r"(\d+)", text)
        if year_match:
            years = int(year_match.group(1))
            for level_name, (min_yr, max_yr) in EXPERIENCE_LEVELS.items():
                if min_yr <= years <= max_yr:
                    return level_name

        # If starts with "EN" or "MI" or "SE" style codes
        if text.startswith("en"):
            return "Entry"
        if text.startswith("mi"):
            return "Mid"
        if text.startswith("se"):
            return "Senior"
        if text.startswith("ex"):
            return "Lead"

        return "Entry"  # Default

    df["experience_level"] = df["experience_text"].apply(_categorize)

    # Standardize work_mode
    def _standardize_work_mode(val):
        if pd.isna(val):
            return None
        text = str(val).strip().lower()

        if any(w in text for w in ["remote", "100", "fully remote", "work from home", "wfh"]):
            return "remote"
        if any(w in text for w in ["hybrid", "partial", "flexible"]):
            return "hybrid"
        if any(w in text for w in ["onsite", "on-site", "office", "in-office", "0"]):
            return "onsite"

        # Handle remote_ratio numbers
        try:
            ratio = float(val)
            if ratio >= 80:
                return "remote"
            elif ratio >= 20:
                return "hybrid"
            else:
                return "onsite"
        except (ValueError, TypeError):
            pass

        return None

    df["work_mode"] = df["work_mode"].apply(_standardize_work_mode)

    logger.info("Experience categorization: %s", df["experience_level"].value_counts().to_dict())

    return df


# ===========================================================================
# Full Transform Pipeline
# ===========================================================================

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full transformation pipeline:
    clean → normalize salaries → extract skills → standardize locations → categorize experience
    """
    logger.info("=" * 60)
    logger.info("Starting transformation pipeline (%d rows)", len(df))
    logger.info("=" * 60)

    df = clean_data(df)
    df = normalize_salaries(df)
    df = extract_skills(df)
    df = standardize_locations(df)
    df = categorize_experience(df)

    logger.info("=" * 60)
    logger.info("Transformation complete: %d rows", len(df))
    logger.info("=" * 60)

    return df
