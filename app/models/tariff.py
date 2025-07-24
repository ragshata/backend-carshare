from sqlmodel import SQLModel, Field
from typing import Optional


class Tariff(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    duration_days: int  # срок действия в днях
