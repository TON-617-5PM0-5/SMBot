"""All bot messages in Ukrainian language."""

# --- General ---
WELCOME_MESSAGE = (
    "👋 Вітаю! Це ваш персональний менеджер продажів.\n"
    "Тут ви можете швидко додавати продажі та переглядати статистику."
)

# --- Start / Default Message ---
def get_default_message(
    day_sales: int,
    day_total: float,
    week_sales: int,
    week_total: float,
    month_sales: int,
    month_total: float,
    current_date: str,
    show_instruction: bool = True
) -> str:
    """Generate the default message shown on /start and after actions."""
    instruction = (
        "\n\n📝 <b>Швидке додавання продажу:</b>\n"
        "Просто напишіть у чат (Замість пропусків можливі '*'):\n"
        "• <code>ціна кількість</code> — напр. <code>150 2</code>\n"
        "• <code>артикул ціна кількість</code> — напр. <code>LED-001 150 2</code>\n"
        "• <code>кількість ціна</code> — напр. <code>2 150</code>\n"
        "• <code>артикул кількість ціна</code> — напр. <code>LED-001 2 150</code>\n"
        "• <code>ціна</code> — кількість = 1\n\n"
        "💡 <i>Ціна визначається автоматично: дробове число або більше значення.</i>"
        if show_instruction
        else ""
    )

    return (
        f"📊 <b>Статистика на {current_date}</b>\n\n"
        f"📅 <b>За сьогодні:</b> {day_sales} продаж(ів) | 💰 Продаж: {day_total:.2f} грн\n"
        f"📆 <b>За тиждень:</b> {week_sales} продаж(ів) | 💰 Продаж: {week_total:.2f} грн\n"
        f"🗓 <b>За місяць:</b> {month_sales} продаж(ів) | 💰 Продаж: {month_total:.2f} грн"
        f"{instruction}"
    )


HIDE_INSTRUCTION = "🙈 Приховати інструкцію"
SHOW_INSTRUCTION = "👁 Показати інструкцію"

# --- Main Menu ---
MAIN_MENU_TEXT = "🏠 <b>Головне меню</b>\nОберіть дію:"
BTN_VIEW_SALES = "📈 Перегляд продаж"
BTN_ADD_SALE = "➕ Додати продаж"
BTN_SEARCH = "🔍 Пошук товарів"
ADD_SALE_METHOD_PROMPT = "➕ <b>Додати продаж</b>\nОберіть спосіб додавання:"
QUICK_ADD_PROMPT = (
    "⚡ <b>Швидке додавання</b>\n"
    "Надішліть ціну та кількість, наприклад <code>150 2</code>.\n"
    "Для скасування використайте /start."
)

# --- Quick Add Sale ---
QUICK_ADD_PARSED = (
    "✅ <b>Додавання продажу:</b>\n"
    "{article_line}"
    "💰 Ціна: {price:.2f} грн\n"
    "📦 Кількість: {quantity}\n"
    "💵 Сума: {total:.2f} грн"
)

ARTICLE_LINE = "🏷 Артикул: {article}\n"

CONFIRM_SALE = "Все правильно ✅"
SWAP_PRICE_QTY = "🔄 Поміняти ціну та кількість"
CANCEL_SALE = "❌ Скасувати"
SWAP_INVALID = "❌ Неможливо поміняти місцями: ціна має дробове значення, а кількість повинна бути цілим числом."

SALE_ADDED_SUCCESS = "✅ Продаж успішно додано!\nID: {sale_id}"
SALE_CANCELLED = "❌ Додавання продажу скасовано."
QUICK_ADD_PREVIOUS_SAVED = (
    "💾 Попередній продаж збережено: {price:.2f} × {quantity} = {total:.2f} грн"
)
STALE_SALE_ALERT = "⚠️ Це підтвердження вже неактуальне."

# --- Guided Add Sale ---
GUIDED_ADD_START = "📝 <b>Послідовне додавання продажу</b>\nВведіть артикул або назву (або <code>-</code> для пропуску):"
GUIDED_ADD_ARTICLE = "Артикул/назва: {article}\nТепер введіть ціну:"
GUIDED_ADD_PRICE = "Артикул: {article}\nЦіна: {price:.2f} грн\nТепер введіть кількість:"
GUIDED_ADD_QUANTITY = (
    "Артикул: {article}\n"
    "Ціна: {price:.2f} грн\n"
    "Кількість: {quantity}\n"
    "Сума: {total:.2f} грн\n\n"
    "Підтвердити?"
)

GUIDED_CONFIRM = "✅ Підтвердити"
GUIDED_CANCEL = "❌ Скасувати"

INVALID_PRICE = "❌ Некоректна ціна. Введіть число (напр. 150 або 150.50):"
INVALID_QUANTITY = "❌ Некоректна кількість. Введіть ціле число (напр. 2):"

