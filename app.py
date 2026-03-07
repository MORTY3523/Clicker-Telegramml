import os
import logging
from flask import Flask, request
import telegram
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

if not TOKEN:
    logger.error("❌ TELEGRAM_TOKEN не найден!")
    exit(1)

# Создаём приложение бота
application = Application.builder().token(TOKEN).build()
app = Flask(__name__)

# ----- КЛАВИАТУРА -----
def main_keyboard():
    keyboard = [
        [KeyboardButton("⛏ Кликнуть"), KeyboardButton("👤 Профиль")],
        [KeyboardButton("🏪 Магазин"), KeyboardButton("🔧 Апгрейд")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ----- ОБРАБОТЧИКИ КОМАНД -----
async def start(update: Update, context):
    await update.message.reply_text(
        "👋 Добро пожаловать в кликер!\n\n"
        "/click — кликнуть\n"
        "/profile — профиль\n"
        "/shop — магазин\n"
        "/upgrade — апгрейд",
        reply_markup=main_keyboard()
    )

async def click(update: Update, context):
    await update.message.reply_text(
        "✅ +0.000001 алмаза",
        reply_markup=main_keyboard()
    )

async def profile(update: Update, context):
    await update.message.reply_text(
        "👤 Профиль\n"
        "└ Алмазы: 0.00000000\n"
        "└ Кликов: 0\n"
        "└ Уровень генератора: 0\n"
        "└ Доход: 0.00000 алм/3с",
        reply_markup=main_keyboard()
    )

async def shop(update: Update, context):
    await update.message.reply_text(
        "🏪 Магазин\n\n"
        "🔧 Улучшение генератора: 0.1 алмазов",
        reply_markup=main_keyboard()
    )

async def upgrade(update: Update, context):
    await update.message.reply_text(
        "❌ Не хватает алмазов",
        reply_markup=main_keyboard()
    )

# ----- ОБРАБОТЧИК КНОПОК -----
async def button_handler(update: Update, context):
    text = update.message.text
    if text == "⛏ Кликнуть":
        await click(update, context)
    elif text == "👤 Профиль":
        await profile(update, context)
    elif text == "🏪 Магазин":
        await shop(update, context)
    elif text == "🔧 Апгрейд":
        await upgrade(update, context)
    else:
        await update.message.reply_text(
            "Используй кнопки внизу",
            reply_markup=main_keyboard()
        )

# ----- РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ -----
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("click", click))
application.add_handler(CommandHandler("profile", profile))
application.add_handler(CommandHandler("shop", shop))
application.add_handler(CommandHandler("upgrade", upgrade))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

# ----- ВЕБХУК -----
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# ----- ПРОВЕРКА ЗДОРОВЬЯ -----
@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

# ----- УСТАНОВКА ВЕБХУКА -----
@app.route('/set_webhook')
def set_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    application.bot.set_webhook(url=webhook_url)
    return f"✅ Webhook set to {webhook_url}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
