"""
ETL Pipeline Orchestrator — ties Extract, Transform, Validate, Load together.

Usage:
    from etl.pipeline import run_pipeline
    run_pipeline()
"""

import time

from config.logging_config import setup_logger
from etl.extractor import extract_all
from etl.transformer import transform
from etl.validators import validate_records
from etl.loader import load_to_database

logger = setup_logger("etl.pipeline")


def run_pipeline(data_dir=None) -> dict:
    """
    Run the complete ETL pipeline:
        1. Extract CSVs → unified DataFrame
        2. Transform (clean, normalize, enrich)
        3. Validate (Pydantic)
        4. Load into PostgreSQL

    Args:
        data_dir: Optional override for raw data directory.

    Returns:
        dict with pipeline summary stats.
    """
    start_time = time.time()

    logger.info("=" * 70)
    logger.info("  TECH TALENT INTELLIGENCE PLATFORM — ETL PIPELINE")
    logger.info("=" * 70)

    # ------------------------------------------------------------------
    # Step 1: Extract
    # ------------------------------------------------------------------
    logger.info("\n[1/4] EXTRACTING data from CSV files...")
    raw_df = extract_all(data_dir)
    extract_count = len(raw_df)

    # ------------------------------------------------------------------
    # Step 2: Transform
    # ------------------------------------------------------------------
    logger.info("\n[2/4] TRANSFORMING data...")
    transformed_df = transform(raw_df)
    transform_count = len(transformed_df)

    # ------------------------------------------------------------------
    # Step 3: Validate
    # ------------------------------------------------------------------
    logger.info("\n[3/4] VALIDATING records...")
    valid_records = validate_records(transformed_df)
    valid_count = len(valid_records)

    # ------------------------------------------------------------------
    # Step 4: Load
    # ------------------------------------------------------------------
    logger.info("\n[4/4] LOADING into PostgreSQL...")
    load_stats = load_to_database(valid_records)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    duration = time.time() - start_time

    summary = {
        "total_extracted": extract_count,
        "after_transform": transform_count,
        "valid_records": valid_count,
        "loaded": load_stats,
        "duration_seconds": round(duration, 2),
    }

    logger.info("")
    logger.info("=" * 70)
    logger.info("  ETL PIPELINE SUMMARY")
    logger.info("=" * 70)
    logger.info("  Records extracted:    %d", extract_count)
    logger.info("  After transformation: %d", transform_count)
    logger.info("  Valid records:        %d", valid_count)
    logger.info("  Jobs loaded:          %d", load_stats.get("jobs", 0))
    logger.info("  Salaries loaded:      %d", load_stats.get("salaries", 0))
    logger.info("  Job-skill links:      %d", load_stats.get("job_skills", 0))
    logger.info("  Duration:             %.2f seconds", duration)
    logger.info("=" * 70)

    return summary
