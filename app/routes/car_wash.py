# app/routes/car_wash.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.car_wash import CarWash as CarWashSchema, CarWashCreate, CarWashWithServices
from app.crud.car_wash import (
    create_car_wash,
    get_car_wash_by_id,
    get_car_washes,
    get_nearby_car_washes,
    search_car_washes,
    get_car_wash_with_services,
    update_car_wash_rating,
    deactivate_car_wash
)
from app.services.core.dependencies import get_current_user, get_optional_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[CarWashSchema])
async def list_car_washes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lista todos os lava-jatos ativos"""
    car_washes = get_car_washes(db, skip=skip, limit=limit)
    return car_washes

@router.get("/nearby", response_model=List[CarWashSchema])
async def get_nearby_car_washes_endpoint(
    latitude: float = Query(..., description="Latitude do usuário"),
    longitude: float = Query(..., description="Longitude do usuário"),
    radius: float = Query(10, ge=1, le=50, description="Raio de busca em km"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Busca lava-jatos próximos à localização do usuário"""
    car_washes = get_nearby_car_washes(
        db,
        user_lat=latitude,
        user_lon=longitude,
        radius_km=radius,
        skip=skip,
        limit=limit
    )
    return car_washes

@router.get("/search", response_model=List[CarWashSchema])
async def search_car_washes_endpoint(
    q: str = Query(..., min_length=2, description="Termo de busca"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Busca lava-jatos por nome ou descrição"""
    car_washes = search_car_washes(db, query=q, skip=skip, limit=limit)
    return car_washes

@router.get("/{car_wash_id}", response_model=CarWashSchema)
async def get_car_wash_details(
    car_wash_id: str,
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um lava-jato específico"""
    car_wash = get_car_wash_by_id(db, car_wash_id)
    if not car_wash:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lava-jato não encontrado"
        )
    return car_wash

@router.get("/{car_wash_id}/services", response_model=CarWashWithServices)
async def get_car_wash_with_services_endpoint(
    car_wash_id: str,
    db: Session = Depends(get_db)
):
    """Obtém lava-jato com lista de serviços"""
    car_wash_with_services = get_car_wash_with_services(db, car_wash_id)
    if not car_wash_with_services:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lava-jato não encontrado"
        )
    return car_wash_with_services

# Endpoints administrativos (podem ser restringidos posteriormente)
@router.post("/", response_model=CarWashSchema, status_code=status.HTTP_201_CREATED)
async def create_car_wash_endpoint(
    car_wash_data: CarWashCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria um novo lava-jato (requer autenticação)"""
    car_wash = create_car_wash(db, car_wash_data)
    return car_wash

@router.put("/{car_wash_id}/rating", response_model=CarWashSchema)
async def update_car_wash_rating_endpoint(
    car_wash_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza a nota média do lava-jato (chamado automaticamente após avaliações)"""
    car_wash = update_car_wash_rating(db, car_wash_id)
    if not car_wash:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lava-jato não encontrado"
        )
    return car_wash

@router.delete("/{car_wash_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_car_wash_endpoint(
    car_wash_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desativa um lava-jato"""
    success = deactivate_car_wash(db, car_wash_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lava-jato não encontrado"
        )