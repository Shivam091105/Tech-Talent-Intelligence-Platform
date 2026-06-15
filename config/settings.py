"""
Central configuration module.
Loads settings from environment variables with sensible defaults for local development.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env file (only in development; production uses real env vars)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DICTIONARIES_DIR = DATA_DIR / "dictionaries"
ML_MODELS_DIR = PROJECT_ROOT / "ml" / "models"

# Ensure key directories exist
for _dir in [RAW_DATA_DIR, PROCESSED_DATA_DIR, ML_MODELS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tech_talent_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Fixed USD exchange rates for salary normalization
EXCHANGE_RATES = {
    "INR": 83.0,   # 1 USD = 83 INR
    "EUR": 0.92,
    "GBP": 0.79,
    "CAD": 1.36,
    "AUD": 1.53,
    "USD": 1.0,
}

# Experience level boundaries (in years)
EXPERIENCE_LEVELS = {
    "Entry":  (0, 2),
    "Mid":    (3, 5),
    "Senior": (6, 10),
    "Lead":   (10, 99),
}

# Top metro cities for binary feature in ML model
METRO_CITIES = [
    "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune",
    "New York", "San Francisco", "London", "Seattle", "Berlin",
    "Toronto", "Singapore", "Tokyo", "Sydney",
]
