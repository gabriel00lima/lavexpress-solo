# app/routes/booking.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time
from app.database import get_db
from app.schemas.booking import (
    Booking as BookingSchema,
    BookingCreate,
    BookingUpdate,
    BookingWithDetails
)
from app.models.booking import BookingStatus
from app.crud.booking import (
    create_booking,
    get_booking_by_id,
    get_user_bookings,
    get_car_wash_bookings,
    get_booking_with_details,
    update_booking_status,
    update_booking,
    check_availability,
    get_available_times,
    cancel_booking,
    get_upcoming_bookings
)
from app.services.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=BookingSchema, status_code=status.HTTP_201_CREATED)
async def create_booking_endpoint(
        booking_data: BookingCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Cria um novo agendamento"""

    # Verifica disponibilidade do horário
    is_available = check_availability(
        db,
        car_wash_id=str(booking_data.car_wash_id),
        service_id=str(booking_data.service_id),
        target_date=booking_data.data,
        target_time=booking_data.hora
    )

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Horário não disponível"
        )

    booking = create_booking(db, booking_data, str(current_user.id))
    return booking


@router.get("/me", response_model=List[BookingSchema])
async def get_my_bookings(
        status_filter: Optional[BookingStatus] = Query(None, description="Filtrar por status"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Lista agendamentos do usuário logado"""
    bookings = get_user_bookings(
        db,
        user_id=str(current_user.id),
        status=status_filter,
        skip=skip,
        limit=limit
    )
    return bookings


@router.get("/upcoming", response_model=List[BookingSchema])
async def get_upcoming_bookings_endpoint(
        days_ahead: int = Query(7, ge=1, le=30, description="Dias à frente para buscar"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Busca agendamentos próximos (para notificações)"""
    bookings = get_upcoming_bookings(db, days_ahead=days_ahead)
    # Filtra apenas os agendamentos do usuário atual
    user_bookings = [b for b in bookings if str(b.user_id) == str(current_user.id)]
    return user_bookings


@router.get("/availability/{car_wash_id}")
async def check_availability_endpoint(
        car_wash_id: str,
        service_id: str = Query(..., description="ID do serviço"),
        target_date: date = Query(..., description="Data desejada"),
        target_time: time = Query(..., description="Horário desejado"),
        db: Session = Depends(get_db)
):
    """Verifica disponibilidade de um horário específico"""
    is_available = check_availability(
        db,
        car_wash_id=car_wash_id,
        service_id=service_id,
        target_date=target_date,
        target_time=target_time
    )

    return {
        "available": is_available,
        "car_wash_id": car_wash_id,
        "service_id": service_id,
        "date": target_date,
        "time": target_time
    }


@router.get("/available-times/{car_wash_id}")
async def get_available_times_endpoint(
        car_wash_id: str,
        target_date: date = Query(..., description="Data desejada"),
        service_duration: int = Query(60, ge=30, le=240, description="Duração do serviço em minutos"),
        db: Session = Depends(get_db)
):
    """Obtém horários disponíveis para uma data específica"""
    available_times = get_available_times(
        db,
        car_wash_id=car_wash_id,
        target_date=target_date,
        service_duration=service_duration
    )

    return {
        "car_wash_id": car_wash_id,
        "date": target_date,
        "available_times": available_times
    }


@router.get("/{booking_id}", response_model=BookingSchema)
async def get_booking_details(
        booking_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Obtém detalhes de um agendamento específico"""
    booking = get_booking_by_id(db, booking_id, str(current_user.id))
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    return booking


@router.get("/{booking_id}/details")
async def get_booking_with_details_endpoint(
        booking_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Obtém agendamento com detalhes completos (lava-jato, serviço, etc.)"""
    booking_details = get_booking_with_details(db, booking_id)
    if not booking_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )

    # Verifica se o agendamento pertence ao usuário
    if str(booking_details["booking"].user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )

    return booking_details


@router.put("/{booking_id}", response_model=BookingSchema)
async def update_booking_endpoint(
        booking_id: str,
        booking_update: BookingUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Atualiza um agendamento"""
    booking = update_booking(db, booking_id, booking_update, str(current_user.id))
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    return booking


@router.put("/{booking_id}/status", response_model=BookingSchema)
async def update_booking_status_endpoint(
        booking_id: str,
        new_status: BookingStatus,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Atualiza status de um agendamento"""
    booking = update_booking_status(db, booking_id, new_status, str(current_user.id))
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking_endpoint(
        booking_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Cancela um agendamento"""
    success = cancel_booking(db, booking_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado ou não pode ser cancelado"
        )


# Endpoints administrativos para lava-jatos
@router.get("/car-wash/{car_wash_id}", response_model=List[BookingSchema])
async def get_car_wash_bookings_endpoint(
        car_wash_id: str,
        target_date: Optional[date] = Query(None, description="Data específica"),
        status_filter: Optional[BookingStatus] = Query(None, description="Filtrar por status"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Lista agendamentos de um lava-jato (administrativo)"""
    # TODO: Verificar se usuário tem permissão para ver agendamentos deste lava-jato
    bookings = get_car_wash_bookings(
        db,
        car_wash_id=car_wash_id,
        target_date=target_date,
        status=status_filter,
        skip=skip,
        limit=limit
    )
    return bookings