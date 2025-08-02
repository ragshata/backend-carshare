from sqlmodel import SQLModel, Field
from typing import Optional


class City(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(index=True, unique=True)
