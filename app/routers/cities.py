from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from typing import List

from app.models.city import City

router = APIRouter(prefix="/cities", tags=["Cities"])

# Дефолтные города
DEFAULT_CITIES = [
  "Бохтар","Бустон","Вахдат","Душанбе","Истаравшан","Истиклол","Исфара",
  "Гиссар","Гулистон","Канибадам","Куляб","Левакант","Нурек","Пенджикент",
  "Рогун","Турсунзаде","Хорог","Худжанд",
  "Мургаб","Фархор","Шахритус","Зафарабад","Балх","Гарм","Гафуров","Яван",
  "Шарора","Абдурахмони Джоми","Дангара","Дусти","Кубодиён","Московский",
  "Муминабад","Пяндж","Ховалинг","Хулбук","20-летия Независимости","Вахш",
  "Кировский","Обикиик","Орзу","Пархар","Хаётинав","Навкат","Мехнатобод",
  "Адрасман","Зарнисор","Зеравшан","Кансай","Варзоб","Чорбог","Такоб",
  "Симиганч","Дехмой","Навобод","Сангтуда","Чилгази","Кухистони Мастчох",
  "Патрук","Поршинев","Ванж","Рушан","Дарвоз","Шахринав","Лахш","Файзабад",
  "Джиликуль","Джайхун","Хуросон","Хамадони","Восе","Дангарин","Темурмалик",
  "Балджуван","Муминобод","Носири Хусрав","Джалолиддин Балхи","Спитамен",
  "Мастчох","Ашт","Бободжон Гафуров","Джаббор Расулов","Деваштич","Шахристан","Айни"
]

@router.get("/", response_model=list[str])
def get_cities(session: Session = Depends(get_session)):
    # города из базы
    db_cities = session.exec(select(City.name)).all()
    # объединяем дефолтные и из базы
    all_cities = sorted(set(DEFAULT_CITIES + list(db_cities)))
    return all_cities

# Добавить новый город
@router.post("/", response_model=City)
def add_city(city: City, session: Session = Depends(get_session)):
    db_city = session.exec(select(City).where(City.name == city.name)).first()
    if db_city:
        raise HTTPException(status_code=400, detail="Город уже существует")
    session.add(city)
    session.commit()
    session.refresh(city)
    return city


# Удалить город
@router.delete("/{city_id}")
def delete_city(city_id: int, session: Session = Depends(get_session)):
    city = session.get(City, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="Город не найден")
    session.delete(city)
    session.commit()
    return {"ok": True}

@router.get("/custom", response_model=list[str])
def get_custom_cities(session: Session = Depends(get_session)):
    """
    Возвращает только города, которых нет в дефолтном списке DEFAULT_CITIES.
    """
    all_cities = session.exec(select(City)).all()
    result = [
        city.name
        for city in all_cities
        if city.name not in DEFAULT_CITIES
    ]
    return result
