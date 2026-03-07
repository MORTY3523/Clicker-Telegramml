import os
import logging
from flask import Flask, request
import telegram
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# Инициализация бота и Flask
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# Клавиатура с кнопками
def main_keyboard():
    keyboard = [
        [KeyboardButton("⛏ Кликнуть"), KeyboardButton("👤 Профиль")],
        [KeyboardButton("🏪 Магазин"), KeyboardButton("🔧 Апгрейд")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Обработчики команд
def start(update, context):
    update.message.reply_text(
        "👋 Добро пожаловать в кликер!\n\n"
        "/click — кликнуть\n"
        "/profile — профиль\n"
        "/shop — магазин\n"
        "/upgrade — апгрейд",
        reply_markup=main_keyboard()
    )

def click(update, context):
    update.message.reply_text(
        "✅ +0.000001 алмаза",
        reply_markup=main_keyboard()
    )

def profile(update, context):
    update.message.reply_text(
        "👤 Профиль\n"
        "└ Алмазы: 0.00000000\n"
        "└ Кликов: 0\n"
        "└ Уровень генератора: 0\n"
        "└ Доход: 0.00000 алм/3с",
        reply_markup=main_keyboard()
    )

def shop(update, context):
    update.message.reply_text(
        "🏪 Магазин\n\n"
        "🔧 Улучшение генератора: 0.1 алмазов",
        reply_markup=main_keyboard()
    )

def upgrade(update, context):
    update.message.reply_text(
        "❌ Не хватает алмазов",
        reply_markup=main_keyboard()
    )

# Обработчик кнопок
def button_handler(update, context):
    text = update.message.text
    if text == "⛏ Кликнуть":
        click(update, context)
    elif text == "👤 Профиль":
        profile(update, context)
    elif text == "🏪 Магазин":
        shop(update, context)
    elif text == "🔧 Апгрейд":
        upgrade(update, context)
    else:
        update.message.reply_text(
            "Используй кнопки внизу",
            reply_markup=main_keyboard()
        )

# Настройка диспетчера
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("click", click))
dispatcher.add_handler(CommandHandler("profile", profile))
dispatcher.add_handler(CommandHandler("shop", shop))
dispatcher.add_handler(CommandHandler("upgrade", upgrade))
dispatcher.add_handler(MessageHandler(Filters.text, button_handler))

# Вебхук
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Проверка здоровья
@app.route('/')
def home():
    return "Bot is running!", 200

# Установка вебхука (вызвать один раз)
@app.route('/set_webhook')
def set_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    bot.set_webhook(url=webhook_url)
    return f"Webhook set to {webhook_url}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
