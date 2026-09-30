"""Helper utilities for date/time and other common operations."""
from datetime import datetime, timedelta
import math
from typing import Tuple


def get_period_dates(period: str) -> Tuple[datetime, datetime]:
    """Get start and end datetime for a given period."""
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


def get_period_name(period: str) -> str:
    """Get Ukrainian period name."""
    names = {
        "day": "сьогодні",
        "week": "тиждень",
        "month": "місяць",
        "year": "рік",
    }
    return names.get(period, period)


def is_valid_price(text: str) -> bool:
    """Check if text is a positive, finite price."""
    try:
        value = float(text.replace(",", "."))
    except ValueError:
        return False
    return math.isfinite(value) and value > 0


def is_valid_quantity(text: str) -> bool:
    """Check if text is a valid quantity (positive integer)."""
    try:
        val = int(text)
        return val > 0
    except ValueError:
        return False