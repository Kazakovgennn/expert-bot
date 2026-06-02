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

# Создаём токен для тестов
def get_test_token():
    payload = {"sub": "admin", "role": "admin", "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def test_get_dialogs_unauthorized():
    """Доступ без токена запрещён"""
    response = client.get("/api/dialogs/")
    assert response.status_code == 403


def test_get_dialogs_with_token():
    """Получение диалогов с токеном"""
    token = get_test_token()
    response = client.get(
        "/api/dialogs/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "data" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()


def test_get_dialogs_pagination():
    """Проверка пагинации"""
    token = get_test_token()
    response = client.get(
        "/api/dialogs/?page=1&limit=10",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["limit"] == 10
    assert response.json()["page"] == 1


def test_get_dialogs_filter_by_user():
    """Фильтрация по user_id"""
    token = get_test_token()
    response = client.get(
        "/api/dialogs/?user_id=999999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_get_dialogs_filter_by_source():
    """Фильтрация по источнику"""
    token = get_test_token()
    response = client.get(
        "/api/dialogs/?source=bot_qwen",
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
    assert "bot_answered" in response.json()
    assert "expert_answered" in response.json()
