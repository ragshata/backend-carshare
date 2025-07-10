from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, SQLModel, Field
from typing import Optional, List
from app.database import engine

router = APIRouter(prefix="/reviews", tags=["reviews"])


# --- Модель отзыва (если у тебя нет отдельного файла models/review.py, можно оставить тут)
class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int
    author_id: int  # пассажир, кто оставил отзыв
    driver_id: int  # водитель, кому отзыв
    rating: int  # 1-5
    text: Optional[str] = None
    created_at: Optional[str] = None  # если нужна дата, иначе убери


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
