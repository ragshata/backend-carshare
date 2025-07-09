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


# Для PATCH запроса — модель для обновления
class UserRolePatch(BaseModel):
    is_driver: bool
    car_number: Optional[str] = None
    car_brand: Optional[str] = None
class UserUpdate(BaseModel):
    is_driver: bool | None = None
    active_driver: bool | None = None

@router.patch("/{user_id}", response_model=User)
def update_user_fields(user_id: int, data: UserUpdate, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated = False
    if data.is_driver is not None:
        user.is_driver = data.is_driver
        updated = True
    if data.active_driver is not None:
        user.active_driver = data.active_driver
        updated = True
    if updated:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"success": True, "detail": "User deleted"}

@router.delete("/delete_all")
def delete_all_users(session: Session = Depends(get_session)):
    session.exec(select(User)).delete(synchronize_session=False)
    session.commit()
    return {"success": True, "detail": "All users deleted"}


@router.get("/", response_model=list[User])
def get_all_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

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
