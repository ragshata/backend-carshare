from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.models.tariff import Tariff
from app.models.subscription import Subscription
from datetime import datetime, timedelta

router = APIRouter()


# Получить список тарифов
@router.get("/tariffs")
def get_tariffs(session: Session = Depends(get_session)):
    return session.exec(select(Tariff)).all()


# Начать пробный период
@router.post("/subscriptions/trial")
def start_driver_trial(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.driver_trial_end:
        raise HTTPException(status_code=400, detail="Trial already used")

    # Активируем пробный период (3 дня)
    trial_end = datetime.utcnow() + timedelta(days=3)
    user.active_driver = True
    user.driver_trial_end = trial_end
    session.add(user)
    session.commit()
    return {"trial_end": trial_end}


# Купить тариф
@router.post("/subscriptions/buy")
def buy_tariff(user_id: int, tariff_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    tariff = session.get(Tariff, tariff_id)

    if not user or not tariff:
        raise HTTPException(status_code=404, detail="User or tariff not found")

    # Активируем подписку
    sub_end = datetime.utcnow() + timedelta(days=tariff.duration_days)
    user.active_driver = True
    user.subscription_end = sub_end

    # Логируем покупку
    subscription = Subscription(user_id=user.id, tariff_id=tariff.id, ends_at=sub_end)
    session.add_all([user, subscription])
    session.commit()
    return {"subscription_end": sub_end}
