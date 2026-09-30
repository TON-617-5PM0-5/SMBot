"""Sales view: paginated browsing with inline edit/delete by sale ID."""
from datetime import datetime
from html import escape

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)

from database import (
    get_or_create_user,
    get_sales_breakdown,
    get_sales_list,
    get_sale_by_id,
    update_sale,
    delete_sale,
)
from keyboards import (
    get_sales_period_keyboard,
    get_sales_pagination_keyboard,
    get_edit_delete_keyboard,
    get_edit_field_keyboard,
    get_delete_confirm_keyboard,
    get_add_sale_method_keyboard,
)
from messages import (
    ADD_SALE_METHOD_PROMPT,
    ARTICLE_LINE,
    BREAKDOWN_BY_DAYS,
    BREAKDOWN_BY_MONTHS,
    BREAKDOWN_LINE,
    DATA_LOST,
    DELETE_CONFIRM,
    EDIT_ARTICLE_PROMPT,
    EDIT_FIELD_PROMPT,
    EDIT_PRICE_PROMPT,
    EDIT_QUANTITY_PROMPT,
    ERROR_GENERIC,
    ERROR_NOT_FOUND,
    INVALID_ID,
    INVALID_PRICE,
    INVALID_QUANTITY,
    NO_SALES_FOUND,
    RECORDS_TITLE,
    SALE_DELETED,
    SALE_DETAILS_FOR_EDIT,
    SALE_UPDATED,
    SALES_VIEW_HINT,
    SALES_VIEW_TITLE,
    VIEW_PERIOD_DAY,
    VIEW_PERIOD_MONTH,
    VIEW_PERIOD_WEEK,
    VIEW_PERIOD_YEAR,
    VIEW_SALES_PROMPT,
)
from utils.formatters import format_sale_item, format_datetime
from utils.helpers import is_valid_price, is_valid_quantity
from config import ITEMS_PER_PAGE


# Conversation states
SALES_VIEW, SALE_DETAILS, EDIT_FIELD, EDIT_VALUE, DELETE_CONFIRM_STATE = range(5)

# User data keys
SALES_PERIOD_KEY = "sales_period"
SALES_PAGE_KEY = "sales_page"
EDIT_SALE_ID_KEY = "edit_sale_id"
EDIT_FIELD_KEY = "edit_field"

# A message that consists only of a number is treated as a sale ID.
SALE_ID_FILTER = filters.TEXT & ~filters.COMMAND & filters.Regex(r"^\s*\d+\s*$")

PERIOD_NAMES = {
    "day": VIEW_PERIOD_DAY,
    "week": VIEW_PERIOD_WEEK,
    "month": VIEW_PERIOD_MONTH,
    "year": VIEW_PERIOD_YEAR,
}


# --- Browsing ---

async def sales_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the period selection menu."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        VIEW_SALES_PROMPT,
        parse_mode="HTML",
        reply_markup=get_sales_period_keyboard(),
    )
    return SALES_VIEW


async def sales_period_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the first page of the selected period."""
    query = update.callback_query
    await query.answer()

    period = query.data.replace("sales_", "")
    await _render_page(query, context, period, page=0)
    return SALES_VIEW


async def sales_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pagination for the sales view."""
    query = update.callback_query
    await query.answer()

    # Callback data is "sales_page_<n>"; the period is remembered in user data.
    page = int(query.data.split("_")[2])
    period = context.user_data.get(SALES_PERIOD_KEY)
    if not period:
        return await sales_menu_callback(update, context)

    await _render_page(query, context, period, page)
    return SALES_VIEW


async def _render_page(query, context: ContextTypes.DEFAULT_TYPE, period: str, page: int) -> None:
    """Fetch and display a sales page, clamping the page to the available range."""
    db_user = await get_or_create_user(query.from_user.id)

    result = await get_sales_list(db_user["id"], period, page=page, per_page=ITEMS_PER_PAGE)
    total_pages = result["total_pages"]
    if total_pages and page > total_pages - 1:
        # The requested page may no longer exist (e.g. items were deleted).
        page = total_pages - 1
        result = await get_sales_list(db_user["id"], period, page=page, per_page=ITEMS_PER_PAGE)

    breakdown = await get_sales_breakdown(db_user["id"], period)

    context.user_data[SALES_PERIOD_KEY] = period
    context.user_data[SALES_PAGE_KEY] = page

    await _show_sales_page(query, result, period, page, breakdown)


async def _show_sales_page(
    query,
    result: dict,
    period: str,
    page: int,
    breakdown: list[dict] | None = None,
) -> None:
    """Display a page of sales."""
    sales = result["sales"]
    total_pages = result["total_pages"]
    total_count = result["total_count"]

    period_name = PERIOD_NAMES.get(period, period)

    if not sales:
        message = f"{SALES_VIEW_TITLE.format(period=period_name)}\n\n{NO_SALES_FOUND}"
    else:
        message = f"{SALES_VIEW_TITLE.format(period=period_name)} (всього: {total_count})\n\n"
        if page == 0 and breakdown:
            message += _format_breakdown(breakdown, period) + "\n\n"
        message += RECORDS_TITLE + "\n"
        for sale in sales:
            message += format_sale_item(sale) + "\n"

    message += f"\n{SALES_VIEW_HINT}"

    keyboard = get_sales_pagination_keyboard(page, total_pages)
    await query.edit_message_text(message, parse_mode="HTML", reply_markup=keyboard)


