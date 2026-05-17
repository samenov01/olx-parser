import re
import time
import sys
from datetime import datetime

from config import OLX_URL, POLL_INTERVAL, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PRICE_MIN, PRICE_MAX
from db import init_db, is_seen, mark_seen
from olx import fetch_listings, get_phone
from telegram_bot import send_notification


def _extract_price(price_str: str) -> int | None:
    digits = re.sub(r"\D", "", price_str)
    return int(digits) if digits else None


def check_config():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Заполните TELEGRAM_TOKEN и TELEGRAM_CHAT_ID в файле .env")
        sys.exit(1)


def seed_db():
    """Первый запуск: сохраняет все текущие объявления как виденные без уведомлений."""
    listings = fetch_listings(OLX_URL)
    count = 0
    for listing in listings:
        if not is_seen(listing["id"]):
            mark_seen(listing["id"])
            count += 1
    print(f"[INIT] Сохранено {count} существующих объявлений. Уведомления только о новых.")
    return count


def is_db_empty() -> bool:
    import sqlite3
    from config import DB_PATH
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT COUNT(*) FROM seen").fetchone()
        return row[0] == 0


def run_once():
    listings = fetch_listings(OLX_URL)
    new_count = 0

    for listing in listings:
        lid = listing["id"]

        # Пропускаем старые объявления (не сегодняшние)
        posted = listing.get("posted_date", "")
        if posted and "сегодня" not in posted:
            mark_seen(lid)  # запоминаем чтобы больше не проверять
            continue

        if is_seen(lid):
            continue

        # Фильтр по цене
        price_num = _extract_price(listing.get("price", ""))
        if PRICE_MIN and price_num and price_num < PRICE_MIN:
            mark_seen(lid)
            continue
        if PRICE_MAX and price_num and price_num > PRICE_MAX:
            mark_seen(lid)
            continue

        mark_seen(lid)
        print(f"[NEW] {listing['title']} — {listing['price']} | {listing['url']}")

        phone = get_phone(lid)
        if phone:
            print(f"      Телефон: {phone}")
        else:
            print("      Телефон: не удалось получить")

        send_notification(listing, phone)
        new_count += 1

        time.sleep(2)

    return new_count, len(listings)


def main():
    check_config()
    init_db()

    print(f"OLX Parser запущен. Интервал: {POLL_INTERVAL}с | URL: {OLX_URL}")
    print("Нажмите Ctrl+C для остановки.\n")

    if is_db_empty():
        seed_db()

    while True:
        now = datetime.now().strftime("%H:%M:%S")
        try:
            new_count, total = run_once()
            print(f"[{now}] Проверено: {total} объявлений, новых: {new_count}")
        except KeyboardInterrupt:
            print("\nОстановлено.")
            break
        except Exception as e:
            print(f"[{now}] [ERROR] {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
