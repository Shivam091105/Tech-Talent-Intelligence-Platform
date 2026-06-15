"""
Unit tests for ETL transformer module.
Tests cleaning, salary normalization, and experience categorization.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
import numpy as np

from etl.transformer import (
    clean_data,
    normalize_salaries,
    categorize_experience,
    _parse_salary_value,
)


# ===========================================================================
# Test: Salary Parsing
# ===========================================================================

class TestSalaryParsing:
    def test_simple_number(self):
        assert _parse_salary_value("50000") == 50000.0

    def test_with_currency_symbol(self):
        assert _parse_salary_value("$50000") == 50000.0

    def test_with_commas(self):
        assert _parse_salary_value("50,000") == 50000.0

    def test_range_midpoint(self):
        assert _parse_salary_value("50000-80000") == 65000.0

    def test_range_with_k(self):
        result = _parse_salary_value("$50K-$80K")
        assert result == 65000.0

    def test_nan_input(self):
        assert np.isnan(_parse_salary_value(np.nan))

    def test_none_input(self):
        assert np.isnan(_parse_salary_value(None))

    def test_lpa_value(self):
        assert _parse_salary_value("5.5") == 5.5

    def test_empty_string(self):
        assert np.isnan(_parse_salary_value(""))


# ===========================================================================
# Test: Data Cleaning
# ===========================================================================

class TestCleaning:
    def _make_df(self, rows):
        return pd.DataFrame(rows, columns=[
            "job_title", "company_name", "location", "salary_raw", "skills_text",
        ])

    def test_removes_rows_without_title(self):
        df = self._make_df([
            ["Engineer", "Acme", "NYC", "100K", "Python"],
            [None, "Acme", "NYC", "100K", "Java"],
        ])
        result = clean_data(df)
        assert len(result) == 1

    def test_removes_duplicates(self):
        df = self._make_df([
            ["Engineer", "Acme", "NYC", "100K", "Python"],
            ["Engineer", "Acme", "NYC", "100K", "Python"],
        ])
        result = clean_data(df)
        assert len(result) == 1

    def test_strips_whitespace(self):
        df = self._make_df([
            ["  Engineer  ", "  Acme  ", "NYC", "100K", "Python"],
        ])
        result = clean_data(df)
        assert result.iloc[0]["job_title"] == "Engineer"


# ===========================================================================
# Test: Experience Categorization
# ===========================================================================

class TestExperienceCategorization:
    def _make_df(self, exp_values):
        return pd.DataFrame({"experience_text": exp_values, "work_mode": [None] * len(exp_values)})

    def test_entry_level(self):
        df = self._make_df(["fresher"])
        result = categorize_experience(df)
        assert result.iloc[0]["experience_level"] == "Entry"

    def test_junior(self):
        df = self._make_df(["Junior Developer"])
        result = categorize_experience(df)
        assert result.iloc[0]["experience_level"] == "Entry"

    def test_senior(self):
        df = self._make_df(["Senior Engineer"])
        result = categorize_experience(df)
        assert result.iloc[0]["experience_level"] == "Senior"

    def test_lead(self):
        df = self._make_df(["Lead Developer"])
        result = categorize_experience(df)
        assert result.iloc[0]["experience_level"] == "Lead"

    def test_years_based(self):
        df = self._make_df(["4 years"])
        result = categorize_experience(df)
        assert result.iloc[0]["experience_level"] == "Mid"

    def test_missing_defaults_to_entry(self):
        df = self._make_df([None])
        result = categorize_experience(df)
        assert result.iloc[0]["experience_level"] == "Entry"


# ===========================================================================
# Test: Salary Normalization
# ===========================================================================

class TestSalaryNormalization:
    def test_usd_passthrough(self):
        df = pd.DataFrame({
            "salary_raw": ["80000"],
            "salary_currency": ["USD"],
        })
        result = normalize_salaries(df)
        assert result.iloc[0]["avg_salary_usd"] == 80000.0

    def test_inr_lpa_conversion(self):
        df = pd.DataFrame({
            "salary_raw": ["10"],  # 10 LPA
            "salary_currency": ["INR"],
        })
        result = normalize_salaries(df)
        # 10 LPA = 1,000,000 INR → ~12,048 USD
        assert result.iloc[0]["avg_salary_usd"] > 10000
        assert result.iloc[0]["avg_salary_usd"] < 15000

    def test_outlier_removal(self):
        df = pd.DataFrame({
            "salary_raw": ["999999999"],
            "salary_currency": ["USD"],
        })
        result = normalize_salaries(df)
        assert pd.isna(result.iloc[0]["avg_salary_usd"])
