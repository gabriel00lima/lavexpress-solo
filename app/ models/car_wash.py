from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, Time, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class CarWash(Base):
    __tablename__ = "car_washes"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    telefone = Column(String(20))
    endereco = Column(String(255))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    nota = Column(Float, default=0)
    total_avaliacoes = Column(Integer, default=0)
    imagem_url = Column(String(500))
    aberto_de = Column(Time)
    aberto_ate = Column(Time)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    services = relationship("Service", back_populates="car_wash")
    bookings = relationship("Booking", back_populates="car_wash")
    reviews = relationship("Review", back_populates="car_wash")
