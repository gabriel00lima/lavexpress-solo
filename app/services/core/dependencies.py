# app/services/core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.core.security import verify_token
from app.crud.user import get_user_by_email
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
        token: str = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """Obtém o usuário atual baseado no token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = verify_token(token.credentials)
    if email is None:
        raise credentials_exception

    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta desativada"
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtém usuário ativo (redundante com get_current_user, mas mantido para compatibilidade)"""
    return current_user


def get_optional_current_user(
        token: str = Depends(security),
        db: Session = Depends(get_db)
) -> User | None:
    """Obtém usuário atual, mas não falha se não autenticado (para endpoints opcionais)"""
    try:
        if not token or not token.credentials:
            return None

        email = verify_token(token.credentials)
        if email is None:
            return None

        user = get_user_by_email(db, email=email)
        if user is None or not user.ativo:
            return None

        return user
    except:
        return None