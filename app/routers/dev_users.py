# app/routers/dev_users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.user import User
from app.database import engine

router = APIRouter(prefix="/dev-users", tags=["dev-users"])


def get_session():
    with Session(engine) as session:
        yield session


@router.post("/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    # Проверим, нет ли такого telegram_id уже
    if user.telegram_id:
        exists = session.exec(
            select(User).where(User.telegram_id == user.telegram_id)
        ).first()
        if exists:
            raise HTTPException(
                status_code=400, detail="Такой telegram_id уже существует"
            )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
