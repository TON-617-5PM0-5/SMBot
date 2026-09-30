"""Confirmation keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from messages import (
    CONFIRM_SALE, SWAP_PRICE_QTY, CANCEL_SALE,
    GUIDED_CONFIRM, GUIDED_CANCEL,
    BTN_EDIT_SALE, BTN_DELETE_SALE, BTN_BACK_TO_LIST,
    BTN_EDIT_ARTICLE, BTN_EDIT_PRICE, BTN_EDIT_QUANTITY,
    DELETE_YES, DELETE_NO,
)


def get_quick_add_confirm_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for quick add confirmation (3 buttons)."""
    keyboard = [
        [
            InlineKeyboardButton(CONFIRM_SALE, callback_data="quick_confirm"),
            InlineKeyboardButton(SWAP_PRICE_QTY, callback_data="quick_swap"),
        ],
        [
            InlineKeyboardButton(CANCEL_SALE, callback_data="quick_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_guided_confirm_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for guided add confirmation."""
    keyboard = [
        [
            InlineKeyboardButton(GUIDED_CONFIRM, callback_data="guided_confirm"),
            InlineKeyboardButton(GUIDED_CANCEL, callback_data="guided_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_edit_delete_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for edit/delete actions."""
    keyboard = [
        [
            InlineKeyboardButton(BTN_EDIT_SALE, callback_data="edit_sale"),
            InlineKeyboardButton(BTN_DELETE_SALE, callback_data="delete_sale"),
        ],
        [
            InlineKeyboardButton(BTN_BACK_TO_LIST, callback_data="back_to_sales_list"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_edit_field_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for choosing field to edit."""
    keyboard = [
        [
            InlineKeyboardButton(BTN_EDIT_ARTICLE, callback_data="edit_field_art"),
            InlineKeyboardButton(BTN_EDIT_PRICE, callback_data="edit_field_cost"),
        ],
        [
            InlineKeyboardButton(BTN_EDIT_QUANTITY, callback_data="edit_field_qty"),
        ],
        [
            InlineKeyboardButton(BTN_BACK_TO_LIST, callback_data="back_to_sale_details"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_delete_confirm_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for delete confirmation."""
    keyboard = [
        [
            InlineKeyboardButton(DELETE_YES, callback_data="delete_confirm"),
            InlineKeyboardButton(DELETE_NO, callback_data="delete_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)