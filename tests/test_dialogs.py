import pytest
from fastapi.testclient import TestClient
from api.main import app
import jwt
from datetime import datetime, timedelta
from core.config import settings

client = TestClient(app)

def get_test_token():
    payload = {"sub": "admin", "role": "admin", "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def test_get_dialogs_unauthorized():
    """Доступ без токена запрещён"""
    response = client.get("/api/dialogs/")
    assert response.status_code == 401


def test_get_dialogs_with_token():
    """Получение диалогов с токеном"""
    token = get_test_token()
    response = client.get(
        "/api/dialogs/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "data" in response.json()


def test_get_dialogs_pagination():
    """Проверка пагинации"""
    token = get_test_token()
    response = client.get(
        "/api/dialogs/?page=1&limit=10",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["limit"] == 10


def test_get_dialogs_filter_by_user():
    """Фильтрация по user_id"""
    token = get_test_token()
    response = client.get(
        "/api/dialogs/?user_id=999999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_get_dialog_stats():
    """Получение статистики"""
    token = get_test_token()
    response = client.get(
        "/api/dialogs/stats/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "total" in response.json()
