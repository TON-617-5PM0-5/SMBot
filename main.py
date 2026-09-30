"""SalesManagmentBot - Main entry point."""
import asyncio
import logging
from telegram.ext import Application, ApplicationBuilder
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Local imports
from config import TG_BOT_API_KEY
from database import init_database, close_connection
from handlers import (
    start_handler,
    toggle_instruction_handler,
    back_to_main_handler,
    add_sale_menu_handler,
    quick_add_menu_handler,
    quick_add_text_handler,
    quick_confirm_handler,
    quick_swap_handler,
    quick_cancel_handler,
    guided_add_conversation,
    sales_conversation,
    search_conversation,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Initialize database on startup."""
    await init_database()
    logger.info("Database initialized")


async def post_shutdown(application: Application) -> None:
    """Close database connection on shutdown."""
    await close_connection()
    logger.info("Database connection closed")


def main() -> None:
    """Main function to run the bot."""
    if not TG_BOT_API_KEY or ":" not in TG_BOT_API_KEY:
        logger.error(
            "TG_BOT_API_KEY is missing or has an invalid format. "
            "Set the token from @BotFather in .env."
        )
        return

    # Build application
    application = (
        ApplicationBuilder()
        .token(TG_BOT_API_KEY)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Add handlers in order of priority

    # 1. Conversation handlers (must be added before generic handlers).
    # The sales conversation is registered after the other conversations so
    # that their text input takes priority over its sale-ID handling.
    application.add_handler(guided_add_conversation)
    application.add_handler(search_conversation)
    application.add_handler(sales_conversation)

    # 2. Command handlers
    application.add_handler(start_handler)

    # 3. Callback query handlers (specific patterns first)
    application.add_handler(toggle_instruction_handler)
    application.add_handler(back_to_main_handler)
    application.add_handler(add_sale_menu_handler)
    application.add_handler(quick_add_menu_handler)

    # Quick add callbacks
    application.add_handler(quick_confirm_handler)
    application.add_handler(quick_swap_handler)
    application.add_handler(quick_cancel_handler)

    # View sales (browsing + edit/delete) is handled by sales_conversation above.

    # 4. Text message handler for quick add (lowest priority)
    application.add_handler(quick_add_text_handler)

    # Run the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()