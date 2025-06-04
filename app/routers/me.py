from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from app.models.user import User
from app.database import engine

router = APIRouter(prefix="/me", tags=["user"])


def get_session():
    with Session(engine) as session:
        yield session


@router.patch("/", response_model=User)
def update_profile(data: dict = Body(...), session: Session = Depends(get_session)):
    telegram_id = data.get("telegram_id")
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Требуется telegram_id")

    user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновим только поля, которые реально пришли (без id, telegram_id)
    for field in ["first_name", "last_name", "phone", "city"]:
        if field in data:
            setattr(user, field, data[field])

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
