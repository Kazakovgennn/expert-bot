import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_login_wrong_password():
    """Неверный пароль"""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrong_password"
    })
    assert response.status_code == 401


def test_login_wrong_username():
    """Неверный логин"""
    response = client.post("/api/auth/login", json={
        "username": "wrong_user",
        "password": "admin123"
    })
    assert response.status_code == 401


def test_login_empty_fields():
    """Пустые поля"""
    response = client.post("/api/auth/login", json={
        "username": "",
        "password": ""
    })
    assert response.status_code == 401


def test_login_missing_fields():
    """Отсутствуют поля"""
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 422  # Validation error
