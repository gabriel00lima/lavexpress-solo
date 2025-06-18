from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc, or_
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.models.car_wash import CarWash
from app.models.service import Service
from app.schemas.booking import BookingCreate, BookingUpdate
from typing import List, Optional
from datetime import date, time, datetime, timedelta


def create_booking(db: Session, booking: BookingCreate, user_id: str) -> Booking:
    db_booking = Booking(user_id=user_id, **booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def get_booking_by_id(db: Session, booking_id: str, user_id: str = None) -> Optional[Booking]:
    query = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.car_wash),
        joinedload(Booking.service)
    ).filter(Booking.id == booking_id)

    if user_id:
        query = query.filter(Booking.user_id == user_id)

    return query.first()


def get_user_bookings(
        db: Session,
        user_id: str,
        status: Optional[BookingStatus] = None,
        skip: int = 0,
        limit: int = 100
) -> List[Booking]:
    query = db.query(Booking).options(
        joinedload(Booking.car_wash),
        joinedload(Booking.service)
    ).filter(Booking.user_id == user_id)

    if status:
        query = query.filter(Booking.status == status.value)  # <-- CORREÇÃO

    return query.order_by(desc(Booking.data), desc(Booking.hora)).offset(skip).limit(limit).all()


def get_car_wash_bookings(
        db: Session,
        car_wash_id: str,
        target_date: Optional[date] = None,
        status: Optional[BookingStatus] = None,
        skip: int = 0,
        limit: int = 100
) -> List[Booking]:
    query = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.service)
    ).filter(Booking.car_wash_id == car_wash_id)

    if target_date:
        query = query.filter(Booking.data == target_date)

    if status:
        query = query.filter(Booking.status == status.value)  # <-- CORREÇÃO

    return query.order_by(Booking.data, Booking.hora).offset(skip).limit(limit).all()


def get_booking_with_details(db: Session, booking_id: str) -> Optional[dict]:
    booking = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.car_wash),
        joinedload(Booking.service)
    ).filter(Booking.id == booking_id).first()

    if not booking:
        return None

    return {
        "booking": booking,
        "car_wash": booking.car_wash,
        "service": booking.service,
        "user": booking.user
    }


def update_booking_status(
        db: Session,
        booking_id: str,
        new_status: BookingStatus,
        user_id: str = None
) -> Optional[Booking]:
    query = db.query(Booking).filter(Booking.id == booking_id)

    if user_id:
        query = query.filter(Booking.user_id == user_id)

    booking = query.first()
    if not booking:
        return None

    booking.status = new_status
    db.commit()
    db.refresh(booking)
    return booking


def update_booking(
        db: Session,
        booking_id: str,
        booking_update: BookingUpdate,
        user_id: str
) -> Optional[Booking]:
    booking = db.query(Booking).filter(
        and_(Booking.id == booking_id, Booking.user_id == user_id)
    ).first()

    if not booking:
        return None

    update_data = booking_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(booking, field):
            setattr(booking, field, value)

    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(db: Session, booking_id: str, user_id: str) -> bool:
    booking = db.query(Booking).filter(
        and_(
            Booking.id == booking_id,
            Booking.user_id == user_id,
            Booking.status.in_([BookingStatus.PENDENTE, BookingStatus.CONFIRMADO])
        )
    ).first()

    if not booking:
        return False

    booking.status = BookingStatus.CANCELADO
    db.commit()
    return True


def check_availability(
        db: Session,
        car_wash_id: str,
        service_id: str,
        target_date: date,
        target_time: time
) -> bool:
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return False

    service_duration = timedelta(minutes=service.duracao_minutos)
    start_datetime = datetime.combine(target_date, target_time)
    end_datetime = start_datetime + service_duration

    conflicting_bookings = db.query(Booking).filter(
        and_(
            Booking.car_wash_id == car_wash_id,
            Booking.data == target_date,
            Booking.status.in_([BookingStatus.PENDENTE, BookingStatus.CONFIRMADO]),
            or_(
                and_(
                    Booking.hora <= target_time,
                    func.addtime(Booking.hora, func.sec_to_time(Service.duracao_minutos * 60)) > target_time
                ),
                and_(
                    Booking.hora < end_datetime.time(),
                    func.addtime(Booking.hora, func.sec_to_time(Service.duracao_minutos * 60)) >= end_datetime.time()
                ),
                and_(
                    Booking.hora >= target_time,
                    Booking.hora < end_datetime.time()
                )
            )
        )
    ).join(Service, Booking.service_id == Service.id).first()

    return conflicting_bookings is None


def get_available_times(
        db: Session,
        car_wash_id: str,
        target_date: date,
        service_duration: int = 60
) -> List[str]:
    car_wash = db.query(CarWash).filter(CarWash.id == car_wash_id).first()
    if not car_wash or not car_wash.aberto_de or not car_wash.aberto_ate:
        return []

    existing_bookings = db.query(Booking).options(
        joinedload(Booking.service)
    ).filter(
        and_(
            Booking.car_wash_id == car_wash_id,
            Booking.data == target_date,
            Booking.status.in_([BookingStatus.PENDENTE, BookingStatus.CONFIRMADO])
        )
    ).all()

    available_times = []
    current_time = car_wash.aberto_de
    end_time = car_wash.aberto_ate

    while current_time < end_time:
        is_available = True
        service_end = (datetime.combine(target_date, current_time) +
                       timedelta(minutes=service_duration)).time()

        if service_end > end_time:
            break

        for booking in existing_bookings:
            booking_start = booking.hora
            booking_end = (datetime.combine(target_date, booking.hora) +
                           timedelta(minutes=booking.service.duracao_minutos)).time()

            if (current_time < booking_end and service_end > booking_start):
                is_available = False
                break

        if is_available:
            available_times.append(current_time.strftime("%H:%M"))

        current_time = (datetime.combine(target_date, current_time) +
                        timedelta(minutes=30)).time()

    return available_times


def get_upcoming_bookings(db: Session, days_ahead: int = 7) -> List[Booking]:
    end_date = date.today() + timedelta(days=days_ahead)

    return db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.car_wash),
        joinedload(Booking.service)
    ).filter(
        and_(
            Booking.data.between(date.today(), end_date),
            Booking.status.in_([BookingStatus.PENDENTE, BookingStatus.CONFIRMADO])
        )
    ).order_by(Booking.data, Booking.hora).all()


def get_bookings_for_reminder(db: Session, reminder_date: date) -> List[Booking]:
    return db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.car_wash),
        joinedload(Booking.service)
    ).filter(
        and_(
            Booking.data == reminder_date,
            Booking.status == BookingStatus.CONFIRMADO
        )
    ).all()