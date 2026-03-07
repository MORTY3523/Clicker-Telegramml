import os
import logging
import asyncio
import requests
from aiohttp import web
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен берется из переменных окружения Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# Клавиатура с кнопками (ReplyKeyboardMarkup)
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("⛏ Кликнуть"), KeyboardButton("👤 Профиль")],
        [KeyboardButton("🏪 Магазин"), KeyboardButton("🔧 Апгрейд")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "Ты попал в кликер-симулятор.\n"
        "Используй кнопки ниже или команды:\n"
        "/click — кликнуть\n"
        "/profile — профиль\n"
        "/shop — магазин\n"
        "/upgrade — апгрейд",
        reply_markup=get_main_keyboard()
    )

# Обработчик кнопки "⛏ Кликнуть"
async def click_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ +0.000001 алмаза", reply_markup=get_main_keyboard())

# Обработчик кнопки "👤 Профиль"
async def profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Профиль\n"
        "└ Алмазы: 0.00000000\n"
        "└ Кликов: 0\n"
        "└ Уровень генератора: 0\n"
        "└ Доход: 0.00000 алм/3с",
        reply_markup=get_main_keyboard()
    )

# Обработчик кнопки "🏪 Магазин"
async def shop_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 Магазин\n\n"
        "🔧 Улучшение генератора\n"
        "└ Уровень: 0\n"
        "└ Цена: 0.1 алмазов\n\n"
        "👉 /upgrade — купить",
        reply_markup=get_main_keyboard()
    )

# Обработчик кнопки "🔧 Апгрейд"
async def upgrade_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Не хватает алмазов\nНужно: 0.1",
        reply_markup=get_main_keyboard()
    )

# Обработчик текстовых команд
async def click_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await click_button(update, context)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await profile_button(update, context)

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await shop_button(update, context)

async def upgrade_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await upgrade_button(update, context)

# Обработчик всех остальных сообщений (которые не команды и не кнопки)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text in ["⛏ Кликнуть", "👤 Профиль", "🏪 Магазин", "🔧 Апгрейд"]:
        return  # Эти уже обработаны отдельно
    await update.message.reply_text(
        "Используй кнопки внизу или команды: /start, /click, /profile, /shop, /upgrade",
        reply_markup=get_main_keyboard()
    )

# Настройка aiohttp сервера (чтобы Render не ругался)
async def handle_health(request):
    return web.Response(text="Bot is running")

async def main():
    # Создаем aiohttp приложение
    app_web = web.Application()
    app_web.router.add_get("/", handle_health)
    app_web.router.add_get("/health", handle_health)
    
    # Запускаем веб-сервер
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"HTTP Server started on port {PORT}")
    
    # Создаем Telegram бота (без Updater, напрямую через Application)
    builder = Application.builder().token(TOKEN)
    builder.updater(None)  # Отключаем встроенный Updater, будем использовать polling
    bot_app = builder.build()
    
    # Добавляем обработчики
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("click", click_command))
    bot_app.add_handler(CommandHandler("profile", profile_command))
    bot_app.add_handler(CommandHandler("shop", shop_command))
    bot_app.add_handler(CommandHandler("upgrade", upgrade_command))
    
    # Обработчики для кнопок
    bot_app.add_handler(MessageHandler(filters.Text("⛏ Кликнуть"), click_button))
    bot_app.add_handler(MessageHandler(filters.Text("👤 Профиль"), profile_button))
    bot_app.add_handler(MessageHandler(filters.Text("🏪 Магазин"), shop_button))
    bot_app.add_handler(MessageHandler(filters.Text("🔧 Апгрейд"), upgrade_button))
    
    # Обработчик всех остальных сообщений
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запускаем бота
    logger.info("Starting bot...")
    await bot_app.initialize()
    await bot_app.start()
    
    # Запускаем polling
    await bot_app.updater.start_polling()
    
    # Держим бота запущенным
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
