from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


from app.database import init_db
from app.routers import admin, auth, reviews, trips, bookings, me, dev_users, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

#check
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или укажи конкретный домен: ["https://ca-rshare.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(auth.router)
app.include_router(reviews.router)
app.include_router(trips.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(me.router) 
app.include_router(dev_users.router)
app.include_router(users.router)
