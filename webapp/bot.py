import json
import random
from datetime import datetime, timedelta
import threading

from flask import Flask, request, jsonify, send_from_directory
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 🔑 ВСТАВЬ СВОЙ ТОКЕН
TOKEN = "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"

# 👤 ВСТАВЬ СВОЙ ID
ADMIN_ID = "8042916047"

# 🌐 URL Railway
WEB_URL = "https://luckuvpnbot1-production.up.railway.app"

KEYS_FILE = "keys.txt"
USERS_FILE = "users.json"


# ===== Работа с пользователями =====
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ===== Получение ключа =====
def get_key(user_id):
    users = load_users()

    try:
        with open(KEYS_FILE, "r") as f:
            keys = f.read().splitlines()
    except:
        keys = []

    if user_id not in users:
        users[user_id] = {
            "keys": [],
            "free_until": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        }

    free_until = datetime.strptime(users[user_id]["free_until"], "%Y-%m-%d")

    if datetime.now() > free_until:
        return "expired", None

    available = list(set(keys) - set(users[user_id]["keys"]))

    if not available:
        return "no_keys", None

    key = random.choice(available)
    users[user_id]["keys"].append(key)

    save_users(users)

    return key, users[user_id]["free_until"]


# ===== TELEGRAM БОТ =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💎 Lucky VPN\n\n"
        "🚀 Быстрый и стабильный VPN\n\n"
        "🎁 4 дня бесплатно\n\n"
        "👇 Откройте приложение"
    )

    keyboard = [
        [InlineKeyboardButton("🌐 Открыть приложение", web_app=WebAppInfo(url=WEB_URL))]
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используйте кнопку 👇",)


# ===== АДМИНКА =====
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) != ADMIN_ID:
        return

    users = load_users()
    total_keys = sum(len(u["keys"]) for u in users.values())

    await update.message.reply_text(
        f"👤 Пользователей: {len(users)}\n🔑 Выдано ключей: {total_keys}"
    )


# ===== FLASK WEB APP =====
flask_app = Flask(__name__, static_folder="webapp")


@flask_app.route("/")
def index():
    return send_from_directory("webapp", "index.html")


@flask_app.route("/user")
def user():
    user_id = request.args.get("user_id")
    users = load_users()

    if user_id not in users:
        users[user_id] = {"keys": [], "free_until": "нет"}
        save_users(users)

    return jsonify(users[user_id])


@flask_app.route("/get_key")
def api_key():
    user_id = request.args.get("user_id")
    result = get_key(user_id)

    if result[0] in ["expired", "no_keys"]:
        return jsonify({"error": result[0]})

    users = load_users()
    return jsonify(users[user_id])


def run_web():
    flask_app.run(host="0.0.0.0", port=5000)


# ===== ЗАПУСК =====
if __name__ == "__main__":
    threading.Thread(target=run_web).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🚀 Бот + WebApp запущены")
    app.run_polling()
