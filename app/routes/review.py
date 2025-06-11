# app/routes/review.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.review import Review as ReviewSchema, ReviewCreate
from app.crud.review import (
    create_review,
    get_review_by_id,
    get_car_wash_reviews,
    get_user_reviews,
    get_review_stats,
    update_review,
    delete_review,
    can_user_review,
    get_recent_reviews
)
from app.services.core.dependencies import get_current_user, get_optional_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review_endpoint(
        review_data: ReviewCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Cria uma nova avaliação"""

    # Verifica se usuário pode avaliar
    can_review = can_user_review(db, str(current_user.id), str(review_data.car_wash_id))
    if not can_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já avaliou este lava-jato ou não possui agendamentos concluídos"
        )

    review = create_review(db, review_data, str(current_user.id))
    if not review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a avaliação"
        )
    return review


@router.get("/me", response_model=List[ReviewSchema])
async def get_my_reviews(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Lista avaliações do usuário logado"""
    reviews = get_user_reviews(db, str(current_user.id), skip=skip, limit=limit)
    return reviews


@router.get("/recent", response_model=List[ReviewSchema])
async def get_recent_reviews_endpoint(
        limit: int = Query(10, ge=1, le=50, description="Número de avaliações recentes"),
        db: Session = Depends(get_db)
):
    """Obtém avaliações mais recentes (feed público)"""
    reviews = get_recent_reviews(db, limit=limit)
    return reviews


@router.get("/car-wash/{car_wash_id}", response_model=List[ReviewSchema])
async def get_car_wash_reviews_endpoint(
        car_wash_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Lista avaliações de um lava-jato específico"""
    reviews = get_car_wash_reviews(db, car_wash_id, skip=skip, limit=limit)
    return reviews


@router.get("/car-wash/{car_wash_id}/stats")
async def get_car_wash_review_stats(
        car_wash_id: str,
        db: Session = Depends(get_db)
):
    """Obtém estatísticas detalhadas das avaliações de um lava-jato"""
    stats = get_review_stats(db, car_wash_id)
    return stats


@router.get("/can-review/{car_wash_id}")
async def can_user_review_endpoint(
        car_wash_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Verifica se usuário pode avaliar um lava-jato"""
    can_review = can_user_review(db, str(current_user.id), car_wash_id)
    return {
        "can_review": can_review,
        "car_wash_id": car_wash_id,
        "user_id": str(current_user.id)
    }


@router.get("/{review_id}", response_model=ReviewSchema)
async def get_review_details(
        review_id: str,
        db: Session = Depends(get_db)
):
    """Obtém detalhes de uma avaliação específica"""
    review = get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada"
        )
    return review


@router.put("/{review_id}", response_model=ReviewSchema)
async def update_review_endpoint(
        review_id: str,
        nota: int = Query(..., ge=1, le=5, description="Nova nota (1-5)"),
        comentario: str = Query(None, description="Novo comentário"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Atualiza uma avaliação do usuário"""
    review = update_review(db, review_id, str(current_user.id), nota, comentario)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada ou você não tem permissão para editá-la"
        )
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review_endpoint(
        review_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Remove uma avaliação do usuário"""
    success = delete_review(db, review_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada ou você não tem permissão para removê-la"
        )