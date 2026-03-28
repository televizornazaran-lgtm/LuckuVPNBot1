import json
import random
from datetime import datetime, timedelta

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8381559075:AAE2zuxEzrJfn0W_Cy-BNbiIQj2jw1_M0AM"

KEYS_FILE = "keys.txt"
USERS_FILE = "users.json"


# 📌 Главное меню
def main_menu():
    keyboard = [
        ["🔑 Получить VPN ключ"],
        ["📊 Мои ключи"],
        ["📞 Поддержка"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# 📌 Работа с пользователями
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# 📌 Выдача ключа
def get_key(user_id):
    users = load_users()

    with open(KEYS_FILE, "r") as f:
        keys = f.read().splitlines()

    if user_id not in users:
        users[user_id] = {
            "keys": [],
            "free_until": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        }

    available_keys = list(set(keys) - set(users[user_id]["keys"]))

    if not available_keys:
        return None

    key = random.choice(available_keys)
    users[user_id]["keys"].append(key)
    save_users(users)

    return key, users[user_id]["free_until"]


# 📌 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💎 Lucky VPN – быстрый и стабильный сервис\n\n"
        "📲 Нажмите кнопку ниже, чтобы получить VPN ключ\n\n"
        "📞 Поддержка: @lucky_vpn_support"
    )
    await update.message.reply_text(text, reply_markup=main_menu())


# 📌 Обработка кнопок
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.message.from_user.id)

    # 🔑 Получить ключ
    if text == "🔑 Получить VPN ключ":
        result = get_key(user_id)

        if result:
            key, date = result
            await update.message.reply_text(
                f"🔑 Ваш ключ:\n{key}\n\n📅 Бесплатно до: {date}"
            )
        else:
            await update.message.reply_text("❌ Ключи закончились")

    # 📊 Мои ключи
    elif text == "📊 Мои ключи":
        users = load_users()

        if user_id in users:
            keys = users[user_id]["keys"]
            date = users[user_id]["free_until"]

            await update.message.reply_text(
                f"🔑 Ваши ключи:\n{', '.join(keys)}\n\n📅 Бесплатно до: {date}"
            )
        else:
            await update.message.reply_text("У вас пока нет ключей")

    # 📞 Поддержка
    elif text == "📞 Поддержка":
        await update.message.reply_text("📞 Напишите: @lucky_vpn_support")

    else:
        await update.message.reply_text("Используйте кнопки меню 👇", reply_markup=main_menu())


# 📌 Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Бот запущен...")
    app.run_polling()
