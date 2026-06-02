import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Проверяет корневой эндпоинт"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Expert Bot Admin API"
    assert response.json()["status"] == "running"


def test_health_endpoint():
    """Проверяет healthcheck"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_invalid():
    """Проверяет логин с неверными данными"""
    response = client.post("/api/auth/login", json={
        "username": "wrong",
        "password": "wrong"
    })
    assert response.status_code == 401


def test_knowledge_list_requires_auth():
    """Проверяет, что эндпоинт требует авторизацию"""
    response = client.get("/api/knowledge/")
    assert response.status_code == 403 or response.status_code == 401


def test_dialogs_list_requires_auth():
    """Проверяет, что эндпоинт требует авторизацию"""
    response = client.get("/api/dialogs/")
    assert response.status_code == 403 or response.status_code == 401
