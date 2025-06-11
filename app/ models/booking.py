from sqlalchemy import Column, String, Text, Date, Time, DateTime, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class BookingStatus(enum.Enum):
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"
    CONCLUIDO = "concluido"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    car_wash_id = Column(UUID(as_uuid=True), ForeignKey("car_washes.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDENTE)
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    user = relationship("User")
    car_wash = relationship("CarWash", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")