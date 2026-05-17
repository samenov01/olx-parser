import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_notification(listing: dict, phone: str | None):
    phone_line = f"📞 *Телефон:* `{phone}`" if phone else "📞 _Номер скрыт (нажмите в объявлении)_"

    text = (
        f"🆕 *Новое объявление на OLX*\n\n"
        f"📱 *{listing['title']}*\n"
        f"💰 {listing['price']}\n"
        f"{phone_line}\n"
        f"🔗 [Открыть объявление]({listing['url']})"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if not resp.ok:
            print(f"[WARN] Telegram ответил {resp.status_code}: {resp.text}")
    except requests.RequestException as e:
        print(f"[ERROR] Ошибка отправки в Telegram: {e}")
