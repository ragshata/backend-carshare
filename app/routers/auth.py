from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models.user import User
from app.database import engine
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from app.utils.auth import create_access_token  # обязательно должен быть

router = APIRouter(prefix="/auth")


def get_session():
    with Session(engine) as session:
        yield session


class TelegramAuthIn(BaseModel):
    telegram_id: int
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    photo_url: str = ""  # если нужно сохранять аву
#ghjcnj

@router.post("/telegram")
def auth_via_telegram(data: TelegramAuthIn, session: Session = Depends(get_session)):
    # Ищем по telegram_id
    user = session.exec(
        select(User).where(User.telegram_id == data.telegram_id)
    ).first()

    if not user:
        # Только если не найден — создаём нового
        user = User(
            telegram_id=data.telegram_id,
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            photo_url=data.photo_url,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        # Просто обнови нужные поля
        updated = False
        if user.first_name != data.first_name:
            user.first_name = data.first_name
            updated = True
        if user.last_name != data.last_name:
            user.last_name = data.last_name
            updated = True
        if user.username != data.username:
            user.username = data.username
            updated = True
        if hasattr(user, "photo_url") and user.photo_url != data.photo_url:
            user.photo_url = data.photo_url
            updated = True
        if updated:
            session.add(user)
            session.commit()
            session.refresh(user)
    # Возвращай только этого юзера!
    token = create_access_token(user.id)
    return {"access_token": token, "user": user}
