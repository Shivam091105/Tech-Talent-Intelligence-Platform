"""
PostgreSQL connection manager using SQLAlchemy.
Provides a reusable engine and session factory for the entire application.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE_URL
from config.logging_config import setup_logger

logger = setup_logger("database")

# ---------------------------------------------------------------------------
# SQLAlchemy engine (singleton per process)
# ---------------------------------------------------------------------------
_engine = None


def get_engine():
    """Return (and lazily create) the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # auto-reconnect stale connections
        )
        logger.info("Database engine created for %s", DATABASE_URL.split("@")[-1])
    return _engine


def get_session():
    """Return a new SQLAlchemy session."""
    Session = sessionmaker(bind=get_engine())
    return Session()


def execute_query(query: str, params: dict = None):
    """
    Execute a raw SQL query and return all rows as a list of dicts.

    Args:
        query: SQL string (can use :param_name placeholders).
        params: Optional dict of parameter values.

    Returns:
        List of dicts for SELECT queries, None for non-SELECT.
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        if result.returns_rows:
            columns = list(result.keys())
            return [dict(zip(columns, row)) for row in result.fetchall()]
        conn.commit()
        return None


def execute_query_df(query: str, params: dict = None):
    """
    Execute a SQL query and return results as a Pandas DataFrame.

    Args:
        query: SQL string.
        params: Optional dict of parameter values.

    Returns:
        pandas.DataFrame with query results.
    """
    import pandas as pd

    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params or {})


def test_connection() -> bool:
    """Test database connectivity. Returns True if successful."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test: SUCCESS")
        return True
    except Exception as e:
        logger.error("Database connection test: FAILED — %s", e)
        return False
