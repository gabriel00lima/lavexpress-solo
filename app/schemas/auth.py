# app/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: Optional[str] = None

class PasswordReset(BaseModel):
    token: str
    new_password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class ForgotPassword(BaseModel):
    email: EmailStr