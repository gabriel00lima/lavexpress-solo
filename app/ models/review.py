from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    car_wash_id = Column(UUID(as_uuid=True), ForeignKey("car_washes.id"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"))
    nota = Column(Integer, nullable=False)
    comentario = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Constraint para nota entre 1 e 5
    __table_args__ = (
        CheckConstraint('nota >= 1 AND nota <= 5', name='check_nota_range'),
    )

    # Relacionamentos
    user = relationship("User")
    car_wash = relationship("CarWash", back_populates="reviews")
    booking = relationship("Booking")