from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import engine
from app.models.trip import Trip
from app.models.booking import Booking
from app.models.review import Review
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


def get_session():
    with Session(engine) as session:
        yield session


# --- Аналитика ---
@router.get("/stats")
def admin_stats(session: Session = Depends(get_session)):
    trips_count = session.exec(select(Trip)).count()
    bookings_count = session.exec(select(Booking)).count()
    users_count = session.exec(select(User)).count()
    # Считаем средний рейтинг водителей
    reviews = session.exec(select(Review)).all()
    ratings = [review.rating for review in reviews if review.rating]
    avg_driver_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0
    return {
        "trips_count": trips_count,
        "bookings_count": bookings_count,
        "users_count": users_count,
        "avg_driver_rating": avg_driver_rating,
    }


# --- Список поездок ---
@router.get("/trips", response_model=List[Trip])
def admin_trips(session: Session = Depends(get_session)):
    return session.exec(select(Trip)).all()


# --- Список отзывов ---
@router.get("/reviews", response_model=List[Review])
def admin_reviews(session: Session = Depends(get_session)):
    return session.exec(select(Review)).all()


# --- Список пользователей ---
@router.get("/users", response_model=List[User])
def admin_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


# --- Удалить поездку ---
@router.delete("/trips/{trip_id}")
def admin_delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    session.delete(trip)
    session.commit()
    return {"ok": True, "detail": "Trip deleted"}


# --- Удалить отзыв ---
@router.delete("/reviews/{review_id}")
def admin_delete_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    session.delete(review)
    session.commit()
    return {"ok": True, "detail": "Review deleted"}


# --- Удалить пользователя ---
@router.delete("/users/{user_id}")
def admin_delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True, "detail": "User deleted"}
