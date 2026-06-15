"""
CLI entry point to run the ETL pipeline.

Usage:
    python scripts/run_etl.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.pipeline import run_pipeline


if __name__ == "__main__":
    print("Starting ETL pipeline...")
    summary = run_pipeline()
    print(f"\nDone! Loaded {summary['loaded']['jobs']} jobs in {summary['duration_seconds']}s")
