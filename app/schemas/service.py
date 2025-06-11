# ===== app/schemas/service.py =====
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID

class ServiceBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: Decimal
    duracao_minutos: int

class ServiceCreate(ServiceBase):
    car_wash_id: UUID

class Service(ServiceBase):
    id: UUID
    car_wash_id: UUID
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True