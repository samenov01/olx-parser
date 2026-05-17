import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from db import get_setting, set_setting

logging.getLogger("httpx").setLevel(logging.WARNING)


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


def _send_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я слежу за новыми объявлениями на OLX.\n\n"
        "Команды:\n"
        "/min 50000 — минимальная цена\n"
        "/max 200000 — максимальная цена\n"
        "/filter — текущие фильтры\n"
        "/pause — пауза\n"
        "/resume — возобновить\n"
        "/status — статус бота"
    )


async def cmd_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи цену: /min 50000")
        return
    try:
        val = int(context.args[0].replace(" ", ""))
        set_setting("price_min", val)
        await update.message.reply_text(f"✅ Минимальная цена: {val:,} ₸")
    except ValueError:
        await update.message.reply_text("Введи число, например: /min 50000")


async def cmd_max(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи цену: /max 200000")
        return
    try:
        val = int(context.args[0].replace(" ", ""))
        set_setting("price_max", val)
        await update.message.reply_text(f"✅ Максимальная цена: {val:,} ₸")
    except ValueError:
        await update.message.reply_text("Введи число, например: /max 200000")


async def cmd_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_min = get_setting("price_min", "0")
    price_max = get_setting("price_max", "0")
    paused = get_setting("paused", "0")

    min_text = f"{int(price_min):,} ₸" if int(price_min) else "не задана"
    max_text = f"{int(price_max):,} ₸" if int(price_max) else "не задана"
    status = "⏸ На паузе" if paused == "1" else "✅ Работает"

    await update.message.reply_text(
        f"📊 *Текущие фильтры:*\n\n"
        f"Минимум: {min_text}\n"
        f"Максимум: {max_text}\n"
        f"Статус: {status}",
        parse_mode="Markdown"
    )


async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_setting("paused", "1")
    await update.message.reply_text("⏸ Бот на паузе. Новые объявления не отслеживаются.")


async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_setting("paused", "0")
    await update.message.reply_text("▶️ Бот возобновил работу!")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    paused = get_setting("paused", "0")
    status = "⏸ На паузе" if paused == "1" else "✅ Работает"
    await update.message.reply_text(f"Статус: {status}")


def build_app() -> Application:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("min", cmd_min))
    app.add_handler(CommandHandler("max", cmd_max))
    app.add_handler(CommandHandler("filter", cmd_filter))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("status", cmd_status))
    return app
