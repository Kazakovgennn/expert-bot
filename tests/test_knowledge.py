import pytest
from fastapi.testclient import TestClient
from api.main import app
import jwt
from datetime import datetime, timezone, timedelta
from core.config import settings
from db.sync_db import get_connection

client = TestClient(app)

def get_test_token():
    payload = {"sub": "admin", "role": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def clean_knowledge():
    """Очищает таблицу knowledge перед каждым тестом"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM knowledge WHERE question LIKE '%pytest%' OR question LIKE 'Для%'")
    conn.commit()
    cur.close()
    conn.close()
    yield
    # После теста тоже очищаем
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM knowledge WHERE question LIKE '%pytest%' OR question LIKE 'Для%'")
    conn.commit()
    cur.close()
    conn.close()


def test_get_knowledge_unauthorized():
    response = client.get("/api/knowledge/")
    assert response.status_code == 401


def test_get_knowledge_with_token():
    token = get_test_token()
    response = client.get("/api/knowledge/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "data" in response.json()


def test_get_knowledge_pagination():
    token = get_test_token()
    response = client.get("/api/knowledge/?page=1&limit=5", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["limit"] == 5


def test_create_knowledge(clean_knowledge):
    token = get_test_token()
    response = client.post(
        "/api/knowledge/",
        json={
            "question": "Вопрос из pytest",
            "answer": "Ответ из pytest",
            "category": "test"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["question"] == "Вопрос из pytest"


def test_update_knowledge(clean_knowledge):
    token = get_test_token()
    # Сначала создаём
    create_resp = client.post(
        "/api/knowledge/",
        json={
            "question": "Для обновления",
            "answer": "Старый ответ"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    knowledge_id = create_resp.json()["id"]
    
    # Обновляем
    update_resp = client.put(
        f"/api/knowledge/{knowledge_id}",
        json={"answer": "Новый ответ"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["answer"] == "Новый ответ"


def test_delete_knowledge(clean_knowledge):
    token = get_test_token()
    create_resp = client.post(
        "/api/knowledge/",
        json={
            "question": "Для удаления",
            "answer": "Ответ для удаления"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    knowledge_id = create_resp.json()["id"]
    
    delete_resp = client.delete(
        f"/api/knowledge/{knowledge_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_resp.status_code == 200
    assert "deactivated" in delete_resp.json()["message"]


def test_get_categories():
    token = get_test_token()
    response = client.get(
        "/api/knowledge/categories/list",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "categories" in response.json()
