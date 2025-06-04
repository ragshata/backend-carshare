from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from app.models.review import Review
from app.models.user import User
from app.database import engine
from datetime import datetime, timezone

router = APIRouter(prefix="/reviews", tags=["reviews"])


def get_session():
    with Session(engine) as session:
        yield session


@router.post("/", response_model=Review)
def create_review(review: Review, session: Session = Depends(get_session)):
    # Проверка: пользователь не может оставить отзыв сам себе
    if review.author_id == review.driver_id:
        raise HTTPException(status_code=400, detail="Нельзя оставить отзыв самому себе")
    # Поездка, водитель и автор должны существовать (лучше добавить проверки)
    review.created_at = datetime.now(timezone.utc).isoformat()
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


@router.get("/driver/{driver_id}", response_model=List[Review])
def get_driver_reviews(driver_id: int, session: Session = Depends(get_session)):
    reviews = session.exec(select(Review).where(Review.driver_id == driver_id)).all()
    return reviews
