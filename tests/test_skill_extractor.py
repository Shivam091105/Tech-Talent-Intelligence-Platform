"""
Unit tests for the skill extraction logic.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd

from etl.transformer import extract_skills


class TestSkillExtraction:
    def _make_df(self, skills_texts):
        return pd.DataFrame({"skills_text": skills_texts})

    def test_exact_match(self):
        df = self._make_df(["Python, Java, SQL"])
        result = extract_skills(df)
        skills = result.iloc[0]["extracted_skills"]
        assert "python" in skills
        assert "java" in skills
        assert "sql" in skills

    def test_alias_match(self):
        df = self._make_df(["ReactJS and NodeJS"])
        result = extract_skills(df)
        skills = result.iloc[0]["extracted_skills"]
        assert "react" in skills
        assert "node.js" in skills

    def test_case_insensitive(self):
        df = self._make_df(["PYTHON, JAVA, AWS"])
        result = extract_skills(df)
        skills = result.iloc[0]["extracted_skills"]
        assert "python" in skills
        assert "aws" in skills

    def test_empty_text(self):
        df = self._make_df([""])
        result = extract_skills(df)
        assert len(result.iloc[0]["extracted_skills"]) == 0

    def test_nan_text(self):
        df = self._make_df([None])
        result = extract_skills(df)
        assert len(result.iloc[0]["extracted_skills"]) == 0

    def test_cloud_skills(self):
        df = self._make_df(["Amazon Web Services, Google Cloud Platform"])
        result = extract_skills(df)
        skills = result.iloc[0]["extracted_skills"]
        assert "aws" in skills
        assert "gcp" in skills

    def test_framework_detection(self):
        df = self._make_df(["Spring Boot microservices with Docker and Kubernetes"])
        result = extract_skills(df)
        skills = result.iloc[0]["extracted_skills"]
        assert "spring" in skills
        assert "docker" in skills
        assert "kubernetes" in skills
        assert "microservices" in skills
