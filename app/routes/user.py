# app/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.user import User as UserSchema, UserUpdate, UserLocation
from app.crud.user import (
    get_user_by_id, 
    update_user, 
    update_user_location, 
    deactivate_user,
    get_users
)
from app.services.core.dependencies import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(current_user: UserSchema = Depends(get_current_user)):
    """Obtém perfil do usuário logado"""
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza perfil do usuário logado"""
    updated_user = update_user(db, str(current_user.id), user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return updated_user

@router.put("/me/location", response_model=UserSchema)
async def update_user_location_endpoint(
    location: UserLocation,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza localização do usuário"""
    updated_user = update_user_location(
        db, 
        str(current_user.id), 
        location.latitude, 
        location.longitude
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return updated_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_current_user(
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desativa conta do usuário logado"""
    success = deactivate_user(db, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id_endpoint(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)  # Requer autenticação
):
    """Obtém usuário por ID (requer autenticação)"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user

# Endpoint administrativo (pode ser removido ou restrito)
@router.get("/", response_model=List[UserSchema])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Lista usuários (endpoint administrativo)"""
    users = get_users(db, skip=skip, limit=limit)
    return users