import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import app
from core.config import settings

client = TestClient(app)

def get_test_token():
    payload = {"sub": "admin", "role": "admin", "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def test_get_knowledge_unauthorized():
    """Доступ без токена запрещён"""
    response = client.get("/api/knowledge/")
    assert response.status_code == 403


def test_get_knowledge_with_token():
    """Получение базы знаний с токеном"""
    token = get_test_token()
    response = client.get(
        "/api/knowledge/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "data" in response.json()


def test_get_knowledge_pagination():
    """Пагинация базы знаний"""
    token = get_test_token()
    response = client.get(
        "/api/knowledge/?page=1&limit=20",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["limit"] == 20


def test_get_knowledge_search():
    """Поиск по базе знаний"""
    token = get_test_token()
    response = client.get(
        "/api/knowledge/?search=2+2",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_create_knowledge():
    """Создание нового вопроса-ответа"""
    token = get_test_token()
    response = client.post(
        "/api/knowledge/",
        json={
            "question": "Тестовый вопрос из pytest",
            "answer": "Тестовый ответ из pytest",
            "category": "test"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["question"] == "Тестовый вопрос из pytest"
    
    # Сохраняем ID для последующего удаления
    return response.json()["id"]


def test_update_knowledge():
    """Обновление вопроса-ответа"""
    # Сначала создаём
    token = get_test_token()
    create_response = client.post(
        "/api/knowledge/",
        json={
            "question": "Вопрос для обновления",
            "answer": "Старый ответ",
            "category": "test"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    knowledge_id = create_response.json()["id"]
    
    # Обновляем
    update_response = client.put(
        f"/api/knowledge/{knowledge_id}",
        json={"answer": "Новый ответ"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["answer"] == "Новый ответ"


def test_delete_knowledge():
    """Удаление вопроса-ответа (деактивация)"""
    # Сначала создаём
    token = get_test_token()
    create_response = client.post(
        "/api/knowledge/",
        json={
            "question": "Вопрос для удаления",
            "answer": "Ответ для удаления",
            "category": "test"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    knowledge_id = create_response.json()["id"]
    
    # Удаляем
    delete_response = client.delete(
        f"/api/knowledge/{knowledge_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 200
    assert "deactivated" in delete_response.json()["message"]


def test_get_categories():
    """Получение списка категорий"""
    token = get_test_token()
    response = client.get(
        "/api/knowledge/categories/list",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "categories" in response.json()
