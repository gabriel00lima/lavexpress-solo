# ===== app/schemas/user.py =====
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None

class UserCreate(UserBase):
    senha: str

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserLocation(BaseModel):
    latitude: float
    longitude: float

class User(UserBase):
    id: UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True