def _format_breakdown(breakdown: list[dict], period: str) -> str:
    """Format daily or monthly totals for the selected period."""
    if period == "day" or not breakdown:
        return ""

    title = BREAKDOWN_BY_MONTHS if period == "year" else BREAKDOWN_BY_DAYS
    lines = [title]
    for item in breakdown:
        key = item["period_key"]
        if period == "year":
            display_key = datetime.strptime(key, "%Y-%m").strftime("%m.%Y")
        else:
            display_key = datetime.strptime(key, "%Y-%m-%d").strftime("%d.%m.%Y")
        lines.append(
            BREAKDOWN_LINE.format(
                period=display_key,
                count=item["count"],
                total=item["total"],
            )
        )
    return "\n".join(lines)


async def sales_back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Leave the sales view and end the conversation."""
    query = update.callback_query
    await query.answer()

    from handlers.start import show_default_message
    await show_default_message(update, context)
    return ConversationHandler.END


async def sales_go_add_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Leave the sales view for the add-sale menu and end the conversation."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        ADD_SALE_METHOD_PROMPT,
        parse_mode="HTML",
        reply_markup=get_add_sale_method_keyboard(),
    )
    return ConversationHandler.END


# --- Edit / Delete ---

async def sales_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Open a sale for editing/deleting when its ID is typed while browsing."""
    text = update.message.text.strip()

    try:
        sale_id = int(text)
    except ValueError:
        await update.message.reply_text(INVALID_ID, parse_mode="HTML")
        return SALES_VIEW

    db_user = await get_or_create_user(update.effective_user.id)
    sale = await get_sale_by_id(sale_id, db_user["id"])
    if not sale:
        await update.message.reply_text(ERROR_NOT_FOUND, parse_mode="HTML")
        return SALES_VIEW

    context.user_data[EDIT_SALE_ID_KEY] = sale_id
    await _show_sale_details(update, sale)
    return SALE_DETAILS


async def _show_sale_details(update: Update, sale: dict) -> None:
    """Show sale details with the edit/delete keyboard."""
    article_line = ""
    if sale.get("art"):
        article_line = ARTICLE_LINE.format(article=escape(str(sale["art"])))

    message = SALE_DETAILS_FOR_EDIT.format(
        sale_id=sale["id"],
        article_line=article_line,
        price=sale["cost"],
        quantity=sale["quantity"],
        total=sale["total_cost"],
        date=format_datetime(sale["date_of_creation"]),
    )

    keyboard = get_edit_delete_keyboard()
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(message, parse_mode="HTML", reply_markup=keyboard)


async def edit_sale_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the field selection keyboard."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        EDIT_FIELD_PROMPT,
        parse_mode="HTML",
        reply_markup=get_edit_field_keyboard(),
    )
    return EDIT_FIELD


async def edit_field_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle field selection for editing."""
    query = update.callback_query
    await query.answer()

    field = query.data.replace("edit_field_", "")  # art, cost, qty
    context.user_data[EDIT_FIELD_KEY] = field

    prompts = {
        "art": EDIT_ARTICLE_PROMPT,
        "cost": EDIT_PRICE_PROMPT,
        "qty": EDIT_QUANTITY_PROMPT,
    }

    await query.edit_message_text(prompts.get(field, EDIT_PRICE_PROMPT), parse_mode="HTML")
    return EDIT_VALUE


async def back_to_sale_details_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to the sale details from the field selection."""
    query = update.callback_query
    await query.answer()

    sale_id = context.user_data.get(EDIT_SALE_ID_KEY)
    if not sale_id:
        await query.edit_message_text(DATA_LOST, parse_mode="HTML")
        return ConversationHandler.END

    db_user = await get_or_create_user(update.effective_user.id)
    sale = await get_sale_by_id(sale_id, db_user["id"])
    if not sale:
        await query.edit_message_text(ERROR_NOT_FOUND, parse_mode="HTML")
        return ConversationHandler.END

    await _show_sale_details(update, sale)
    return SALE_DETAILS


