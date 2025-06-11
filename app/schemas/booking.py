from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime
from uuid import UUID
from app.models.booking import BookingStatus

class BookingBase(BaseModel):
    data: date
    hora: time
    observacoes: Optional[str] = None

class BookingCreate(BookingBase):
    car_wash_id: UUID
    service_id: UUID

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    observacoes: Optional[str] = None

class Booking(BookingBase):
    id: UUID
    user_id: UUID
    car_wash_id: UUID
    service_id: UUID
    status: BookingStatus
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

class BookingWithDetails(Booking):
    car_wash_nome: str
    service_nome: str
    service_preco: Decimal