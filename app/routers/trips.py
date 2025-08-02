from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional, List
from datetime import date, time, datetime

from app.models.city import City
from app.utils.telegram_notify import send_telegram_message_rate
from app.models.booking import Booking
from app.models.trip import Trip
from app.database import engine
from app.models.user import User

router = APIRouter(prefix="/trips", tags=["trips"])


def get_session():
    with Session(engine) as session:
        yield session


@router.patch("/{trip_id}/finish")
def finish_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip.status = "done"
    session.add(trip)
    session.commit()
    session.refresh(trip)

    # Получить всех пассажиров с confirmed booking
    bookings = session.exec(
        select(Booking).where(
            (Booking.trip_id == trip_id) & (Booking.status == "confirmed")
        )
    ).all()
    for booking in bookings:
        passenger = session.get(User, booking.user_id)
        if passenger and passenger.telegram_id:
            send_telegram_message_rate(
                user_tg_id=passenger.telegram_id,
                driver_id=trip.owner_id,
                trip_id=trip.id,
            )
    return trip


@router.get("/{trip_id}/passengers", response_model=List[User])
def get_trip_passengers(trip_id: int, session: Session = Depends(get_session)):
    bookings = session.exec(
        select(Booking).where(
            (Booking.trip_id == trip_id) & (Booking.status == "confirmed")
        )
    ).all()
    user_ids = [b.user_id for b in bookings]
    if not user_ids:
        return []
    users = session.exec(select(User).where(User.id.in_(user_ids))).all()
    return users


@router.delete("/{trip_id}", response_model=Trip)
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    session.delete(trip)
    session.commit()
    return trip


@router.get("/", response_model=List[Trip])
def list_trips(
    session: Session = Depends(get_session),
    from_: Optional[str] = Query(None, description="Город отправления"),
    to: Optional[str] = Query(None, description="Город прибытия"),
    date: Optional[str] = Query(None, description="Дата поездки (YYYY-MM-DD)"),
    date_from: Optional[str] = Query(None, description="Дата с (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Дата по (YYYY-MM-DD)"),
    status: Optional[str] = Query(
        None, description="Статус поездки (active/archived/...)"
    ),
    maxPrice: Optional[float] = Query(None, description="Максимальная цена"),
    driver_id: Optional[int] = Query(None, description="ID водителя"),
):
    query = select(Trip)
    if from_:
        query = query.where(Trip.from_ == from_)
    if to:
        query = query.where(Trip.to == to)
    if date:
        query = query.where(Trip.date == date)
    if date_from:
        query = query.where(Trip.date >= date_from)
    if date_to:
        query = query.where(Trip.date <= date_to)
    if status:
        query = query.where(Trip.status == status)
    if maxPrice:
        query = query.where(Trip.price <= maxPrice)
    if driver_id:
        query = query.where(Trip.owner_id == driver_id)

    trips = session.exec(query).all()
    return trips


@router.get("/{trip_id}", response_model=Trip)
def get_trip_by_id(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    return trip


@router.post("/", response_model=Trip)
def create_trip(trip: Trip, session: Session = Depends(get_session)):
    # Проверяем и добавляем города, если их нет
    def ensure_city(name: str):
        name = name.strip()
        existing = session.exec(select(City).where(City.name == name)).first()
        if not existing:
            new_city = City(name=name)
            session.add(new_city)
            session.commit()
            session.refresh(new_city)

    ensure_city(trip.from_)
    ensure_city(trip.to)

    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip



@router.patch("/{trip_id}", response_model=Trip)
def update_trip(trip_id: int, data: dict, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    for k, v in data.items():
        # Автоматически парсим строку в date/time
        if k == "date" and isinstance(v, str):
            v = date.fromisoformat(v)
        if k == "time" and isinstance(v, str):
            # Допускаем формат "21:05:00" или "21:05"
            try:
                v = time.fromisoformat(v)
            except Exception:
                v = datetime.strptime(v, "%H:%M").time()
        setattr(trip, k, v)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip
