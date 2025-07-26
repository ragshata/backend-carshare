from sqlmodel import Session, select
from app.database import engine
from app.models.tariff import Tariff


def init_tariffs():
    with Session(engine) as session:
        # Проверяем, есть ли тарифы
        existing = session.exec(select(Tariff)).all()
        if existing and len(existing) >= 3:
            print("Тарифы уже существуют, пропускаем.")
            return

        # Если нет – создаем
        default_tariffs = [
            Tariff(
                name="За 1 день",
                duration_days=1,
                price=10,
                description="Оплата на карту ...",
            ),
            Tariff(
                name="За 1 неделю",
                duration_days=7,
                price=50,
                description="Оплата на карту ...",
            ),
            Tariff(
                name="За 1 месяц",
                duration_days=30,
                price=150,
                description="Оплата на карту ...",
            ),
        ]

        session.add_all(default_tariffs)
        session.commit()
        print("Базовые тарифы созданы.")
