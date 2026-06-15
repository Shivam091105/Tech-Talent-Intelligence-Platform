"""
Database initialization script.
Creates the PostgreSQL schema by executing schema.sql.

Usage:
    python scripts/setup_database.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import PROJECT_ROOT
from config.logging_config import setup_logger
from database.connection import get_engine, test_connection

logger = setup_logger("setup_database")


def setup_database():
    """Read schema.sql and execute it against the configured PostgreSQL database."""
    logger.info("=" * 60)
    logger.info("Tech Talent Intelligence Platform — Database Setup")
    logger.info("=" * 60)

    # Test connectivity first
    if not test_connection():
        logger.error("Cannot connect to database. Is PostgreSQL running?")
        logger.error("Start it with: docker-compose up -d db")
        sys.exit(1)

    # Read schema file
    schema_path = PROJECT_ROOT / "database" / "schema.sql"
    if not schema_path.exists():
        logger.error("Schema file not found: %s", schema_path)
        sys.exit(1)

    schema_sql = schema_path.read_text(encoding="utf-8")
    logger.info("Read schema file: %s (%d bytes)", schema_path.name, len(schema_sql))

    # Execute schema
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(__import__("sqlalchemy").text(schema_sql))
        conn.commit()

    logger.info("Schema created successfully!")
    logger.info("=" * 60)

    # Verify tables
    from database.connection import execute_query
    tables = execute_query("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    logger.info("Tables in database:")
    for t in tables:
        logger.info("  ✓ %s", t["table_name"])

    logger.info("=" * 60)
    logger.info("Database setup complete!")


if __name__ == "__main__":
    setup_database()
