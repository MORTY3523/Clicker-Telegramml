import os
import logging
import asyncio
import requests
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен берется из переменных окружения Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))  # Render сам подставляет PORT

# Простой обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен на Render! 🚀")

# Настройка aiohttp сервера (чтобы Render не ругался на отсутствие порта)
async def handle(request):
    return web.Response(text="Bot is running")

async def main():
    # Создаем aiohttp приложение
    app = web.Application()
    app.router.add_get("/", handle)
    app.router.add_get("/health", handle)
    
    # Запускаем веб-сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"HTTP Server started on port {PORT}")
    
    # Создаем Telegram бота
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    
    # Запускаем бота
    logger.info("Starting bot polling...")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    
    # Держим бота запущенным
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
