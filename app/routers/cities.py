from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.models import City
from app.database import get_session

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("/", response_model=List[City])
def get_cities(session: Session = Depends(get_session)):
    return session.exec(select(City).order_by(City.name)).all()


@router.post("/", response_model=City)
def add_city(city: City, session: Session = Depends(get_session)):
    existing = session.exec(select(City).where(City.name == city.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Город уже существует")
    session.add(city)
    session.commit()
    session.refresh(city)
    return city


@router.delete("/{city_id}")
def delete_city(city_id: int, session: Session = Depends(get_session)):
    city = session.get(City, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="Город не найден")
    session.delete(city)
    session.commit()
    return {"detail": "Город удалён"}
