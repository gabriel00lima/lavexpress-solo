# app/crud/review.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from app.models.review import Review
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.schemas.review import ReviewCreate
from typing import List, Optional


def create_review(db: Session, review: ReviewCreate, user_id: str) -> Optional[Review]:
    """Cria uma nova avaliação"""
    # Verifica se o usuário já avaliou este lava-jato
    existing_review = db.query(Review).filter(
        and_(
            Review.user_id == user_id,
            Review.car_wash_id == review.car_wash_id
        )
    ).first()

    if existing_review:
        return None  # Usuário já avaliou

    # Se foi especificado um booking, verifica se pertence ao usuário e está concluído
    if review.booking_id:
        booking = db.query(Booking).filter(
            and_(
                Booking.id == review.booking_id,
                Booking.user_id == user_id,
                Booking.status == BookingStatus.CONCLUIDO
            )
        ).first()

        if not booking:
            return None  # Booking inválido

    db_review = Review(
        user_id=user_id,
        **review.dict()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # Atualiza a nota média do lava-jato
    from app.crud.car_wash import update_car_wash_rating
    update_car_wash_rating(db, str(review.car_wash_id))

    return db_review


def get_review_by_id(db: Session, review_id: str) -> Optional[Review]:
    """Busca avaliação por ID"""
    return db.query(Review).options(
        joinedload(Review.user)
    ).filter(Review.id == review_id).first()


def get_car_wash_reviews(
        db: Session,
        car_wash_id: str,
        skip: int = 0,
        limit: int = 100
) -> List[Review]:
    """Busca avaliações de um lava-jato"""
    return db.query(Review).options(
        joinedload(Review.user)
    ).filter(Review.car_wash_id == car_wash_id).order_by(desc(Review.criado_em)).offset(skip).limit(limit).all()


def get_user_reviews(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100
) -> List[Review]:
    """Busca avaliações de um usuário"""
    return db.query(Review).options(
        joinedload(Review.car_wash)
    ).filter(Review.user_id == user_id).order_by(desc(Review.criado_em)).offset(skip).limit(limit).all()


def get_review_stats(db: Session, car_wash_id: str) -> dict:
    """Retorna estatísticas detalhadas das avaliações"""
    stats = db.query(
        func.avg(Review.nota).label('nota_media'),
        func.count(Review.id).label('total_avaliacoes'),
        func.sum(func.case((Review.nota == 5, 1), else_=0)).label('nota_5'),
        func.sum(func.case((Review.nota == 4, 1), else_=0)).label('nota_4'),
        func.sum(func.case((Review.nota == 3, 1), else_=0)).label('nota_3'),
        func.sum(func.case((Review.nota == 2, 1), else_=0)).label('nota_2'),
        func.sum(func.case((Review.nota == 1, 1), else_=0)).label('nota_1'),
    ).filter(Review.car_wash_id == car_wash_id).first()

    return {
        'nota_media': round(float(stats.nota_media or 0), 1),
        'total_avaliacoes': int(stats.total_avaliacoes or 0),
        'distribuicao': {
            '5': int(stats.nota_5 or 0),
            '4': int(stats.nota_4 or 0),
            '3': int(stats.nota_3 or 0),
            '2': int(stats.nota_2 or 0),
            '1': int(stats.nota_1 or 0),
        }
    }


def update_review(db: Session, review_id: str, user_id: str, nota: int, comentario: str = None) -> Optional[Review]:
    """Atualiza uma avaliação"""
    review = db.query(Review).filter(
        and_(Review.id == review_id, Review.user_id == user_id)
    ).first()

    if not review:
        return None

    review.nota = nota
    if comentario is not None:
        review.comentario = comentario

    db.commit()
    db.refresh(review)

    # Atualiza a nota média do lava-jato
    from app.crud.car_wash import update_car_wash_rating
    update_car_wash_rating(db, str(review.car_wash_id))

    return review


def delete_review(db: Session, review_id: str, user_id: str) -> bool:
    """Remove uma avaliação"""
    review = db.query(Review).filter(
        and_(Review.id == review_id, Review.user_id == user_id)
    ).first()

    if not review:
        return False

    car_wash_id = review.car_wash_id
    db.delete(review)
    db.commit()

    # Atualiza a nota média do lava-jato
    from app.crud.car_wash import update_car_wash_rating
    update_car_wash_rating(db, str(car_wash_id))

    return True


def can_user_review(db: Session, user_id: str, car_wash_id: str) -> bool:
    """Verifica se o usuário pode avaliar o lava-jato"""
    # Verifica se já não avaliou
    existing_review = db.query(Review).filter(
        and_(Review.user_id == user_id, Review.car_wash_id == car_wash_id)
    ).first()

    if existing_review:
        return False

    # Verifica se tem pelo menos um agendamento concluído
    completed_booking = db.query(Booking).filter(
        and_(
            Booking.user_id == user_id,
            Booking.car_wash_id == car_wash_id,
            Booking.status == BookingStatus.CONCLUIDO
        )
    ).first()

    return completed_booking is not None


def get_recent_reviews(db: Session, limit: int = 10) -> List[Review]:
    """Busca avaliações mais recentes para exibir no feed"""
    return db.query(Review).options(
        joinedload(Review.user),
        joinedload(Review.car_wash)
    ).order_by(desc(Review.criado_em)).limit(limit).all()