from sqlmodel import SQLModel, Field
from typing import Optional
from app.utils.time import get_utc_now


class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int
    user_id: int
    status: str = Field(default="pending")
    created_at: Optional[str] = Field(default_factory=get_utc_now)
