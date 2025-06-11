from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate):
    db_user = User(
        nome=user.nome,
        email=user.email,
        senha=user.senha,  # ⚠️ vamos criptografar depois!
        tipo=user.tipo,
        latitude=user.latitude,
        longitude=user.longitude
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
