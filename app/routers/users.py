from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel
from app.models.user import User
from app.database import engine

router = APIRouter(prefix="/users")


def get_session():
    with Session(engine) as session:
        yield session


# Pydantic модель для безопасности
class UserRolePatch(BaseModel):
    is_driver: bool


@router.patch("/{user_id}", response_model=User)
def update_user_role(
    user_id: int, payload: UserRolePatch, session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_driver = payload.is_driver
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
