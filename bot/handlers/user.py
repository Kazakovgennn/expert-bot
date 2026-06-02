import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ChatAction
from core.config import settings
from core.qwen_client import generate_answer
from core.rag import KnowledgeBase

logger = logging.getLogger(__name__)

# Инициализация базы знаний (RAG)
kb = KnowledgeBase()

ASKING_QUESTION = 1

main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("❓ Задать вопрос"), KeyboardButton("📞 Позвать эксперта")],
        [KeyboardButton("📊 Статистика")]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я экспертная система.\n\n"
        "Задай мне вопрос, и я постараюсь ответить.\n"
        "Если я не буду уверен — передам вопрос эксперту.\n\n"
        "Чем могу помочь?",
        reply_markup=main_keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Как я работаю:\n\n"
        "1️⃣ Ты задаёшь вопрос\n"
        "2️⃣ Я ищу похожий в базе знаний\n"
        "3️⃣ Если нахожу с уверенностью >85% — отвечаю сам\n"
        "4️⃣ Если нет — передаю эксперту\n\n"
        "Команды:\n"
        "/start — начать заново\n"
        "/stats — моя статистика"
    )

async def ask_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✏️ Напиши свой вопрос текстом:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Отмена")]], resize_keyboard=True)
    )
    return ASKING_QUESTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.", reply_markup=main_keyboard)
    return ConversationHandler.END

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from db.sync_db import get_stats
    total, bot_answered = get_stats(update.effective_user.id)
    
    if total and total > 0:
        percent = int(bot_answered / total * 100) if bot_answered else 0
    else:
        percent = 0
    
    await update.message.reply_text(
        f"📊 Твоя статистика:\n\n"
        f"Всего вопросов: {total or 0}\n"
        f"Я ответил сам: {bot_answered or 0} ({percent}%)\n"
        f"Передано эксперту: {(total or 0) - (bot_answered or 0)}",
        reply_markup=main_keyboard
    )

