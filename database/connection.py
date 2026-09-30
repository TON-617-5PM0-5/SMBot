"""Database connection management using aiosqlite."""
import aiosqlite
from contextlib import asynccontextmanager
from config import DB_PATH


# Global connection pool (single connection for SQLite)
_connection: aiosqlite.Connection | None = None


async def get_connection() -> aiosqlite.Connection:
    """Get or create the database connection."""
    global _connection
    if _connection is None:
        _connection = await aiosqlite.connect(DB_PATH)
        _connection.row_factory = aiosqlite.Row
        # Enable foreign keys
        await _connection.execute("PRAGMA foreign_keys = ON")
    return _connection


async def close_connection() -> None:
    """Close the database connection."""
    global _connection
    if _connection is not None:
        await _connection.close()
        _connection = None


@asynccontextmanager
async def transaction():
    """Context manager for database transactions."""
    conn = await get_connection()
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise


async def init_database() -> None:
    """Initialize database - create tables if not exist."""
    conn = await get_connection()

    # Users table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER UNIQUE NOT NULL,
            show_quick_instruction BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sales table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            art TEXT,
            cost REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            total_cost REAL NOT NULL,
            date_of_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Indexes for performance
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_user_date
        ON sales(user_id, date_of_creation)
    """)

    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_art
        ON sales(art)
    """)

    await conn.commit()