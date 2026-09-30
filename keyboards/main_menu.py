"""Main menu keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from messages import (
    BTN_VIEW_SALES,
    BTN_ADD_SALE,
    ADD_GUIDED_METHOD,
    ADD_QUICK_METHOD,
    BACK_TO_MENU,
    BTN_SEARCH,
    HIDE_INSTRUCTION,
    SHOW_INSTRUCTION,
)


def get_main_menu_keyboard(show_instruction: bool = True) -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    instruction_btn = HIDE_INSTRUCTION if show_instruction else SHOW_INSTRUCTION

    keyboard = [
        [
            InlineKeyboardButton(BTN_VIEW_SALES, callback_data="menu_view_sales"),
        ],
        [
            InlineKeyboardButton(BTN_ADD_SALE, callback_data="menu_add_sale"),
            InlineKeyboardButton(BTN_SEARCH, callback_data="menu_search"),
        ],
        [
            InlineKeyboardButton(instruction_btn, callback_data="toggle_instruction"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_sales_period_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for selecting sales view period."""
    from messages import VIEW_PERIOD_DAY, VIEW_PERIOD_WEEK, VIEW_PERIOD_MONTH, VIEW_PERIOD_YEAR

    keyboard = [
        [
            InlineKeyboardButton(VIEW_PERIOD_DAY, callback_data="sales_day"),
            InlineKeyboardButton(VIEW_PERIOD_WEEK, callback_data="sales_week"),
        ],
        [
            InlineKeyboardButton(VIEW_PERIOD_MONTH, callback_data="sales_month"),
            InlineKeyboardButton(VIEW_PERIOD_YEAR, callback_data="sales_year"),
        ],
        [
            InlineKeyboardButton(BACK_TO_MENU, callback_data="back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_add_sale_method_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for choosing add sale method."""
    keyboard = [
        [
            InlineKeyboardButton(ADD_QUICK_METHOD, callback_data="quick_add"),
            InlineKeyboardButton(ADD_GUIDED_METHOD, callback_data="guided_add"),
        ],
        [
            InlineKeyboardButton(BACK_TO_MENU, callback_data="back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)