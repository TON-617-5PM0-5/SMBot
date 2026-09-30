"""Guided add sale handler - step by step conversation."""
from html import escape

from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler,
    CallbackQueryHandler, CommandHandler, filters
)

from database import get_or_create_user, add_sale
from keyboards import get_guided_confirm_keyboard
from messages import (
    GUIDED_ADD_START, GUIDED_ADD_ARTICLE, GUIDED_ADD_PRICE,
    DATA_LOST, GUIDED_ADD_QUANTITY, GUIDED_CONFIRM, GUIDED_CANCEL,
    INVALID_PRICE, INVALID_QUANTITY, SALE_ADDED_SUCCESS,
    SALE_CANCELLED, ERROR_GENERIC
)
from utils.helpers import is_valid_price, is_valid_quantity
from utils.formatters import format_guided_add_step

# Conversation states
ARTICLE, PRICE, QUANTITY, CONFIRM = range(4)

# User data keys
GUIDED_ARTICLE_KEY = "guided_article"
GUIDED_PRICE_KEY = "guided_price"
GUIDED_QUANTITY_KEY = "guided_quantity"


async def guided_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start guided add conversation."""
    query = update.callback_query
    if query:
        await query.answer()

    # Clear any previous data
    context.user_data.pop(GUIDED_ARTICLE_KEY, None)
    context.user_data.pop(GUIDED_PRICE_KEY, None)
    context.user_data.pop(GUIDED_QUANTITY_KEY, None)

    message = format_guided_add_step(None, None, None)

    if query:
        await query.edit_message_text(message, parse_mode="HTML")
    else:
        await update.message.reply_text(message, parse_mode="HTML")

    return ARTICLE


async def guided_add_article(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle article input."""
    text = update.message.text.strip()

    # Handle skip
    if text == "-":
        article = None
    else:
        article = text if text else None

    context.user_data[GUIDED_ARTICLE_KEY] = article

    message = GUIDED_ADD_ARTICLE.format(article=escape(article or "—"))
    await update.message.reply_text(message, parse_mode="HTML")

    return PRICE


async def guided_add_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle price input."""
    text = update.message.text.strip()

    if not is_valid_price(text):
        await update.message.reply_text(INVALID_PRICE, parse_mode="HTML")
        return PRICE

    price = float(text.replace(",", "."))
    context.user_data[GUIDED_PRICE_KEY] = price

    article = context.user_data.get(GUIDED_ARTICLE_KEY)
    message = GUIDED_ADD_PRICE.format(article=escape(article or "—"), price=price)
    await update.message.reply_text(message, parse_mode="HTML")

    return QUANTITY


async def guided_add_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle quantity input."""
    text = update.message.text.strip()

    if not is_valid_quantity(text):
        await update.message.reply_text(INVALID_QUANTITY, parse_mode="HTML")
        return QUANTITY

    quantity = int(text)
    context.user_data[GUIDED_QUANTITY_KEY] = quantity

    article = context.user_data.get(GUIDED_ARTICLE_KEY)
    price = context.user_data.get(GUIDED_PRICE_KEY)

    # Show confirmation
    article_display = article or "—"

    message = GUIDED_ADD_QUANTITY.format(
        article=escape(article_display),
        price=price,
        quantity=quantity,
        total=price * quantity
    )

    keyboard = get_guided_confirm_keyboard()
    await update.message.reply_text(message, parse_mode="HTML", reply_markup=keyboard)

    return CONFIRM


async def guided_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm and save guided sale."""
    query = update.callback_query
    await query.answer()

    article = context.user_data.get(GUIDED_ARTICLE_KEY)
    price = context.user_data.get(GUIDED_PRICE_KEY)
    quantity = context.user_data.get(GUIDED_QUANTITY_KEY)

    if price is None or quantity is None:
        await query.edit_message_text(DATA_LOST, parse_mode="HTML")
        return ConversationHandler.END

    user = update.effective_user
    db_user = await get_or_create_user(user.id)

    try:
        sale_id = await add_sale(
            user_id=db_user["id"],
            cost=price,
            quantity=quantity,
            art=article
        )

        # Clear user data
        context.user_data.pop(GUIDED_ARTICLE_KEY, None)
        context.user_data.pop(GUIDED_PRICE_KEY, None)
        context.user_data.pop(GUIDED_QUANTITY_KEY, None)

        await query.edit_message_text(
            SALE_ADDED_SUCCESS.format(sale_id=sale_id),
            parse_mode="HTML"
        )

        # Show default message
        from handlers.start import show_default_message
        await show_default_message(update, context)

    except Exception as e:
        await query.edit_message_text(ERROR_GENERIC, parse_mode="HTML")

    return ConversationHandler.END


async def guided_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel guided sale addition."""
    query = update.callback_query
    await query.answer()

    context.user_data.pop(GUIDED_ARTICLE_KEY, None)
    context.user_data.pop(GUIDED_PRICE_KEY, None)
    context.user_data.pop(GUIDED_QUANTITY_KEY, None)

    await query.edit_message_text(SALE_CANCELLED, parse_mode="HTML")

    from handlers.start import show_default_message
    await show_default_message(update, context)

    return ConversationHandler.END


async def guided_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel via /cancel command."""
    context.user_data.pop(GUIDED_ARTICLE_KEY, None)
    context.user_data.pop(GUIDED_PRICE_KEY, None)
    context.user_data.pop(GUIDED_QUANTITY_KEY, None)

    await update.message.reply_text(SALE_CANCELLED, parse_mode="HTML")

    from handlers.start import show_default_message
    await show_default_message(update, context)

    return ConversationHandler.END


# Conversation handler
guided_add_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(guided_add_start, pattern="^guided_add$"),
    ],
    states={
        ARTICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, guided_add_article)],
        PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, guided_add_price)],
        QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, guided_add_quantity)],
        CONFIRM: [
            CallbackQueryHandler(guided_confirm_callback, pattern="^guided_confirm$"),
            CallbackQueryHandler(guided_cancel_callback, pattern="^guided_cancel$"),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", guided_cancel_command),
    ],
    per_message=False,
)