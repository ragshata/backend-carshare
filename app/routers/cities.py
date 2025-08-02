from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from typing import List

from app.models.city import City

router = APIRouter(prefix="/cities", tags=["Cities"])


# Получить список городов
@router.get("/", response_model=List[City])
def get_cities(session: Session = Depends(get_session)):
    cities = session.exec(select(City)).all()
    return cities


# Добавить новый город
@router.post("/", response_model=City)
def add_city(city: City, session: Session = Depends(get_session)):
    db_city = session.exec(select(City).where(City.name == city.name)).first()
    if db_city:
        raise HTTPException(status_code=400, detail="Город уже существует")
    session.add(city)
    session.commit()
    session.refresh(city)
    return city


# Удалить город
@router.delete("/{city_id}")
def delete_city(city_id: int, session: Session = Depends(get_session)):
    city = session.get(City, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="Город не найден")
    session.delete(city)
    session.commit()
    return {"ok": True}
