import asyncio
from core.qwen_client import generate_answer

async def test():
    print("🟢 Тестируем Qwen...")
    answer, confidence = await generate_answer("Привет! Как дела?")
    print(f"📝 Ответ: {answer}")
    print(f"🎯 Уверенность: {confidence}%")

asyncio.run(test())
