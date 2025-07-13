from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from app.models.user import User
from app.database import engine

router = APIRouter(prefix="/users")


def get_session():
    with Session(engine) as session:
        yield session


# Модель PATCH-запроса для обновления любого поля
class UserUpdate(BaseModel):
    is_driver: Optional[bool] = None
    active_driver: Optional[bool] = None
    car_number: Optional[str] = None
    car_brand: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


@router.patch("/{user_id}", response_model=User)
def update_user_fields(
    user_id: int, data: UserUpdate, session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Обновляем только переданные поля
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/by_telegram/{telegram_id}")
def delete_user_by_telegram_id(
    telegram_id: int, session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"success": True, "detail": "User deleted by telegram_id"}


@router.delete("/delete_all")
def delete_all_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    for user in users:
        session.delete(user)
    session.commit()
    return {"success": True, "detail": "All users deleted"}


@router.get("/", response_model=list[User])
def get_all_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=User)
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/start_driver_trial")
def start_driver_trial(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.driver_trial_end and user.driver_trial_end > datetime.utcnow():
        raise HTTPException(status_code=400, detail="Триал уже активирован")
    user.active_driver = True
    user.driver_trial_end = datetime.utcnow() + timedelta(days=3)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"ok": True, "trial_end": user.driver_trial_end}
