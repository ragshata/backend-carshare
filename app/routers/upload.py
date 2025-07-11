from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlmodel import Session
from app.models.user import User
from app.database import engine
import shutil
import os

router = APIRouter(prefix="/upload", tags=["upload"])


def get_session():
    with Session(engine) as session:
        yield session


UPLOAD_DIR = "static/car_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/car_photo/{user_id}")
def upload_car_photo(
    user_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Генерируем путь для сохранения фото
    filename = f"user_{user_id}_car_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Обновляем url в профиле пользователя
    user.car_photo_url = f"/static/car_photos/{filename}"
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"url": user.car_photo_url}
