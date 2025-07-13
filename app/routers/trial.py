from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.database import get_session
from app.models.user import User

router = APIRouter()


@router.post("/start_driver_trial")
def start_driver_trial(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверка: если уже был триал, не даём второй раз (опционально)
    if user.driver_trial_end:
        raise HTTPException(
            status_code=400, detail="Триальный период уже был активирован."
        )

    user.active_driver = True
    # Сохраняем дату окончания триала (через 3 дня)
    user.driver_trial_end = (datetime.utcnow() + timedelta(days=3)).isoformat()
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"ok": True, "trial_end": user.driver_trial_end}