async def call_expert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🆘 Эксперт уведомлён. Он свяжется с тобой в ближайшее время.")
    from bot.handlers.expert import notify_expert_urgent
    await notify_expert_urgent(update)

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("🟢 handle_question ВЫЗВАНА")
    
    question = update.message.text.strip()
    logger.info(f"🟢 Вопрос: {question}")
    
    # ========== ОБРАБОТКА КНОПОК ==========
    if question == "❓ Задать вопрос":
        await ask_question_start(update, context)
        return
    
    if question == "📊 Статистика":
        await stats(update, context)
        return
    
    if question == "📞 Позвать эксперта":
        await call_expert(update, context)
        return
    
    if question == "❌ Отмена":
        await cancel(update, context)
        return
    # =====================================
    
    # Предопределённые ответы на частые вопросы
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["кто ты", "ты кто", "ты кто такой", "расскажи о себе", "представься"]):
        await update.message.reply_text(
            "🤖 Я — виртуальный эксперт компании [Название компании].\n\n"
            "Моя задача — профессионально консультировать клиентов 24/7.\n"
            "Я обучен на базе знаний компании и постоянно совершенствуюсь.\n\n"
            "Чем могу помочь сегодня?",
            reply_markup=main_keyboard
        )
        return
    
    if any(word in question_lower for word in ["привет", "здравствуй", "здравствуйте", "доброе утро", "добрый день", "добрый вечер", "хай", "hello"]):
        await update.message.reply_text(
            "👋 Здравствуйте! Я виртуальный эксперт.\n\n"
            "Задайте ваш вопрос, и я постараюсь ответить максимально точно.",
            reply_markup=main_keyboard
        )
        return
    
    if any(word in question_lower for word in ["кто тебя создал", "кто тебя сделал", "твой создатель", "кто разработал", "кто программист"]):
        await update.message.reply_text(
            "🔧 Меня разработала команда экспертов на основе современных AI-технологий.\n\n"
            "Я использую локальную нейросеть, что гарантирует конфиденциальность данных и быстрый ответ.\n\n"
            "А теперь давайте к делу — какой у вас вопрос?",
            reply_markup=main_keyboard
        )
        return
    
    if any(word in question_lower for word in ["на чем ты работаешь", "какая модель", "какой ии", "нейросеть", "llm", "qwen", "gpt", "искусственный интеллект"]):
        await update.message.reply_text(
            "🧠 Я работаю на современной языковой модели Qwen 2.5.\n\n"
            "Обработка происходит локально, поэтому:\n"
            "✅ Ваши данные не передаются третьим лицам\n"
            "✅ Скорость ответа максимально высокая\n"
            "✅ Нет ежемесячных платежей за API\n\n"
            "Чем могу помочь?",
            reply_markup=main_keyboard
        )
        return
    
    if any(word in question_lower for word in ["что ты умеешь", "твои возможности", "какие вопросы", "чем можешь помочь", "что ты можешь"]):
        await update.message.reply_text(
            "💡 Мои возможности:\n\n"
            "📌 Консультировать по вопросам компании\n"
            "📌 Отвечать на технические вопросы\n"
            "📌 Помогать с выбором продуктов/услуг\n"
            "📌 Обучаться на основе новых вопросов\n"
            "📌 Передавать сложные вопросы эксперту\n\n"
            "Задавайте любой вопрос — я постараюсь помочь!",
            reply_markup=main_keyboard
        )
        return
    
    if any(word in question_lower for word in ["сохраняешь данные", "конфиденциальность", "приватность", "мои данные", "безопасно"]):
        await update.message.reply_text(
            "🔒 О конфиденциальности:\n\n"
            "✅ Диалоги сохраняются только для обучения системы\n"
            "✅ Данные не передаются третьим лицам\n"
            "✅ Обработка происходит локально на сервере\n"
            "✅ Вы можете запросить удаление ваших данных\n\n"
            "Мы ценим ваше доверие!",
            reply_markup=main_keyboard
        )
        return
    
    if any(word in question_lower for word in ["когда работаешь", "график", "24/7", "круглосуточно", "в любое время"]):
        await update.message.reply_text(
            "⏰ Я работаю 24 часа в сутки, 7 дней в неделю!\n\n"
            "Можете задавать вопросы в любое время — я всегда на связи.\n"
            "Если вопрос окажется слишком сложным, я передам его эксперту.\n\n"
            "Чем могу помочь прямо сейчас?",
            reply_markup=main_keyboard
        )
        return
    
    if any(word in question_lower for word in ["спасибо", "благодарю", "ты помог", "отлично", "супер"]):
        await update.message.reply_text(
            "😊 Пожалуйста! Всегда рад помочь.\n\n"
            "Если появятся новые вопросы — обращайтесь. Хорошего дня!",
            reply_markup=main_keyboard
        )
        return
    
    if any(word in question_lower for word in ["пока", "до свидания", "всего хорошего", "удачи", "прощай"]):
        await update.message.reply_text(
            "👋 До свидания! Буду рад помочь снова.\n\n"
            "Хорошего дня!",
            reply_markup=main_keyboard
        )
        return
    
    # Проверка длины вопроса
    if len(question) > settings.MAX_QUESTION_LENGTH:
        await update.message.reply_text(f"❌ Вопрос слишком длинный (макс {settings.MAX_QUESTION_LENGTH} символов)")
        return
    
    await update.message.chat.send_action(ChatAction.TYPING)
    
    # Поиск в базе знаний (RAG)
    if kb:
        answer, confidence, qa_id = kb.find_similar(question)
        if answer and confidence >= settings.RAG_SIMILARITY_THRESHOLD:
            await update.message.reply_text(f"✅ {answer}", reply_markup=main_keyboard)
            return
    
    # Сохранение диалога и вызов Qwen
    from db.sync_db import save_dialog, update_dialog_answer
    
    log_id = save_dialog(
        user_id=update.effective_user.id,
        user_name=update.effective_user.full_name,
        user_question=question,
        final_answer="Генерирую ответ...",
        source="pending",
        confidence=0
    )
    
    logger.info("🟢 Вызываем Qwen...")
    answer, confidence = await generate_answer(question)
    logger.info(f"🟢 Qwen ответила: answer={answer}, confidence={confidence}")
    
    # ========== ОСНОВНАЯ ЛОГИКА ==========
    # Если ответ есть И уверенность >= 70% — отвечаем сами
    if answer is not None and confidence >= 70:
        if log_id:
            update_dialog_answer(log_id, answer, "bot_qwen", confidence)
        await update.message.reply_text(f"🤖 {answer}", reply_markup=main_keyboard)
        return
    
    # Если ответ есть, но уверенность < 70% — передаём эксперту
    if answer is not None and confidence < 70:
        logger.info(f"🟢 Уверенность {confidence}% < 70%, передаём эксперту")
        if settings.EXPERT_TELEGRAM_ID:
            from bot.handlers.expert import forward_to_expert
            if log_id:
                update_dialog_answer(log_id, "Ожидает ответа эксперта", "pending_expert", confidence)
            await forward_to_expert(update, question, log_id)
            await update.message.reply_text(
                "❓ Я не уверен в ответе.\n\n"
                "Вопрос передан эксперту. Обычно ответ приходит в течение часа.\n"
                "Я уведомлю вас, когда ответ появится.",
                reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text(
                "❌ Извините, я не смог найти ответ. Эксперт временно недоступен.",
                reply_markup=main_keyboard
            )
        return
    
    # Если ответа нет (None) — тоже передаём эксперту
    if answer is None:
        logger.info(f"🟢 Ответ отсутствует, передаём эксперту")
        if settings.EXPERT_TELEGRAM_ID:
            from bot.handlers.expert import forward_to_expert
            if log_id:
                update_dialog_answer(log_id, "Ожидает ответа эксперта", "pending_expert", 0)
            await forward_to_expert(update, question, log_id)
            await update.message.reply_text(
                "❓ Я не уверен в ответе.\n\n"
                "Вопрос передан эксперту. Обычно ответ приходит в течение часа.\n"
                "Я уведомлю вас, когда ответ появится.",
                reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text(
                "❌ Извините, я не смог найти ответ. Эксперт временно недоступен.",
                reply_markup=main_keyboard
            )
        return
