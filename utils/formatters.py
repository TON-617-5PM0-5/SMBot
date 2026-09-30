"""Message formatting utilities."""
from datetime import datetime
from html import escape
from typing import Optional
from config import DATE_FORMAT, DATETIME_FORMAT


def format_date(dt: datetime | str) -> str:
    """Format datetime for display."""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            return dt
    return dt.strftime(DATE_FORMAT)


def format_datetime(dt: datetime | str) -> str:
    """Format datetime with time for display."""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            return dt
    return dt.strftime(DATETIME_FORMAT)


def format_sale_item(sale: dict) -> str:
    """Format a single sale item for display."""
    from messages import SALE_ITEM_TEMPLATE, ARTICLE_LINE

    article_line = ""
    if sale.get("art"):
        article_line = ARTICLE_LINE.format(article=escape(str(sale["art"])))

    return SALE_ITEM_TEMPLATE.format(
        sale_id=sale["id"],
        article_line=article_line,
        price=sale["cost"],
        quantity=sale["quantity"],
        total=sale["total_cost"],
        date=format_datetime(sale["date_of_creation"])
    )


def format_sale_details(sale: dict) -> str:
    """Format sale details for edit/delete confirmation."""
    from messages import SALE_DETAILS_FOR_EDIT, ARTICLE_LINE

    article_line = ""
    if sale.get("art"):
        article_line = ARTICLE_LINE.format(article=escape(str(sale["art"])))

    return SALE_DETAILS_FOR_EDIT.format(
        sale_id=sale["id"],
        article_line=article_line,
        price=sale["cost"],
        quantity=sale["quantity"],
        total=sale["total_cost"],
        date=format_datetime(sale["date_of_creation"])
    )


def format_search_result(item: dict) -> str:
    """Format search result item."""
    from messages import SEARCH_RESULT_ITEM

    article = escape(str(item.get("art") or "—"))

    return SEARCH_RESULT_ITEM.format(
        article=article,
        price=item["cost"],
        count=item["count"],
        total=item["total"]
    )


def format_quick_add_confirmation(parsed_sale) -> str:
    """Format quick add confirmation message."""
    from messages import QUICK_ADD_PARSED, ARTICLE_LINE

    article_line = ""
    if parsed_sale.article:
        article_line = ARTICLE_LINE.format(article=escape(str(parsed_sale.article)))
    return QUICK_ADD_PARSED.format(
        article_line=article_line,
        price=parsed_sale.price,
        quantity=parsed_sale.quantity,
        total=parsed_sale.total
    )


def format_guided_add_step(article: Optional[str], price: Optional[float], quantity: Optional[int]) -> str:
    """Format guided add step message."""
    from messages import (
        GUIDED_ADD_ARTICLE, GUIDED_ADD_PRICE, GUIDED_ADD_QUANTITY, GUIDED_ADD_START
    )

    if price is None and quantity is None:
        # First step - asking for article
        return GUIDED_ADD_START

    if quantity is None:
        # Asking for quantity
        return GUIDED_ADD_PRICE.format(article=article or "—", price=price)

    # All filled - confirmation
    article_display = article or "—"
    return GUIDED_ADD_QUANTITY.format(
        article=article_display,
        price=price,
        quantity=quantity,
        total=price * quantity
    )