# --- View Sales ---
VIEW_PERIOD_DAY = "📅 Сьогодні"
VIEW_PERIOD_WEEK = "📆 Тиждень"
VIEW_PERIOD_MONTH = "🗓 Місяць"
VIEW_PERIOD_YEAR = "📊 Рік"

SALES_VIEW_TITLE = "📈 <b>Продажі за {period}</b>"
BREAKDOWN_BY_DAYS = "📅 <b>Підсумок по днях:</b>"
BREAKDOWN_BY_MONTHS = "🗓 <b>Підсумок по місяцях:</b>"
BREAKDOWN_LINE = "• {period}: {count} продаж(ів) | {total:.2f} грн"
RECORDS_TITLE = "📋 <b>Записи:</b>"
SALES_VIEW_HINT = "💡 Введіть ID продажу, щоб редагувати або видалити його."

NO_SALES_FOUND = "📭 Продажів за цей період не знайдено."

SALE_ITEM_TEMPLATE = (
    "🆔 ID: <code>{sale_id}</code>\n"
    "{article_line}"
    "💰 Ціна: {price:.2f} грн | 📦 К-сть: {quantity} | 💵 Сума: {total:.2f} грн\n"
    "🕐 {date}\n"
    "──────────────────"
)

PAGINATION_PREV = "⬅️ Назад"
PAGINATION_NEXT = "Вперед ➡️"
PAGINATION_INFO = "Сторінка {current}/{total}"

# --- Edit/Delete ---
SALE_DETAILS_FOR_EDIT = (
    "📋 <b>Продаж ID: {sale_id}</b>\n"
    "{article_line}"
    "💰 Ціна: {price:.2f} грн\n"
    "📦 Кількість: {quantity}\n"
    "💵 Сума: {total:.2f} грн\n"
    "🕐 {date}\n\n"
    "Оберіть дію:"
)

BTN_EDIT_SALE = "✏️ Редагувати"
BTN_DELETE_SALE = "🗑 Видалити"
BTN_BACK_TO_LIST = "⬅️ Назад до списку"

EDIT_CHOOSE_FIELD = "Що бажаєте змінити?"
BTN_EDIT_ARTICLE = "🏷 Артикул"
BTN_EDIT_PRICE = "💰 Ціну"
BTN_EDIT_QUANTITY = "📦 Кількість"

EDIT_ARTICLE_PROMPT = "Введіть новий артикул (або <code>-</code> для очищення):"
EDIT_PRICE_PROMPT = "Введіть нову ціну:"
EDIT_QUANTITY_PROMPT = "Введіть нову кількість:"

SALE_UPDATED = "✅ Продаж оновлено!"
SALE_DELETED = "✅ Продаж видалено!"
DELETE_CONFIRM = "⚠️ Ви впевнені, що хочете видалити цей продаж?"
DELETE_YES = "✅ Так, видалити"
DELETE_NO = "❌ Ні, скасувати"

# --- Search ---
SEARCH_PROMPT = (
    "🔍 <b>Пошук товарів</b>\n"
    "Введіть артикул, назву або ціну для пошуку:"
)

SEARCH_RESULTS_TITLE = "🔍 <b>Результати пошуку: {query}</b>"
SEARCH_NO_RESULTS = "📭 Нічого не знайдено за запитом: <code>{query}</code>"

SEARCH_RESULT_ITEM = (
    "🏷 Артикул/назва: {article}\n"
    "💰 Ціна: {price:.2f} грн\n"
    "📦 Продажів: {count} | 💵 Сума: {total:.2f} грн\n"
    "──────────────────"
)

# --- Errors ---
ERROR_GENERIC = "❌ Сталася помилка. Спробуйте ще раз."
ERROR_NOT_FOUND = "❌ Продаж не знайдено."
ERROR_DB = "❌ Помилка бази даних. Зверніться до розробника."
DATA_LOST = "❌ Дані втрачено. Спробуйте ще раз."
INVALID_ID = "❌ Введіть коректний числовий ID."
EDIT_FIELD_PROMPT = "Що бажаєте змінити?"
CANCELLED = "❌ Скасовано."
SEARCH_EMPTY = "❌ Введіть запит для пошуку."
QUICK_ADD_INVALID = (
    "❌ Не вдалося розпізнати формат. Спробуйте:\n"
    "• <code>150 2</code> — ціна 150, кількість 2\n"
    "• <code>LED-001 150 2</code> — артикул, ціна, кількість\n"
    "• <code>2 150</code> — кількість 2, ціна 150\n"
    "• <code>150</code> — ціна 150, кількість 1"
)
VIEW_SALES_PROMPT = "📈 <b>Перегляд продаж</b>\nОберіть період:"
BACK_TO_MENU = "⬅️ До меню"
BACK_TO_SALES_LIST = "⬅️ Назад до списку"
ADD_QUICK_METHOD = "⚡ Швидке додавання (текстом)"
ADD_GUIDED_METHOD = "📝 Послідовне додавання"