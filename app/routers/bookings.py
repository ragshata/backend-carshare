from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime, timedelta
from app.models.booking import Booking
from app.models.user import User
from app.models.trip import Trip
from app.database import engine

# Импортируем функцию отправки уведомления (сделай такую функцию в utils/telegram_notify.py)
from app.utils.telegram_notify import (
    send_new_booking_notification,
    send_telegram_message,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


def get_session():
    with Session(engine) as session:
        yield session


# ——— Расширенная модель для выдачи брони с данными о user
from pydantic import BaseModel


class BookingWithUser(BaseModel):
    id: int
    trip_id: int
    user_id: int
    status: Optional[str]
    user: Optional[dict]

    class Config:
        orm_mode = True


# ——— Создать бронь
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

    # --- Проверка: есть ли уже бронь этого пользователя на эту поездку
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

    # ——— Оповещение водителя с inline-кнопкой
    driver = session.get(User, trip.owner_id)
    if driver and driver.telegram_id:
        send_new_booking_notification(driver.telegram_id, trip.id)

    # ——— Вернуть user как вложенный объект
    return BookingWithUser(**booking.dict(), user=user.dict())


# ——— Получить бронирования (по пользователю или по поездке)
@router.get("/", response_model=List[BookingWithUser])
def get_bookings(
    user_id: Optional[int] = Query(
        None, description="ID пользователя (фильтр по пассажиру)"
    ),
    trip_id: Optional[int] = Query(None, description="ID поездки (фильтр по поездке)"),
    session: Session = Depends(get_session),
):
    query = select(Booking)
    if user_id:
        query = query.where(Booking.user_id == user_id)
    if trip_id:
        query = query.where(Booking.trip_id == trip_id)
    bookings = session.exec(query).all()
    # ——— Для каждой брони добавить user
    result = []
    for booking in bookings:
        user = session.get(User, booking.user_id)
        result.append(
            BookingWithUser(**booking.dict(), user=user.dict() if user else None)
        )
    return result


# ——— Удалить бронирование
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


# ——— Подтвердить бронирование
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

    # ——— Оповещение пассажира
    if user and user.telegram_id and trip:
        msg = (
            f"✅ <b>Ваша заявка подтверждена!</b>\n"
            f"Поездка <b>{trip.from_} — {trip.to}</b> на {trip.date} {trip.time} подтверждена водителем."
        )
        send_telegram_message(user.telegram_id, msg)

    return BookingWithUser(**booking.dict(), user=user.dict() if user else None)


# ——— Отклонить бронирование
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

    # ——— Оповещение пассажира
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

    # Проверяем, что пользователь является автором бронирования
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Проверяем время
    if datetime.utcnow() - booking.created_at > timedelta(minutes=30):
        raise HTTPException(
            status_code=400,
            detail="Отменить можно только в течение 30 минут после бронирования",
        )

    session.delete(booking)
    session.commit()
    return {"ok": True, "detail": "Booking cancelled"}
