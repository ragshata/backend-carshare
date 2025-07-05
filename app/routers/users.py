from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.models.user import User
from app.database import engine

router = APIRouter(prefix="/users")

def get_session():
    with Session(engine) as session:
        yield session

@router.patch("/{user_id}")
def update_user_role(user_id: int, payload: dict, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if "is_driver" in payload:
        user.is_driver = payload["is_driver"]
        session.add(user)
        session.commit()
        session.refresh(user)
    return user
