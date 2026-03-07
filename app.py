import os
import json
import logging
from flask import Flask, request, jsonify
import telegram
from telegram import ReplyKeyboardMarkup, KeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# Клавиатура с кнопками
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("⛏ Кликнуть"), KeyboardButton("👤 Профиль")],
        [KeyboardButton("🏪 Магазин"), KeyboardButton("🔧 Апгрейд")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Обработка команд и кнопок
def handle_message(update):
    chat_id = update.message.chat.id
    text = update.message.text
    
    # Команды
    if text == '/start':
        bot.send_message(
            chat_id=chat_id,
            text="👋 Добро пожаловать в кликер!\nИспользуй кнопки ниже.",
            reply_markup=get_main_keyboard()
        )
    elif text == '/click' or text == "⛏ Кликнуть":
        bot.send_message(
            chat_id=chat_id,
            text="✅ +0.000001 алмаза",
            reply_markup=get_main_keyboard()
        )
    elif text == '/profile' or text == "👤 Профиль":
        bot.send_message(
            chat_id=chat_id,
            text="👤 Профиль\n└ Алмазы: 0.00000000\n└ Кликов: 0\n└ Уровень генератора: 0\n└ Доход: 0.00000 алм/3с",
            reply_markup=get_main_keyboard()
        )
    elif text == '/shop' or text == "🏪 Магазин":
        bot.send_message(
            chat_id=chat_id,
            text="🏪 Магазин\n\n🔧 Улучшение генератора: 0.1 алмазов",
            reply_markup=get_main_keyboard()
        )
    elif text == '/upgrade' or text == "🔧 Апгрейд":
        bot.send_message(
            chat_id=chat_id,
            text="❌ Не хватает алмазов",
            reply_markup=get_main_keyboard()
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Используй кнопки внизу",
            reply_markup=get_main_keyboard()
        )

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        update = telegram.Update.de_json(data, bot)
        
        if update.message:
            handle_message(update)
        
        return "OK", 200
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return "Error", 500

@app.route('/set_webhook')
def set_webhook():
    """Установка вебхука (вызвать один раз в браузере)"""
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    bot.set_webhook(url=webhook_url)
    return f"Webhook set to {webhook_url}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
