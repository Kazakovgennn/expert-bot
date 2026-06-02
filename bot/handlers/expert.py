import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.config import settings
from db.sync_db import update_dialog_answer

logger = logging.getLogger(__name__)

# Глобальный объект бота
bot_instance = None

def set_bot(bot):
    global bot_instance
    bot_instance = bot


async def forward_to_expert(update: Update, question: str, log_id: int):
    """Пересылает вопрос эксперту в Telegram"""
    if not bot_instance:
        logger.error("❌ Бот не инициализирован, не могу отправить сообщение эксперту")
        return
    
    expert_text = (
        f"🔔 НОВЫЙ ВОПРОС\n\n"
        f"От: {update.effective_user.full_name} (ID: {update.effective_user.id})\n"
        f"Вопрос: {question}\n\n"
        f"Лог ID: {log_id}\n\n"
        f"Чтобы ответить, просто отправь сообщение в этот чат."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Ответить", callback_data=f"answer_{log_id}")],
        [InlineKeyboardButton("⏭️ Пропустить", callback_data=f"skip_{log_id}")]
    ])
    
    try:
        await bot_instance.send_message(
            settings.EXPERT_TELEGRAM_ID,
            expert_text,
            reply_markup=keyboard
        )
        logger.info(f"✅ Вопрос #{log_id} передан эксперту")
    except Exception as e:
        logger.error(f"❌ Ошибка при пересылке эксперту: {e}")


async def notify_expert_urgent(update: Update):
    """Срочное уведомление эксперта"""
    if not bot_instance:
        logger.error("Бот не инициализирован")
        return
    
    text = (
        f"🚨 СРОЧНЫЙ ВЫЗОВ ЭКСПЕРТА\n\n"
        f"Пользователь: {update.effective_user.full_name} (ID: {update.effective_user.id})\n"
        f"Требует внимания!"
    )
    
    try:
        await bot_instance.send_message(settings.EXPERT_TELEGRAM_ID, text)
        logger.info("✅ Срочное уведомление отправлено эксперту")
    except Exception as e:
        logger.error(f"❌ Ошибка при срочном уведомлении: {e}")


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Эксперт нажал 'Ответить'"""
    query = update.callback_query
    await query.answer()
    
    log_id = int(query.data.split("_")[1])
    context.user_data['answering_log_id'] = log_id
    context.user_data['waiting_for_expert_answer'] = True
    
    await query.edit_message_text(
        f"✏️ Напиши ответ на вопрос (лог #{log_id}):\n\n"
        f"Просто отправь сообщение в этот чат."
    )
    logger.info(f"Эксперт начал отвечать на вопрос #{log_id}")


async def skip_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Эксперт пропустил вопрос"""
    query = update.callback_query
    await query.answer()
    
    log_id = int(query.data.split("_")[1])
    
    # Обновляем статус в БД
    update_dialog_answer(log_id, "Пропущен экспертом", "skipped", 0)
    
    await query.edit_message_text(f"⏭️ Вопрос #{log_id} пропущен.")
    logger.info(f"Эксперт пропустил вопрос #{log_id}")


async def handle_expert_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа эксперта"""
    if not context.user_data.get('waiting_for_expert_answer'):
        return
    
    log_id = context.user_data.get('answering_log_id')
    if not log_id:
        await update.message.reply_text("❌ Ошибка: не найден ID вопроса")
        context.user_data.clear()
        return
    
    answer_text = update.message.text
    
    # Получаем информацию о вопросе из БД
    from db.sync_db import get_question_by_id
    question_info = get_question_by_id(log_id)
    
    if not question_info:
        await update.message.reply_text("❌ Лог не найден")
        context.user_data.clear()
        return
    
    user_id = question_info['user_id']
    user_question = question_info['user_question']
    
    # Обновляем запись с ответом эксперта
    update_dialog_answer(log_id, answer_text, "expert", 100)
    
    # Отправляем ответ пользователю
    if bot_instance:
        try:
            await bot_instance.send_message(
                user_id,
                f"👨‍🏫 Эксперт ответил:\n\n{answer_text}"
            )
            await update.message.reply_text(
                f"✅ Ответ отправлен пользователю!\n\n"
                f"Вопрос: {user_question[:100]}...\n"
                f"Ответ: {answer_text[:200]}..."
            )
            logger.info(f"✅ Ответ эксперта отправлен пользователю {user_id}")
        except Exception as e:
            logger.error(f"❌ Не удалось отправить ответ пользователю: {e}")
            await update.message.reply_text(f"❌ Ошибка: не удалось отправить ответ пользователю. {e}")
    else:
        await update.message.reply_text("❌ Бот не инициализирован")
    
    context.user_data.clear()


async def add_kb_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Эксперт подтвердил добавление в БЗ (заглушка, пока RAG отключён)"""
    query = update.callback_query
    await query.answer()
    
    log_id = int(query.data.split("_")[2])
    
    await query.edit_message_text(
        f"💾 Ответ будет добавлен в базу знаний после включения RAG.\n\n"
        f"Лог #{log_id} помечен для обучения."
    )
    logger.info(f"Эксперт отметил ответ #{log_id} для добавления в БЗ")
