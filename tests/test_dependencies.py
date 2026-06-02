import pytest
import sys
from pathlib import Path
import jwt
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings
from api.dependencies import verify_token, get_current_user
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


def test_valid_token():
    """Проверяет валидный JWT токен"""
    # Создаём валидный токен
    payload = {"sub": "admin", "role": "admin", "exp": datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    credentials = HTTPAuthorizationCredentials(credentials=token, scheme="Bearer")
    result = verify_token(credentials)
    
    assert result["sub"] == "admin"
    assert result["role"] == "admin"


def test_expired_token():
    """Проверяет просроченный токен"""
    # Создаём просроченный токен
    payload = {"sub": "admin", "exp": datetime.utcnow() - timedelta(hours=1)}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    credentials = HTTPAuthorizationCredentials(credentials=token, scheme="Bearer")
    
    with pytest.raises(HTTPException) as exc:
        verify_token(credentials)
    assert exc.value.status_code == 401
    assert "Token expired" in str(exc.value.detail)


def test_invalid_token():
    """Проверяет невалидный токен"""
    credentials = HTTPAuthorizationCredentials(credentials="invalid.token.here", scheme="Bearer")
    
    with pytest.raises(HTTPException) as exc:
        verify_token(credentials)
    assert exc.value.status_code == 401
    assert "Invalid token" in str(exc.value.detail)


def test_get_current_user():
    """Проверяет получение текущего пользователя из токена"""
    payload = {"sub": "admin", "role": "admin"}
    user = get_current_user(payload)
    
    assert user["username"] == "admin"
    assert user["role"] == "admin"
