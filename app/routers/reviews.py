from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, SQLModel, Field
from typing import Optional, List
from app.database import engine
from app.models.review import Review

router = APIRouter(prefix="/reviews", tags=["reviews"])


def get_session():
    with Session(engine) as session:
        yield session


# --- Создать отзыв
@router.post("/", response_model=Review)
def create_review(review: Review, session: Session = Depends(get_session)):
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


# --- Получить отзывы о конкретном водителе
@router.get("/driver/{driver_id}", response_model=List[Review])
def get_reviews_for_driver(driver_id: int, session: Session = Depends(get_session)):
    reviews = session.exec(select(Review).where(Review.driver_id == driver_id)).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="Нет отзывов для этого водителя")
    return reviews


# --- Получить отзывы по поездке (необязательно, но удобно)
@router.get("/trip/{trip_id}", response_model=List[Review])
def get_reviews_for_trip(trip_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Review).where(Review.trip_id == trip_id)).all()
