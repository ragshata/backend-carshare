from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime, time


class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_: str = Field(alias="from_")
    to: str
    date: date
    time: time
    seats: int
    price: int
    owner_id: int = Field(foreign_key="user.id")
    status: str = Field(default="active")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    # NEW: валюта (ISO-код)
    currency: str = Field(default="TJS", max_length=5)
