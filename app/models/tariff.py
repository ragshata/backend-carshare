from sqlmodel import SQLModel, Field
from typing import Optional


class Tariff(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    duration_days: int
    price: int
    description: Optional[str] = None