async def back_to_sales_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return from the sale details to the sales list."""
    query = update.callback_query
    await query.answer()

    period = context.user_data.get(SALES_PERIOD_KEY)
    if not period:
        return await sales_menu_callback(update, context)

    page = context.user_data.get(SALES_PAGE_KEY, 0)
    await _render_page(query, context, period, page)
    return SALES_VIEW


async def edit_value_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Apply the new value for the selected field."""
    text = update.message.text.strip()
    field = context.user_data.get(EDIT_FIELD_KEY)
    sale_id = context.user_data.get(EDIT_SALE_ID_KEY)

    if not field or not sale_id:
        await update.message.reply_text(DATA_LOST, parse_mode="HTML")
        return ConversationHandler.END

    db_user = await get_or_create_user(update.effective_user.id)

    if field == "art":
        new_art = None if text == "-" else text
        success = await update_sale(sale_id, db_user["id"], art=new_art)

    elif field == "cost":
        if not is_valid_price(text):
            await update.message.reply_text(INVALID_PRICE, parse_mode="HTML")
            return EDIT_VALUE
        success = await update_sale(sale_id, db_user["id"], cost=float(text.replace(",", ".")))

    elif field == "qty":
        if not is_valid_quantity(text):
            await update.message.reply_text(INVALID_QUANTITY, parse_mode="HTML")
            return EDIT_VALUE
        success = await update_sale(sale_id, db_user["id"], quantity=int(text))

    else:
        await update.message.reply_text(ERROR_GENERIC, parse_mode="HTML")
        return ConversationHandler.END

    if success:
        await update.message.reply_text(SALE_UPDATED, parse_mode="HTML")
    else:
        await update.message.reply_text(ERROR_GENERIC, parse_mode="HTML")

    _clear_sale_keys(context)

    from handlers.start import show_default_message
    await show_default_message(update, context)
    return ConversationHandler.END


async def delete_sale_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for confirmation before deleting."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        DELETE_CONFIRM,
        parse_mode="HTML",
        reply_markup=get_delete_confirm_keyboard(),
    )
    return DELETE_CONFIRM_STATE


async def delete_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete the sale after confirmation."""
    query = update.callback_query
    await query.answer()

    sale_id = context.user_data.get(EDIT_SALE_ID_KEY)
    if not sale_id:
        await query.edit_message_text(DATA_LOST, parse_mode="HTML")
        return ConversationHandler.END

    db_user = await get_or_create_user(update.effective_user.id)
    success = await delete_sale(sale_id, db_user["id"])

    _clear_sale_keys(context)

    if success:
        await query.edit_message_text(SALE_DELETED, parse_mode="HTML")
    else:
        await query.edit_message_text(ERROR_GENERIC, parse_mode="HTML")

    from handlers.start import show_default_message
    await show_default_message(update, context)
    return ConversationHandler.END


async def delete_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel deletion and return to the sale details."""
    query = update.callback_query
    await query.answer()

    sale_id = context.user_data.get(EDIT_SALE_ID_KEY)
    if not sale_id:
        await query.edit_message_text(DATA_LOST, parse_mode="HTML")
        return ConversationHandler.END

    db_user = await get_or_create_user(update.effective_user.id)
    sale = await get_sale_by_id(sale_id, db_user["id"])
    if not sale:
        await query.edit_message_text(ERROR_NOT_FOUND, parse_mode="HTML")
        return ConversationHandler.END

    await _show_sale_details(update, sale)
    return SALE_DETAILS


def _clear_sale_keys(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Drop the per-sale user data keys."""
    context.user_data.pop(EDIT_SALE_ID_KEY, None)
    context.user_data.pop(EDIT_FIELD_KEY, None)


async def sales_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel via the /cancel command."""
    _clear_sale_keys(context)

    from handlers.start import show_default_message
    await show_default_message(update, context)
    return ConversationHandler.END


# Conversation handler
sales_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(sales_menu_callback, pattern="^menu_view_sales$"),
    ],
    states={
        SALES_VIEW: [
            CallbackQueryHandler(sales_period_callback, pattern="^sales_(day|week|month|year)$"),
            CallbackQueryHandler(sales_page_callback, pattern="^sales_page_\\d+$"),
            CallbackQueryHandler(sales_go_add_callback, pattern="^menu_add_sale$"),
            CallbackQueryHandler(sales_back_to_menu_callback, pattern="^back_to_main$"),
            MessageHandler(SALE_ID_FILTER, sales_id_input),
        ],
        SALE_DETAILS: [
            CallbackQueryHandler(edit_sale_callback, pattern="^edit_sale$"),
            CallbackQueryHandler(delete_sale_callback, pattern="^delete_sale$"),
            CallbackQueryHandler(back_to_sales_list_callback, pattern="^back_to_sales_list$"),
        ],
        EDIT_FIELD: [
            CallbackQueryHandler(edit_field_callback, pattern="^edit_field_(art|cost|qty)$"),
            CallbackQueryHandler(back_to_sale_details_callback, pattern="^back_to_sale_details$"),
        ],
        EDIT_VALUE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_value_handler),
        ],
        DELETE_CONFIRM_STATE: [
            CallbackQueryHandler(delete_confirm_callback, pattern="^delete_confirm$"),
            CallbackQueryHandler(delete_cancel_callback, pattern="^delete_cancel$"),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", sales_cancel_command),
    ],
    allow_reentry=True,
    per_message=False,
)
