import asyncio
import aiohttp
import logging
import re
from core.config import settings

logger = logging.getLogger(__name__)

async def ask_qwen(prompt: str, system_prompt: str = None) -> tuple[str | None, int]:
    """
    Отправляет запрос к локальной Qwen 2.5 через Ollama
    Возвращает: (ответ, уверенность_в_процентах)
    """
    full_prompt = ""
    if system_prompt:
        full_prompt = f"{system_prompt}\n\nПользователь: {prompt}\nАссистент:"
    else:
        full_prompt = f"Пользователь: {prompt}\nАссистент:"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 500
                    }
                },
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                result = await response.json()
                answer = result.get("response", "").strip()
                
                # Удаляем китайские/японские символы
                cleaned = re.sub(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', '', answer)
                if cleaned != answer:
                    logger.warning(f"Удалены китайские/японские символы из ответа")
                    answer = cleaned
                
                # Оценка уверенности
                if len(answer) > 100:
                    confidence = 90
                elif len(answer) > 50:
                    confidence = 85
                elif len(answer) > 20:
                    confidence = 70
                elif len(answer) > 5:
                    confidence = 50
                else:
                    confidence = 30
                
                unknown_phrases = ["не знаю", "не уверен", "извините", "не могу ответить", "no idea"]
                if any(phrase in answer.lower() for phrase in unknown_phrases):
                    confidence = min(confidence, 35)
                
                logger.info(f"Qwen ответила. Длина: {len(answer)}. Уверенность: {confidence}%")
                return answer, confidence
                
    except asyncio.TimeoutError:
        logger.error("Таймаут при запросе к Ollama (120 сек)")
        return None, 0
    except Exception as e:
        logger.error(f"Ошибка при запросе к Qwen: {e}")
        return None, 0

async def generate_answer(question: str, context: str = None) -> tuple[str | None, int]:
    """Главная функция для генерации ответа"""
    system_prompt = """Ты — профессиональный эксперт-консультант. Твоя задача — давать полезные, точные и развёрнутые ответы на русском языке.

ПРАВИЛА:
1. Отвечай ТОЛЬКО на русском языке. Ни слова на английском, китайском или других языках.
2. Если не знаешь ответа — скажи "У меня нет точной информации по этому вопросу".
3. Не выдумывай факты.
4. Будь дружелюбным и профессиональным.

ЗАПОМНИ: ВСЕГДА ОТВЕЧАЙ НА РУССКОМ ЯЗЫКЕ."""
    
    user_prompt = f"Вопрос: {question}"
    if context:
        user_prompt += f"\n\nКонтекст из базы знаний: {context}"
    
    return await ask_qwen(user_prompt, system_prompt)
