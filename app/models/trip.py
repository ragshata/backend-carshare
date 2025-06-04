from sqlmodel import SQLModel, Field
from typing import Optional
from app.utils.time import get_utc_now
from datetime import datetime


class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_: str = Field(alias="from")
    to: str
    date: str
    time: str
    seats: int
    price: int
    owner_id: int = Field(foreign_key="user.id")
    status: str = Field(default="active")  # варианты: active, done, cancelled
    created_at: str = Field(default_factory=get_utc_now)
