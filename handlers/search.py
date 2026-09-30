"""Search products handler."""
from html import escape

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CommandHandler

from database import get_or_create_user, search_products
from keyboards import get_pagination_keyboard
from messages import (
    BACK_TO_MENU,
    SEARCH_EMPTY,
    SEARCH_NO_RESULTS,
    SEARCH_PROMPT,
    SEARCH_RESULTS_TITLE,
)
from utils.formatters import format_search_result


# Conversation state
SEARCH_QUERY = 0


async def search_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start search conversation."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(SEARCH_PROMPT, parse_mode="HTML")
    return SEARCH_QUERY


async def search_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle search query input."""
    query_text = update.message.text.strip()

    if not query_text:
        await update.message.reply_text(SEARCH_EMPTY, parse_mode="HTML")
        return SEARCH_QUERY

    user = update.effective_user
    db_user = await get_or_create_user(user.id)

    results = await search_products(db_user["id"], query_text)

    if not results:
        message = SEARCH_NO_RESULTS.format(query=escape(query_text))
    else:
        message = SEARCH_RESULTS_TITLE.format(query=escape(query_text)) + "\n\n"
        for item in results:
            message += format_search_result(item) + "\n"

    # Add back button
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(BACK_TO_MENU, callback_data="back_to_main")
    ]])

    await update.message.reply_text(message, parse_mode="HTML", reply_markup=keyboard)
    return ConversationHandler.END


async def search_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel search via /cancel command."""
    from handlers.start import show_default_message
    await show_default_message(update, context)
    return ConversationHandler.END


# Conversation handler
search_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(search_start_callback, pattern="^menu_search$"),
    ],
    states={
        SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_query_handler)],
    },
    fallbacks=[
        CommandHandler("cancel", search_cancel_command),
    ],
    per_message=False,
)