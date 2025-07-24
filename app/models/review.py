from sqlmodel import SQLModel, Field
from typing import Optional


class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    author_id: int  # Кто оставил отзыв
    driver_id: int  # Кому (водителю)
    rating: int
    text: Optional[str] = None
    created_at: Optional[str] = None
