from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.models.review import Review
from app.database import get_session
from datetime import datetime, timezone

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=Review)
def create_review(review: Review, session: Session = Depends(get_session)):
    if review.author_id == review.driver_id:
        raise HTTPException(status_code=400, detail="Нельзя оставить отзыв самому себе")
    review.created_at = datetime.now(timezone.utc).isoformat()
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


@router.get("/driver/{driver_id}/", response_model=List[Review])
def get_driver_reviews(driver_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Review).where(Review.driver_id == driver_id)).all()


@router.get("/", response_model=List[Review])
def get_all_reviews(session: Session = Depends(get_session)):
    return session.exec(select(Review)).all()


@router.delete("/{review_id}/")
def delete_review(review_id: int, session: Session = Depends(get_session)):
    try:
        review = session.get(Review, review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Отзыв не найден")
        session.delete(review)
        session.commit()
        return {"detail": "Отзыв удалён"}
    except Exception as e:
        session.rollback()
        print("Ошибка удаления отзыва:", e)
        raise HTTPException(status_code=500, detail="Ошибка при удалении отзыва")
