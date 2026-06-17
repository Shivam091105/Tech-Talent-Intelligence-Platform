"""
Database initialization script.
Creates the database (if needed) and the PostgreSQL schema by executing schema.sql.

Usage:
    python scripts/setup_database.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text

from config.settings import PROJECT_ROOT, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from config.logging_config import setup_logger

logger = setup_logger("setup_database")


def _create_database_if_not_exists():
    """
    Connect to the default 'postgres' database and create our target DB
    if it doesn't already exist.
    """
    # Connect to the default 'postgres' maintenance database
    maintenance_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"

    try:
        engine = create_engine(maintenance_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            # Check if our database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": DB_NAME},
            )
            exists = result.fetchone() is not None

            if not exists:
                conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
                logger.info("Created database: %s", DB_NAME)
            else:
                logger.info("Database already exists: %s", DB_NAME)

        engine.dispose()
        return True

    except Exception as e:
        logger.error("Failed to create database: %s", e)
        logger.error("Make sure PostgreSQL is running and user '%s' can connect.", DB_USER)
        return False


def setup_database():
    """Create the database (if needed) and apply schema.sql."""
    logger.info("=" * 60)
    logger.info("Tech Talent Intelligence Platform — Database Setup")
    logger.info("=" * 60)

    # Step 1: Create database if it doesn't exist
    logger.info("Step 1: Ensuring database '%s' exists...", DB_NAME)
    if not _create_database_if_not_exists():
        sys.exit(1)

    # Step 2: Connect to our database and test
    from database.connection import test_connection, get_engine, execute_query

    if not test_connection():
        logger.error("Cannot connect to database '%s'.", DB_NAME)
        sys.exit(1)

    # Step 3: Read and execute schema file
    schema_path = PROJECT_ROOT / "database" / "schema.sql"
    if not schema_path.exists():
        logger.error("Schema file not found: %s", schema_path)
        sys.exit(1)

    schema_sql = schema_path.read_text(encoding="utf-8")
    logger.info("Step 2: Applying schema (%d bytes)...", len(schema_sql))

    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text(schema_sql))
        conn.commit()

    logger.info("Schema applied successfully!")

    # Step 4: Verify tables
    logger.info("Step 3: Verifying tables...")
    tables = execute_query("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    logger.info("Tables in database:")
    for t in tables:
        logger.info("  [OK] %s", t["table_name"])

    views = execute_query("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    logger.info("Views in database:")
    for v in views:
        logger.info("  [OK] %s", v["table_name"])

    logger.info("=" * 60)
    logger.info("Database setup complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    setup_database()
