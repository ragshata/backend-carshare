from sqlmodel import SQLModel, Field
from typing import Optional


class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int
    author_id: int  # Кто оставил отзыв (обычно пассажир)
    driver_id: int  # Кому (водителю)
    rating: int  # Оценка (1-5)
    text: Optional[str]  # Текст отзыва
    created_at: Optional[str] = None
