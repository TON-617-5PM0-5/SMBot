"""Pagination keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from messages import BACK_TO_MENU, PAGINATION_INFO, PAGINATION_NEXT, PAGINATION_PREV


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str,
    extra_buttons: list = None
) -> InlineKeyboardMarkup:
    """
    Get pagination keyboard.

    Args:
        current_page: Current page (0-indexed)
        total_pages: Total number of pages
        callback_prefix: Prefix for callback data (e.g., "sales")
        extra_buttons: Additional buttons to add at the bottom
    """
    keyboard = []

    if total_pages <= 0:
        if extra_buttons:
            keyboard.extend(extra_buttons)
        return InlineKeyboardMarkup(keyboard)

    # Navigation row
    nav_row = []
    if current_page > 0:
        nav_row.append(InlineKeyboardButton(
            PAGINATION_PREV,
            callback_data=f"{callback_prefix}_page_{current_page - 1}"
        ))
    if current_page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(
            PAGINATION_NEXT,
            callback_data=f"{callback_prefix}_page_{current_page + 1}"
        ))

    if nav_row:
        keyboard.append(nav_row)

    # Page info row
    keyboard.append([
        InlineKeyboardButton(
            PAGINATION_INFO.format(current=current_page + 1, total=total_pages),
            callback_data="pagination_info"
        )
    ])

    # Extra buttons (e.g., back to menu)
    if extra_buttons:
        keyboard.extend(extra_buttons)

    return InlineKeyboardMarkup(keyboard)


def get_sales_pagination_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Get pagination keyboard for sales view."""
    return get_pagination_keyboard(
        current_page,
        total_pages,
        "sales",
        [[InlineKeyboardButton(BACK_TO_MENU, callback_data="back_to_main")]]
    )