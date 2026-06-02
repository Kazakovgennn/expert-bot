import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.sync_db import save_dialog, update_dialog_answer, get_stats, get_connection


def test_get_connection():
    """Проверяет подключение к БД"""
    conn = get_connection()
    assert conn is not None
    conn.close()


def test_save_and_update_dialog():
    """Проверяет сохранение и обновление диалога"""
    # Сохраняем
    log_id = save_dialog(
        user_id=999999,
        user_name="Test User",
        user_question="Тестовый вопрос",
        final_answer="Временный ответ",
        source="test",
        confidence=50
    )
    
    assert log_id is not None
    
    # Обновляем
    result = update_dialog_answer(log_id, "Финальный ответ", "test_updated", 100)
    assert result is True


def test_get_stats():
    """Проверяет получение статистики"""
    total, bot_answered = get_stats(999999)
    assert isinstance(total, int)
    assert isinstance(bot_answered, int)
