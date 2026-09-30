"""Quick add sale handler - parse text input and confirm."""
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

from database import get_or_create_user, add_sale
from utils import parse_quick_sale, ParsedSale
from utils.formatters import format_quick_add_confirmation
from keyboards import get_quick_add_confirm_keyboard
from messages import (
    DATA_LOST,
    ERROR_GENERIC,
    QUICK_ADD_INVALID,
    QUICK_ADD_PREVIOUS_SAVED,
    SALE_ADDED_SUCCESS,
    SALE_CANCELLED,
    STALE_SALE_ALERT,
    SWAP_INVALID,
)

# Store parsed sale temporarily in user_data
PARSED_SALE_KEY = "parsed_sale"
# Message id of the confirmation that the pending sale belongs to
PARSED_MESSAGE_KEY = "parsed_sale_message_id"

# An empty inline keyboard is serialized as ``{}``, which is how Telegram is
# told to drop the buttons from a message.
EMPTY_KEYBOARD = InlineKeyboardMarkup([])


def _clear_pending(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forget the sale that was waiting for confirmation."""
    context.user_data.pop(PARSED_SALE_KEY, None)
    context.user_data.pop(PARSED_MESSAGE_KEY, None)


def _is_current_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    """
    Return whether a callback was pressed on the confirmation of the pending sale.

    Confirmations of already handled sales stay in the chat, so their buttons
    must not act on a newer pending sale.
    """
    query = update.callback_query
    pending_message_id = context.user_data.get(PARSED_MESSAGE_KEY)
    callback_message_id = getattr(query.message, "message_id", None)

    if pending_message_id is None or callback_message_id is None:
        return True
    return pending_message_id == callback_message_id


async def _retire_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parsed: ParsedSale
) -> None:
    """Turn an obsolete confirmation into a note that its sale was saved."""
    note = QUICK_ADD_PREVIOUS_SAVED.format(
        price=parsed.price,
        quantity=parsed.quantity,
        total=parsed.total
    )
    message_id = context.user_data.get(PARSED_MESSAGE_KEY)

    if message_id is None:
        await update.message.reply_text(note, parse_mode="HTML")
        return

    try:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text=note,
            parse_mode="HTML",
            reply_markup=EMPTY_KEYBOARD
        )
    except Exception:
        # The confirmation may be too old to edit; the note is informational.
        await update.message.reply_text(note, parse_mode="HTML")


async def _save_pending_sale(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    """
    Save the sale that is still waiting for confirmation.

    Returns whether a sale was saved. On a database failure the pending sale is
    left untouched so that it is not lost.
    """
    parsed: ParsedSale = context.user_data.get(PARSED_SALE_KEY)
    if not parsed:
        return False

    db_user = await get_or_create_user(update.effective_user.id)

    try:
        await add_sale(
            user_id=db_user["id"],
            cost=parsed.price,
            quantity=parsed.quantity,
            art=parsed.article
        )
    except Exception:
        return False

    await _retire_confirmation(update, context, parsed)
    _clear_pending(context)
    return True


async def handle_quick_add_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text input for quick sale addition."""
    text = update.message.text.strip()

    # Parse the input
    parsed = parse_quick_sale(text)

    if not parsed:
        await update.message.reply_text(QUICK_ADD_INVALID, parse_mode="HTML")
        return

    # A sale typed while an earlier one was still unanswered is saved instead of
    # being silently dropped.
    if context.user_data.get(PARSED_SALE_KEY) and not await _save_pending_sale(update, context):
        await update.message.reply_text(ERROR_GENERIC, parse_mode="HTML")
        return

    # Store parsed sale in context
    context.user_data[PARSED_SALE_KEY] = parsed

    # Show confirmation
    message = format_quick_add_confirmation(parsed)
    keyboard = get_quick_add_confirm_keyboard()

    sent = await update.message.reply_text(
        message,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    context.user_data[PARSED_MESSAGE_KEY] = sent.message_id


async def quick_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirm and save the quick sale."""
    query = update.callback_query

    if not _is_current_confirmation(update, context):
        await query.answer(STALE_SALE_ALERT, show_alert=True)
        return

    await query.answer()

    parsed: ParsedSale = context.user_data.get(PARSED_SALE_KEY)
    if not parsed:
        await query.edit_message_text(DATA_LOST, parse_mode="HTML")
        return

    user = update.effective_user
    db_user = await get_or_create_user(user.id)

    try:
        sale_id = await add_sale(
            user_id=db_user["id"],
            cost=parsed.price,
            quantity=parsed.quantity,
            art=parsed.article
        )

        # Clear parsed sale
        _clear_pending(context)

        await query.edit_message_text(
            SALE_ADDED_SUCCESS.format(sale_id=sale_id),
            parse_mode="HTML"
        )

        # Show default message after a moment
        from handlers.start import show_default_message
        await show_default_message(update, context)

    except Exception:
        await query.edit_message_text(ERROR_GENERIC, parse_mode="HTML")


async def quick_swap_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Swap price and quantity."""
    query = update.callback_query

    if not _is_current_confirmation(update, context):
        await query.answer(STALE_SALE_ALERT, show_alert=True)
        return

    parsed: ParsedSale = context.user_data.get(PARSED_SALE_KEY)
    if not parsed:
        await query.answer()
        await query.edit_message_text(DATA_LOST, parse_mode="HTML")
        return

    # Swapping is valid only when the current price can become an integer
    # quantity without truncating a decimal value.
    if not parsed.price.is_integer():
        await query.answer(SWAP_INVALID, show_alert=True)
        return

    await query.answer()

    new_price = float(parsed.quantity)
    new_quantity = int(parsed.price)

    # Create new parsed sale with swapped values
    swapped = ParsedSale(
        article=parsed.article,
        price=new_price,
        quantity=new_quantity
    )

    context.user_data[PARSED_SALE_KEY] = swapped

    # Show updated confirmation
    message = format_quick_add_confirmation(swapped)
    keyboard = get_quick_add_confirm_keyboard()

    await query.edit_message_text(
        message,
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def quick_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel quick sale addition."""
    query = update.callback_query

    if not _is_current_confirmation(update, context):
        await query.answer(STALE_SALE_ALERT, show_alert=True)
        return

    await query.answer()

    _clear_pending(context)

    await query.edit_message_text(
        SALE_CANCELLED,
        parse_mode="HTML"
    )

    # Show default message
    from handlers.start import show_default_message
    await show_default_message(update, context)


# Handlers
quick_add_text_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    handle_quick_add_text
)
quick_confirm_handler = CallbackQueryHandler(quick_confirm_callback, pattern="^quick_confirm$")
quick_swap_handler = CallbackQueryHandler(quick_swap_callback, pattern="^quick_swap$")
quick_cancel_handler = CallbackQueryHandler(quick_cancel_callback, pattern="^quick_cancel$")
