# app/crud/user.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.core.security import get_password_hash, verify_password
from typing import Optional


def create_user(db: Session, user: UserCreate) -> User:
    # Hash da senha
    hashed_password = get_password_hash(user.senha)

    db_user = User(
        nome=user.nome,
        email=user.email,
        senha_hash=hashed_password,
        telefone=user.telefone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.senha_hash):
        return None
    return user


def update_user(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_location(db: Session, user_id: str, latitude: float, longitude: float) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    db_user.latitude = latitude
    db_user.longitude = longitude
    db.commit()
    db.refresh(db_user)
    return db_user


def deactivate_user(db: Session, user_id: str) -> bool:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db_user.ativo = False
    db.commit()
    return True


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.ativo == True).offset(skip).limit(limit).all()