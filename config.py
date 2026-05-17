import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

OLX_URL = "https://www.olx.kz/elektronika/telefony-i-aksesuary/mobilnye-telefony-smartfony/?search%5Border%5D=created_at%3Adesc&search%5Bregion_id%5D=9"

# Интервал опроса в секундах (по умолчанию 2 минуты)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "120"))

DB_PATH = "seen_listings.db"
