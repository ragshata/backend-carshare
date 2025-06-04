from sqlmodel import SQLModel, Field
from typing import Optional
from app.utils.time import get_utc_now 


class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: str = Field(default_factory=get_utc_now)
