from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    is_driver: Optional[bool] = False
    registered_at: Optional[str] = None
    city: Optional[str] = None
    active_driver: Optional[bool] = False
    car_number: Optional[str] = None
    car_brand: Optional[str] = None
