"""Database queries for SalesManagmentBot."""
from datetime import datetime, timedelta
import math
from typing import Optional, List, Dict, Any

from database.connection import get_connection, transaction


_UNSET = object()


def _sql_datetime(value: datetime) -> str:
    """Format a datetime using SQLite's timestamp representation."""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _date_params(period: str) -> tuple[str, str]:
    """Return SQLite-compatible boundaries for a reporting period."""
    start, end = _get_date_range(period)
    return _sql_datetime(start), _sql_datetime(end)


# --- User Queries ---

async def get_or_create_user(telegram_user_id: int) -> Dict[str, Any]:
    """Get user by telegram ID or create new one."""
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT * FROM users WHERE telegram_user_id = ?",
        (telegram_user_id,)
    )
    user = await cursor.fetchone()

    if user:
        return dict(user)

    # Create new user
    async with transaction() as conn:
        cursor = await conn.execute(
            "INSERT INTO users (telegram_user_id) VALUES (?)",
            (telegram_user_id,)
        )
        user_id = cursor.lastrowid
        cursor = await conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        user = await cursor.fetchone()
        return dict(user)


async def get_user_by_telegram_id(telegram_user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by telegram ID."""
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT * FROM users WHERE telegram_user_id = ?",
        (telegram_user_id,)
    )
    user = await cursor.fetchone()
    return dict(user) if user else None


async def toggle_quick_instruction(telegram_user_id: int) -> bool:
    """Toggle show_quick_instruction setting. Returns new value."""
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT show_quick_instruction FROM users WHERE telegram_user_id = ?",
        (telegram_user_id,)
    )
    user = await cursor.fetchone()
    if not user:
        return True

    new_value = not user["show_quick_instruction"]
    await conn.execute(
        "UPDATE users SET show_quick_instruction = ? WHERE telegram_user_id = ?",
        (new_value, telegram_user_id)
    )
    await conn.commit()
    return new_value


# --- Sale Queries ---

async def add_sale(
    user_id: int,
    cost: float,
    quantity: int,
    art: Optional[str] = None
) -> int:
    """Add a new sale and return its ID."""
    if not math.isfinite(cost) or cost <= 0:
        raise ValueError("cost must be a positive finite number")
    if quantity <= 0:
        raise ValueError("quantity must be positive")

    total_cost = cost * quantity
    async with transaction() as conn:
        cursor = await conn.execute(
            """
            INSERT INTO sales (user_id, art, cost, quantity, total_cost, date_of_creation)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                art,
                cost,
                quantity,
                total_cost,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        return cursor.lastrowid


async def get_sale_by_id(sale_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Get a sale by ID for a specific user."""
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT * FROM sales WHERE id = ? AND user_id = ?",
        (sale_id, user_id)
    )
    sale = await cursor.fetchone()
    return dict(sale) if sale else None


async def update_sale(
    sale_id: int,
    user_id: int,
    art: object = _UNSET,
    cost: object = _UNSET,
    quantity: object = _UNSET,
) -> bool:
    """Update a sale. Pass ``art=None`` to clear the article."""
    updates = []
    params = []

    if art is not _UNSET:
        updates.append("art = ?")
        params.append(art)
    if cost is not _UNSET:
        updates.append("cost = ?")
        params.append(cost)
    if quantity is not _UNSET:
        updates.append("quantity = ?")
        params.append(quantity)

    if not updates:
        return False

    # Recalculate total_cost if cost or quantity changed.
    if cost is not _UNSET or quantity is not _UNSET:
        sale = await get_sale_by_id(sale_id, user_id)
        if not sale:
            return False
        new_cost = cost if cost is not _UNSET else sale["cost"]
        new_quantity = quantity if quantity is not _UNSET else sale["quantity"]
        updates.append("total_cost = ?")
        params.append(new_cost * new_quantity)

    params.extend([sale_id, user_id])

    async with transaction() as conn:
        cursor = await conn.execute(
            f"UPDATE sales SET {', '.join(updates)} WHERE id = ? AND user_id = ?",
            params,
        )
        return cursor.rowcount > 0


async def delete_sale(sale_id: int, user_id: int) -> bool:
    """Delete a sale. Returns True if deleted."""
    async with transaction() as conn:
        cursor = await conn.execute(
            "DELETE FROM sales WHERE id = ? AND user_id = ?",
            (sale_id, user_id)
        )
        return cursor.rowcount > 0


# --- Analytics Queries ---

def _get_date_range(period: str) -> tuple:
    """Get start and end dates for a period."""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    if period == "day":
        return today_start, today_end
    elif period == "week":
        week_start = today_start - timedelta(days=today_start.weekday())
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return week_start, week_end
    elif period == "month":
        month_start = today_start.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(seconds=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1) - timedelta(seconds=1)
        return month_start, month_end
    elif period == "year":
        year_start = today_start.replace(month=1, day=1)
        year_end = year_start.replace(year=year_start.year + 1) - timedelta(seconds=1)
        return year_start, year_end
    else:
        return today_start, today_end


async def get_sales_stats(user_id: int, period: str) -> Dict[str, Any]:
    """Get sales count and total for a period."""
    start_date, end_date = _get_date_range(period)
    conn = await get_connection()
    cursor = await conn.execute(
        """
        SELECT COUNT(*) as count, COALESCE(SUM(total_cost), 0) as total
        FROM sales
        WHERE user_id = ? AND datetime(date_of_creation) BETWEEN datetime(?) AND datetime(?)
        """,
        (user_id, start_date.isoformat(), end_date.isoformat())
    )
    row = await cursor.fetchone()
    count = row["count"] or 0
    total = row["total"] or 0
    return {"count": count, "total": total}


async def get_sales_list(
    user_id: int,
    period: str,
    page: int = 0,
    per_page: int = 10
) -> Dict[str, Any]:
    """Get paginated sales list for a period."""
    start_date, end_date = _get_date_range(period)
    offset = page * per_page

    conn = await get_connection()

    # Get total count
    cursor = await conn.execute(
        """
        SELECT COUNT(*) as count
        FROM sales
        WHERE user_id = ? AND datetime(date_of_creation) BETWEEN datetime(?) AND datetime(?)
        """,
        (user_id, start_date.isoformat(), end_date.isoformat())
    )
    total_count = (await cursor.fetchone())["count"]

    # Get sales
    cursor = await conn.execute(
        """
        SELECT * FROM sales
        WHERE user_id = ? AND datetime(date_of_creation) BETWEEN datetime(?) AND datetime(?)
        ORDER BY date_of_creation DESC
        LIMIT ? OFFSET ?
        """,
        (user_id, start_date.isoformat(), end_date.isoformat(), per_page, offset)
    )
    sales = [dict(row) for row in await cursor.fetchall()]

    total_pages = (total_count + per_page - 1) // per_page

    return {
        "sales": sales,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": page
    }


async def search_products(
    user_id: int,
    query: str,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Search products by article, price, or aggregate by article."""
    conn = await get_connection()

    # Try to parse query as price
    try:
        price_query = float(query.replace(",", "."))
        is_price = True
    except ValueError:
        is_price = False

    if is_price:
        # Search by exact price
        cursor = await conn.execute(
            """
            SELECT art, cost, COUNT(*) as count, SUM(total_cost) as total
            FROM sales
            WHERE user_id = ? AND cost = ?
            GROUP BY art, cost
            ORDER BY count DESC
            LIMIT ?
            """,
            (user_id, price_query, limit)
        )
    else:
        # Search by article (partial match)
        cursor = await conn.execute(
            """
            SELECT art, cost, COUNT(*) as count, SUM(total_cost) as total
            FROM sales
            WHERE user_id = ? AND art LIKE ?
            GROUP BY art, cost
            ORDER BY count DESC
            LIMIT ?
            """,
            (user_id, f"%{query}%", limit)
        )

    return [dict(row) for row in await cursor.fetchall()]


async def get_sales_breakdown(
    user_id: int,
    period: str,
) -> List[Dict[str, Any]]:
    """Return period totals grouped by day or month."""
    start_date, end_date = _date_params(period)
    group_expression = {
        "day": "date(date_of_creation)",
        "week": "date(date_of_creation)",
        "month": "date(date_of_creation)",
        "year": "strftime('%Y-%m', date_of_creation)",
    }.get(period, "date(date_of_creation)")

    conn = await get_connection()
    cursor = await conn.execute(
        f"""
        SELECT {group_expression} AS period_key,
               COUNT(*) AS count,
               COALESCE(SUM(total_cost), 0) AS total
        FROM sales
        WHERE user_id = ?
          AND datetime(date_of_creation) BETWEEN datetime(?) AND datetime(?)
        GROUP BY {group_expression}
        ORDER BY period_key
        """,
        (user_id, start_date, end_date),
    )
    return [dict(row) for row in await cursor.fetchall()]


async def get_all_sales_for_user(user_id: int) -> List[Dict[str, Any]]:
    """Get all sales for a user (for search/export)."""
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT * FROM sales WHERE user_id = ? ORDER BY date_of_creation DESC",
        (user_id,)
    )
    return [dict(row) for row in await cursor.fetchall()]