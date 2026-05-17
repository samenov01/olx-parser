import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

OLX_URL = "https://www.olx.kz/elektronika/telefony-i-aksesuary/mobilnye-telefony-smartfony/?search%5Border%5D=created_at%3Adesc&search%5Bregion_id%5D=9"

# Интервал опроса в секундах (по умолчанию 2 минуты)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "120"))

# Фильтр по цене (0 = отключён)
PRICE_MIN = int(os.getenv("PRICE_MIN", "0"))
PRICE_MAX = int(os.getenv("PRICE_MAX", "0"))

DB_PATH = "seen_listings.db"
