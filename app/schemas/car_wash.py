# ===== app/schemas/car_wash.py =====
from pydantic import BaseModel
from typing import Optional, List
from datetime import time, datetime
from uuid import UUID
from app.schemas.service import Service

class CarWashBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    latitude: float
    longitude: float
    imagem_url: Optional[str] = None
    aberto_de: Optional[time] = None
    aberto_ate: Optional[time] = None

class CarWashCreate(CarWashBase):
    pass

class CarWash(CarWashBase):
    id: UUID
    nota: float
    total_avaliacoes: int
    ativo: bool
    criado_em: datetime
    distancia: Optional[float] = None  # Calculada dinamicamente

    class Config:
        from_attributes = True

class CarWashWithServices(CarWash):
    services: List[Service] = []