import os
from sqlmodel import SQLModel, create_engine, Session

# Абсолютный путь до базы данных
db_path = os.path.abspath("database/carshare.db")

# Убедимся, что папка существует
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Создаём движок
engine = create_engine(f"sqlite:///{db_path}", echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

# Вот функция для FastAPI Depends
def get_session():
    with Session(engine) as session:
        yield session
