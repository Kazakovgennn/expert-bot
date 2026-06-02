import pytest
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings
from core.rag import KnowledgeBase


def test_config_loaded():
    """Проверяет, что конфигурация загружается"""
    assert settings.BOT_TOKEN is not None
    assert settings.DATABASE_URL is not None


def test_knowledge_base_init():
    """Проверяет инициализацию базы знаний"""
    kb = KnowledgeBase()
    assert kb is not None


def test_knowledge_base_add_and_find():
    """Проверяет добавление и поиск в базе знаний"""
    kb = KnowledgeBase()
    
    # Добавляем тестовый вопрос
    kb.add_qa(999, "тестовый вопрос", "тестовый ответ")
    
    # Ищем
    answer, score, qa_id = kb.find_similar("тестовый вопрос")
    
    # Проверяем
    assert answer == "тестовый ответ"
    assert score >= 85
    assert qa_id == 999


def test_fuzzy_search():
    """Проверяет нечёткий поиск"""
    kb = KnowledgeBase()
    
    kb.add_qa(998, "сколько будет 2 плюс 2", "4")
    
    answer, score, _ = kb.find_similar("2+2?")
    
    # Должен найти с достаточной уверенностью
    assert score >= 50
