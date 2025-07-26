from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime, timedelta
from app.models.booking import Booking
from app.models.user import User
from app.models.trip import Trip
from app.database import engine
from app.utils.telegram_notify import (
    send_new_booking_notification,
    send_telegram_message,
)
from pydantic import BaseModel

router = APIRouter(prefix="/bookings", tags=["bookings"])


def get_session():
    with Session(engine) as session:
        yield session


class BookingWithUser(BaseModel):
    id: int
    trip_id: int
    user_id: int
    status: Optional[str]
    created_at: Optional[str]
    created_at_for_timer: Optional[datetime]
    user: Optional[dict]

    class Config:
        orm_mode = True


def get_booking_datetime(booking: Booking) -> datetime:
    """
    Берём created_at_for_timer если оно есть, иначе пытаемся распарсить created_at (строку).
    """
    if getattr(booking, "created_at_for_timer", None):
        return booking.created_at_for_timer
    # created_at может быть строкой
    created_str = getattr(booking, "created_at", None)
    if created_str:
        try:
            return datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except Exception:
            pass
    return datetime.utcnow()  # fallback


@router.post("/", response_model=BookingWithUser)
def create_booking(booking: Booking, session: Session = Depends(get_session)):
    trip = session.get(Trip, booking.trip_id)
    user = session.get(User, booking.user_id)

    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if trip.seats <= 0:
        raise HTTPException(status_code=400, detail="Нет свободных мест")

    existing = session.exec(
        select(Booking).where(
            (Booking.trip_id == booking.trip_id) & (Booking.user_id == booking.user_id)
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже бронировали эту поездку!")

    trip.seats -= 1
    session.add(booking)
    session.commit()
    session.refresh(booking)

    driver = session.get(User, trip.owner_id)
    if driver and driver.telegram_id:
        send_new_booking_notification(driver.telegram_id, trip.id)

    return BookingWithUser(**booking.dict(), user=user.dict())


@router.get("/", response_model=List[BookingWithUser])
def get_bookings(
    user_id: Optional[int] = Query(None, description="ID пользователя"),
    trip_id: Optional[int] = Query(None, description="ID поездки"),
    session: Session = Depends(get_session),
):
    query = select(Booking)
    if user_id:
        query = query.where(Booking.user_id == user_id)
    if trip_id:
        query = query.where(Booking.trip_id == trip_id)
    bookings = session.exec(query).all()

    result = []
    for booking in bookings:
        user = session.get(User, booking.user_id)
        result.append(
            BookingWithUser(
                **booking.dict(),
                created_at=booking.created_at,
                created_at_for_timer=getattr(booking, "created_at_for_timer", None),
                user=user.dict() if user else None,
            )
        )
    return result


@router.delete("/{booking_id}", response_model=dict)
def delete_booking(booking_id: int, session: Session = Depends(get_session)):
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    trip = session.get(Trip, booking.trip_id)
    if trip:
        trip.seats += 1

    session.delete(booking)
    session.commit()
    return {"ok": True, "detail": "Бронирование отменено"}


@router.post("/{booking_id}/confirm", response_model=BookingWithUser)
def confirm_booking(booking_id: int, session: Session = Depends(get_session)):
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    booking.status = "confirmed"
    session.add(booking)
    session.commit()
    session.refresh(booking)
    user = session.get(User, booking.user_id)
    trip = session.get(Trip, booking.trip_id)

    if user and user.telegram_id and trip:
        msg = (
            f"✅ <b>Ваша заявка подтверждена!</b>\n"
            f"Поездка <b>{trip.from_} — {trip.to}</b> на {trip.date} {trip.time} подтверждена водителем."
        )
        send_telegram_message(user.telegram_id, msg)

    return BookingWithUser(**booking.dict(), user=user.dict() if user else None)


@router.post("/{booking_id}/reject", response_model=BookingWithUser)
def reject_booking(booking_id: int, session: Session = Depends(get_session)):
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    booking.status = "rejected"
    session.add(booking)
    session.commit()
    session.refresh(booking)
    user = session.get(User, booking.user_id)
    trip = session.get(Trip, booking.trip_id)

    if user and user.telegram_id and trip:
        msg = (
            f"❌ <b>Ваша заявка отклонена</b>\n"
            f"Поездка <b>{trip.from_} — {trip.to}</b> на {trip.date} {trip.time} отклонена водителем."
        )
        send_telegram_message(user.telegram_id, msg)

    return BookingWithUser(**booking.dict(), user=user.dict() if user else None)


@router.delete("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: int, user_id: int, session: Session = Depends(get_session)
):
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # --- Время берём из created_at_for_timer если есть
    created = get_booking_datetime(booking)
    if datetime.utcnow().replace(tzinfo=created.tzinfo) - created > timedelta(
        minutes=30
    ):
        raise HTTPException(
            status_code=400,
            detail="Отменить можно только в течение 30 минут после бронирования",
        )

    session.delete(booking)
    session.commit()
    return {"ok": True, "detail": "Booking cancelled"}
