import os
import logging
from flask import Flask, request, jsonify
import telegram

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telegram.Bot(token=TOKEN)

# Создаём Flask приложение
app = Flask(__name__)

# Простая клавиатура
def get_keyboard():
    keyboard = [
        [telegram.KeyboardButton("⛏ Кликнуть"), telegram.KeyboardButton("👤 Профиль")],
        [telegram.KeyboardButton("🏪 Магазин"), telegram.KeyboardButton("🔧 Апгрейд")]
    ]
    return telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

@app.route('/')
def index():
    return "Бот работает!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Принимает обновления от Telegram"""
    try:
        # Получаем данные от Telegram
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        
        # Обрабатываем сообщение
        if update.message and update.message.text:
            chat_id = update.message.chat.id
            text = update.message.text
            
            logger.info(f"Получено сообщение: {text} от {chat_id}")
            
            # Обработка команд и кнопок
            if text == '/start':
                bot.send_message(
                    chat_id=chat_id,
                    text="👋 Привет! Ты попал в кликер-симулятор.",
                    reply_markup=get_keyboard()
                )
            elif text == '⛏ Кликнуть' or text == '/click':
                bot.send_message(
                    chat_id=chat_id,
                    text="✅ +0.000001 алмаза",
                    reply_markup=get_keyboard()
                )
            elif text == '👤 Профиль' or text == '/profile':
                bot.send_message(
                    chat_id=chat_id,
                    text="👤 Профиль\n└ Алмазы: 0.00000000\n└ Кликов: 0\n└ Уровень генератора: 0",
                    reply_markup=get_keyboard()
                )
            elif text == '🏪 Магазин' or text == '/shop':
                bot.send_message(
                    chat_id=chat_id,
                    text="🏪 Магазин\n\n🔧 Улучшение генератора: 0.1 алмазов",
                    reply_markup=get_keyboard()
                )
            elif text == '🔧 Апгрейд' or text == '/upgrade':
                bot.send_message(
                    chat_id=chat_id,
                    text="❌ Не хватает алмазов",
                    reply_markup=get_keyboard()
                )
            else:
                bot.send_message(
                    chat_id=chat_id,
                    text="Используй кнопки внизу или команды: /start, /click, /profile, /shop, /upgrade",
                    reply_markup=get_keyboard()
                )
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return "Error", 500

# Функция для установки вебхука (выполни один раз)
@app.route('/setwebhook')
def set_webhook():
    s = bot.setWebhook(f'https://{os.environ.get("RENDER_EXTERNAL_HOSTNAME")}/webhook')
    if s:
        return "Webhook установлен!"
    else:
        return "Ошибка установки вебхука"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
