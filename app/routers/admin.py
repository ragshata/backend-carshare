# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.models.user import User
from app.database import engine

router = APIRouter(prefix="/admin")

def get_session():
    with Session(engine) as session:
        yield session

# -- Доступ к админке по telegram_id (минимальная реализация)
ADMIN_IDS = [6931781449, 6931781449]  # твои telegram_id админов

def admin_required(telegram_id: int):
    if telegram_id not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Not admin")

# -- Поиск пользователей (по id или username)
@router.get("/users")
def search_users(
    telegram_id: int,  # Админ id для проверки
    user_id: int = Query(None), 
    username: str = Query(None),
    session: Session = Depends(get_session)
):
    admin_required(telegram_id)
    q = select(User)
    if user_id:
        q = q.where(User.id == user_id)
    if username:
        q = q.where(User.username == username)
    return session.exec(q).all()

# -- Изменение роли и active_driver
@router.patch("/users/{user_id}")
def patch_user(
    user_id: int, 
    data: dict, 
    telegram_id: int,  # Админ id для проверки
    session: Session = Depends(get_session)
):
    admin_required(telegram_id)
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if "is_driver" in data:
        user.is_driver = data["is_driver"]
    if "active_driver" in data:
        user.active_driver = data["active_driver"]
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
