import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.request import HTTPXRequest
from core.config import settings
from bot.handlers import user, expert

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные объекты
application = None

async def main():
    """Запуск бота"""
    global application
    
    # Создаём request с большими таймаутами
    request = HTTPXRequest(
        connect_timeout=60.0,
        read_timeout=60.0,
        write_timeout=60.0,
        pool_timeout=60.0,
        connection_pool_size=1
    )
    
    # Создаём приложение
    application = Application.builder().token(settings.BOT_TOKEN).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", user.start))
    application.add_handler(CommandHandler("help", user.help_command))
    application.add_handler(CommandHandler("stats", user.stats))
    application.add_handler(CommandHandler("expert", user.call_expert))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user.handle_question))
    
    # Callback-обработчики для эксперта
    application.add_handler(CallbackQueryHandler(expert.answer_callback, pattern="^answer_"))
    application.add_handler(CallbackQueryHandler(expert.skip_callback, pattern="^skip_"))
    application.add_handler(CallbackQueryHandler(expert.add_kb_callback, pattern="^add_kb_"))

    # Обработчик ответов эксперта
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, expert.handle_expert_answer))
    
    # Запуск
    logger.info("Запуск бота...")
    await application.initialize()
    await application.start()
    
    # Инициализируем эксперта после запуска
    expert.set_bot(application.bot)
    logger.info("✅ Бот готов к работе!")
    
    await application.updater.start_polling()
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Остановка бота...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
