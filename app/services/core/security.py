# app/services/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.services.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha digitada corresponde ao hash armazenado"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha para armazenamento seguro"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT para autenticação"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


def create_refresh_token(data: dict) -> str:
    """Cria token de refresh com duração maior"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 7 dias
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> Optional[str]:
    """Verifica token de refresh"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Verifica se é um refresh token
        if payload.get("type") != "refresh":
            return None

        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


def generate_password_reset_token(email: str) -> str:
    """Gera token para reset de senha"""
    delta = timedelta(hours=1)  # Token válido por 1 hora
    to_encode = {"sub": email, "type": "password_reset"}
    expire = datetime.utcnow() + delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verifica token de reset de senha"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Verifica se é um token de reset
        if payload.get("type") != "password_reset":
            return None

        email: str = payload.get("sub")
        return email
    except JWTError:
        return None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Valida se a senha atende aos critérios de segurança"""
    if len(password) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres"

    if not any(c.isupper() for c in password):
        return False, "Senha deve conter pelo menos uma letra maiúscula"

    if not any(c.islower() for c in password):
        return False, "Senha deve conter pelo menos uma letra minúscula"

    if not any(c.isdigit() for c in password):
        return False, "Senha deve conter pelo menos um número"

    # Verifica caracteres especiais
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Senha deve conter pelo menos um caractere especial"

    return True, "Senha válida"