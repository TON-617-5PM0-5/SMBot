"""Keyboards package initialization."""
from keyboards.main_menu import (
    get_main_menu_keyboard,
    get_sales_period_keyboard,
    get_add_sale_method_keyboard,
)
from keyboards.confirm import (
    get_quick_add_confirm_keyboard,
    get_guided_confirm_keyboard,
    get_edit_delete_keyboard,
    get_edit_field_keyboard,
    get_delete_confirm_keyboard,
)
from keyboards.pagination import (
    get_pagination_keyboard,
    get_sales_pagination_keyboard,
)

__all__ = [
    "get_main_menu_keyboard",
    "get_sales_period_keyboard",
    "get_add_sale_method_keyboard",
    "get_quick_add_confirm_keyboard",
    "get_guided_confirm_keyboard",
    "get_edit_delete_keyboard",
    "get_edit_field_keyboard",
    "get_delete_confirm_keyboard",
    "get_pagination_keyboard",
    "get_sales_pagination_keyboard",
]
