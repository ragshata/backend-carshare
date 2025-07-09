from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel
from app.models.user import User
from app.database import engine

router = APIRouter(prefix="/users")


def get_session():
    with Session(engine) as session:
        yield session


# Для PATCH запроса — модель для обновления
class UserRolePatch(BaseModel):
    is_driver: bool
    car_number: Optional[str] = None
    car_brand: Optional[str] = None


@router.patch("/{user_id}", response_model=User)
def update_user_role(
    user_id: int, payload: UserRolePatch, session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_driver = payload.is_driver
    if payload.car_number is not None:
        user.car_number = payload.car_number
    if payload.car_brand is not None:
        user.car_brand = payload.car_brand
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Получить пользователя по id (с car_number и car_brand)
@router.get("/{user_id}", response_model=User)
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
