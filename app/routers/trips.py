# app/routers/trips
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional, List

from app.models.trip import Trip
from app.database import engine

router = APIRouter(prefix="/trips", tags=["trips"])


def get_session():
    with Session(engine) as session:
        yield session


@router.get("/", response_model=List[Trip])
def list_trips(
    session: Session = Depends(get_session),
    from_city: Optional[str] = Query(None, description="Город отправления"),
    to_city: Optional[str] = Query(None, description="Город прибытия"),
    date: Optional[str] = Query(None, description="Дата поездки (YYYY-MM-DD)"),
    date_from: Optional[str] = Query(None, description="Дата с (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Дата по (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Статус поездки (active/archived/...)"),
    maxPrice: Optional[float] = Query(None, description="Максимальная цена"),
    driver_id: Optional[int] = Query(None, description="ID водителя"),  
):
    query = select(Trip)
    if from_city:
        query = query.where(Trip.from_city == from_city)
    if to_city:
        query = query.where(Trip.to_city == to_city)
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
        query = query.where(Trip.driver_id == driver_id)   

    trips = session.exec(query).all()
    return trips



@router.get("/{trip_id}", response_model=Trip)
def get_trip_by_id(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Поездка не найдена")
    return trip
