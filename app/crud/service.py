# app/crud/service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.service import Service
from app.schemas.service import ServiceCreate
from typing import List, Optional


def create_service(db: Session, service: ServiceCreate) -> Service:
    db_service = Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


def get_service_by_id(db: Session, service_id: str) -> Optional[Service]:
    return db.query(Service).filter(
        and_(Service.id == service_id, Service.ativo == True)
    ).first()


def get_services_by_car_wash(db: Session, car_wash_id: str) -> List[Service]:
    return db.query(Service).filter(
        and_(Service.car_wash_id == car_wash_id, Service.ativo == True)
    ).all()


def get_all_services(db: Session, skip: int = 0, limit: int = 100) -> List[Service]:
    return db.query(Service).filter(Service.ativo == True).offset(skip).limit(limit).all()


def update_service(db: Session, service_id: str, service_data: dict) -> Optional[Service]:
    db_service = get_service_by_id(db, service_id)
    if not db_service:
        return None

    for field, value in service_data.items():
        if hasattr(db_service, field) and value is not None:
            setattr(db_service, field, value)

    db.commit()
    db.refresh(db_service)
    return db_service


def deactivate_service(db: Session, service_id: str) -> bool:
    db_service = get_service_by_id(db, service_id)
    if not db_service:
        return False

    db_service.ativo = False
    db.commit()
    return True


def search_services(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Service]:
    """Busca serviços por nome ou descrição"""
    from sqlalchemy import func

    return db.query(Service).filter(
        and_(
            Service.ativo == True,
            func.lower(Service.nome).contains(query.lower()) |
            func.lower(Service.descricao).contains(query.lower())
        )
    ).offset(skip).limit(limit).all()


def get_services_by_price_range(
        db: Session,
        min_price: float = None,
        max_price: float = None,
        skip: int = 0,
        limit: int = 100
) -> List[Service]:
    """Busca serviços por faixa de preço"""
    query = db.query(Service).filter(Service.ativo == True)

    if min_price is not None:
        query = query.filter(Service.preco >= min_price)

    if max_price is not None:
        query = query.filter(Service.preco <= max_price)

    return query.offset(skip).limit(limit).all()