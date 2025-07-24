from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    tariff_id: int = Field(foreign_key="tariff.id")
    ends_at: datetime
