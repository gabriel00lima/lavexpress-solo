from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    preco = Column(Numeric(10, 2), nullable=False)
    duracao_minutos = Column(Integer, nullable=False)
    car_wash_id = Column(UUID(as_uuid=True), ForeignKey("car_washes.id"), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    car_wash = relationship("CarWash", back_populates="services")
    bookings = relationship("Booking", back_populates="service")
