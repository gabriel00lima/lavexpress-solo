# app/crud/car_wash.py
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.car_wash import CarWash
from app.models.service import Service
from app.models.review import Review
from app.schemas.car_wash import CarWashCreate
from typing import List, Optional
import math


def create_car_wash(db: Session, car_wash: CarWashCreate) -> CarWash:
    db_car_wash = CarWash(**car_wash.dict())
    db.add(db_car_wash)
    db.commit()
    db.refresh(db_car_wash)
    return db_car_wash


def get_car_wash_by_id(db: Session, car_wash_id: str) -> Optional[CarWash]:
    return db.query(CarWash).filter(
        and_(CarWash.id == car_wash_id, CarWash.ativo == True)
    ).first()


def get_car_washes(db: Session, skip: int = 0, limit: int = 100) -> List[CarWash]:
    return db.query(CarWash).filter(CarWash.ativo == True).offset(skip).limit(limit).all()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula distância entre dois pontos usando fórmula de Haversine"""
    R = 6371  # Raio da Terra em km

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return round(distance, 2)


def get_nearby_car_washes(
        db: Session,
        user_lat: float,
        user_lon: float,
        radius_km: float = 10,
        skip: int = 0,
        limit: int = 100
) -> List[CarWash]:
    """Busca lava-jatos próximos ao usuário"""
    car_washes = db.query(CarWash).filter(CarWash.ativo == True).all()

    nearby_car_washes = []
    for car_wash in car_washes:
        distance = calculate_distance(user_lat, user_lon, car_wash.latitude, car_wash.longitude)
        if distance <= radius_km:
            # Adiciona distância como atributo temporário
            car_wash.distancia = distance
            nearby_car_washes.append(car_wash)

    # Ordena por distância
    nearby_car_washes.sort(key=lambda x: x.distancia)

    return nearby_car_washes[skip:skip + limit]


def search_car_washes(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[CarWash]:
    """Busca lava-jatos por nome ou descrição"""
    return db.query(CarWash).filter(
        and_(
            CarWash.ativo == True,
            func.lower(CarWash.nome).contains(query.lower()) |
            func.lower(CarWash.descricao).contains(query.lower())
        )
    ).offset(skip).limit(limit).all()


def get_car_wash_with_services(db: Session, car_wash_id: str):
    """Retorna lava-jato com seus serviços"""
    car_wash = get_car_wash_by_id(db, car_wash_id)
    if not car_wash:
        return None

    services = db.query(Service).filter(
        and_(Service.car_wash_id == car_wash_id, Service.ativo == True)
    ).all()

    car_wash.services = services
    return car_wash


def update_car_wash_rating(db: Session, car_wash_id: str):
    """Atualiza a nota média do lava-jato baseado nas avaliações"""
    rating_data = db.query(
        func.avg(Review.nota).label('avg_rating'),
        func.count(Review.id).label('total_reviews')
    ).filter(Review.car_wash_id == car_wash_id).first()

    car_wash = get_car_wash_by_id(db, car_wash_id)
    if car_wash and rating_data:
        car_wash.nota = round(rating_data.avg_rating or 0, 1)
        car_wash.total_avaliacoes = rating_data.total_reviews or 0
        db.commit()
        db.refresh(car_wash)

    return car_wash


def deactivate_car_wash(db: Session, car_wash_id: str) -> bool:
    car_wash = get_car_wash_by_id(db, car_wash_id)
    if not car_wash:
        return False

    car_wash.ativo = False
    db.commit()
    return True