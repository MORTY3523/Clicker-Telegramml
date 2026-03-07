import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# --- Клавиатура ---
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("⛏ Кликнуть"), KeyboardButton("👤 Профиль")],
        [KeyboardButton("🏪 Магазин"), KeyboardButton("🔧 Апгрейд")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name}!\n\n"
        "/click — кликнуть\n/profile — профиль\n/shop — магазин\n/upgrade — апгрейд",
        reply_markup=get_main_keyboard()
    )

async def click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ +0.000001 алмаза", reply_markup=get_main_keyboard())

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Профиль\n"
        "└ Алмазы: 0.00000000\n"
        "└ Кликов: 0\n"
        "└ Уровень генератора: 0\n"
        "└ Доход: 0.00000 алм/3с",
        reply_markup=get_main_keyboard()
    )

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 Магазин\n\n"
        "🔧 Улучшение генератора: 0.1 алмазов",
        reply_markup=get_main_keyboard()
    )

async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Не хватает алмазов", reply_markup=get_main_keyboard())

# --- Кнопки ---
async def handle_click_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await click(update, context)

async def handle_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await profile(update, context)

async def handle_shop_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await shop(update, context)

async def handle_upgrade_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await upgrade(update, context)

# --- Всё остальное ---
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Используй кнопки внизу",
        reply_markup=get_main_keyboard()
    )

# --- Health check для Render ---
async def health(request):
    return web.Response(text="Bot is running")

# --- Запуск ---
async def main():
    # Веб-сервер, чтобы Render не думал, что мы умерли
    app_web = web.Application()
    app_web.router.add_get("/", health)
    app_web.router.add_get("/health", health)

    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"✅ HTTP сервер запущен на порту {PORT}")

    # Создаём бота с polling
    bot_app = Application.builder().token(TOKEN).build()

    # Регистрируем команды
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("click", click))
    bot_app.add_handler(CommandHandler("profile", profile))
    bot_app.add_handler(CommandHandler("shop", shop))
    bot_app.add_handler(CommandHandler("upgrade", upgrade))

    # Регистрируем кнопки
    bot_app.add_handler(MessageHandler(filters.Text("⛏ Кликнуть"), handle_click_button))
    bot_app.add_handler(MessageHandler(filters.Text("👤 Профиль"), handle_profile_button))
    bot_app.add_handler(MessageHandler(filters.Text("🏪 Магазин"), handle_shop_button))
    bot_app.add_handler(MessageHandler(filters.Text("🔧 Апгрейд"), handle_upgrade_button))

    # Всё остальное
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    # Запуск
    logger.info("🚀 Бот запускается...")
    await bot_app.initialize()
    await bot_app.start()

    # Запускаем polling
    await bot_app.updater.start_polling()
    logger.info("✅ Бот слушает команды")

    # Держим процесс живым
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановка")
