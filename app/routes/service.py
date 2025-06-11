# app/routes/service.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.service import Service as ServiceSchema, ServiceCreate
from app.crud.service import (
    create_service,
    get_service_by_id,
    get_services_by_car_wash,
    get_all_services,
    update_service,
    deactivate_service,
    search_services,
    get_services_by_price_range
)
from app.services.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[ServiceSchema])
async def list_all_services(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Lista todos os serviços ativos"""
    services = get_all_services(db, skip=skip, limit=limit)
    return services


@router.get("/search", response_model=List[ServiceSchema])
async def search_services_endpoint(
        q: str = Query(..., min_length=2, description="Termo de busca"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Busca serviços por nome ou descrição"""
    services = search_services(db, query=q, skip=skip, limit=limit)
    return services


@router.get("/price-range", response_model=List[ServiceSchema])
async def get_services_by_price_range_endpoint(
        min_price: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
        max_price: Optional[float] = Query(None, ge=0, description="Preço máximo"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Busca serviços por faixa de preço"""
    if max_price is not None and min_price is not None and max_price < min_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preço máximo deve ser maior que preço mínimo"
        )

    services = get_services_by_price_range(
        db,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit
    )
    return services


@router.get("/car-wash/{car_wash_id}", response_model=List[ServiceSchema])
async def get_services_by_car_wash_endpoint(
        car_wash_id: str,
        db: Session = Depends(get_db)
):
    """Lista serviços de um lava-jato específico"""
    services = get_services_by_car_wash(db, car_wash_id)
    return services


@router.get("/{service_id}", response_model=ServiceSchema)
async def get_service_details(
        service_id: str,
        db: Session = Depends(get_db)
):
    """Obtém detalhes de um serviço específico"""
    service = get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
    return service


# Endpoints administrativos
@router.post("/", response_model=ServiceSchema, status_code=status.HTTP_201_CREATED)
async def create_service_endpoint(
        service_data: ServiceCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Cria um novo serviço (requer autenticação)"""
    # TODO: Verificar se usuário tem permissão para criar serviços para este lava-jato
    service = create_service(db, service_data)
    return service


@router.put("/{service_id}", response_model=ServiceSchema)
async def update_service_endpoint(
        service_id: str,
        service_data: dict,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Atualiza um serviço existente"""
    # TODO: Verificar se usuário tem permissão para editar este serviço
    service = update_service(db, service_id, service_data)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_service_endpoint(
        service_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Desativa um serviço"""
    # TODO: Verificar se usuário tem permissão para desativar este serviço
    success = deactivate_service(db, service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )