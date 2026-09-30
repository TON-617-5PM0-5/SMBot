"""Database package initialization."""
from database.connection import init_database, get_connection, close_connection, transaction
from database.queries import (
    get_or_create_user,
    get_user_by_telegram_id,
    toggle_quick_instruction,
    add_sale,
    get_sale_by_id,
    update_sale,
    delete_sale,
    get_sales_stats,
    get_sales_list,
    get_sales_breakdown,
    search_products,
    get_all_sales_for_user,
)

__all__ = [
    "init_database",
    "get_connection",
    "close_connection",
    "transaction",
    "get_or_create_user",
    "get_user_by_telegram_id",
    "toggle_quick_instruction",
    "add_sale",
    "get_sale_by_id",
    "update_sale",
    "delete_sale",
    "get_sales_stats",
    "get_sales_list",
    "get_sales_breakdown",
    "search_products",
    "get_all_sales_for_user",
]