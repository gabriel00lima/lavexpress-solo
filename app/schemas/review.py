from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class ReviewBase(BaseModel):
    nota: int
    comentario: Optional[str] = None

    @validator('nota')
    def validate_nota(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Nota deve estar entre 1 e 5')
        return v

class ReviewCreate(ReviewBase):
    car_wash_id: UUID
    booking_id: Optional[UUID] = None

class Review(ReviewBase):
    id: UUID
    user_id: UUID
    car_wash_id: UUID
    criado_em: datetime
    user_nome: Optional[str] = None

    class Config:
        from_attributes = True