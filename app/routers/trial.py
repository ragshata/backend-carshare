from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.database import get_session
from app.models.user import User

router = APIRouter()


class TrialRequest(BaseModel):
    user_id: int


@router.post("/start_driver_trial")
def start_driver_trial(data: TrialRequest, session: Session = Depends(get_session)):
    user = session.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.active_driver:
        return {
            "detail": "Пробный период уже активирован",
            "trial_end": user.driver_trial_end,
        }
    now = datetime.utcnow()
    trial_end = now + timedelta(days=3)
    user.active_driver = True
    user.driver_trial_end = trial_end  # Важно! Тут объект datetime, не строка
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"detail": "Trial activated", "trial_end": trial_end.isoformat()}
