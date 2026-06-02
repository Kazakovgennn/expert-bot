import asyncio
from telegram import Bot
from core.config import settings

async def test():
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=settings.EXPERT_TELEGRAM_ID,
            text="🔧 Тест: бот может отправить сообщение эксперту"
        )
        print(f"✅ Сообщение отправлено эксперту {settings.EXPERT_TELEGRAM_ID}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

asyncio.run(test())
