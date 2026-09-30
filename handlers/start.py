"""Start command and default message handler."""
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from database import get_or_create_user, get_sales_stats, toggle_quick_instruction
from keyboards import get_main_menu_keyboard, get_add_sale_method_keyboard
from messages import (
    ADD_SALE_METHOD_PROMPT,
    QUICK_ADD_PROMPT,
    WELCOME_MESSAGE,
    get_default_message,
)
from utils.helpers import get_period_name
from config import DATE_FORMAT


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    db_user = await get_or_create_user(user.id)

    # Get stats for default message
    day_stats = await get_sales_stats(db_user["id"], "day")
    week_stats = await get_sales_stats(db_user["id"], "week")
    month_stats = await get_sales_stats(db_user["id"], "month")

    current_date = datetime.now().strftime(DATE_FORMAT)
    show_instruction = db_user.get("show_quick_instruction", True)

    message = get_default_message(
        day_sales=day_stats["count"],
        day_total=day_stats["total"],
        week_sales=week_stats["count"],
        week_total=week_stats["total"],
        month_sales=month_stats["count"],
        month_total=month_stats["total"],
        current_date=current_date,
        show_instruction=show_instruction
    )

    keyboard = get_main_menu_keyboard(show_instruction)

    if update.message:
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        # Called from callback query
        await update.callback_query.edit_message_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )


async def show_default_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show default message (used after actions)."""
    user = update.effective_user
    db_user = await get_or_create_user(user.id)

    day_stats = await get_sales_stats(db_user["id"], "day")
    week_stats = await get_sales_stats(db_user["id"], "week")
    month_stats = await get_sales_stats(db_user["id"], "month")

    current_date = datetime.now().strftime(DATE_FORMAT)
    show_instruction = db_user.get("show_quick_instruction", True)

    message = get_default_message(
        day_sales=day_stats["count"],
        day_total=day_stats["total"],
        week_sales=week_stats["count"],
        week_total=week_stats["total"],
        month_sales=month_stats["count"],
        month_total=month_stats["total"],
        current_date=current_date,
        show_instruction=show_instruction
    )

    keyboard = get_main_menu_keyboard(show_instruction)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    elif update.message:
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )


async def toggle_instruction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle quick instruction visibility."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    new_value = await toggle_quick_instruction(user.id)

    # Refresh the default message
    await show_default_message(update, context)


async def add_sale_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the quick or guided sale entry options."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        ADD_SALE_METHOD_PROMPT,
        parse_mode="HTML",
        reply_markup=get_add_sale_method_keyboard(),
    )


async def quick_add_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain how to start a quick sale entry."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(QUICK_ADD_PROMPT, parse_mode="HTML")


# Handlers
start_handler = CommandHandler("start", start_command)
add_sale_menu_handler = CallbackQueryHandler(add_sale_menu_callback, pattern="^menu_add_sale$")
quick_add_menu_handler = CallbackQueryHandler(quick_add_menu_callback, pattern="^quick_add$")
toggle_instruction_handler = CallbackQueryHandler(toggle_instruction_callback, pattern="^toggle_instruction$")
back_to_main_handler = CallbackQueryHandler(show_default_message, pattern="^back_to_main$")