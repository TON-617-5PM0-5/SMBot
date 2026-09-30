"""Configuration module for SalesManagmentBot."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "sales.db"

# Telegram Bot API
TG_BOT_API_KEY = os.getenv("TG_BOT_API_KEY", "")

# Business constants
DEFAULT_QUANTITY = 1

# Pagination
ITEMS_PER_PAGE = 10

# Date formats
DATE_FORMAT = "%d.%m.%Y"
DATETIME_FORMAT = "%d.%m.%Y %H:%M"