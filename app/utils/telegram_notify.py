import requests

TELEGRAM_BOT_TOKEN = (
    "7709134236:AAEhA7DRFlOq4-0DckormcF3SgcYcAdSsuM"  # ← сюда вставь токен своего бота!
)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

BOT_USERNAME = "Safarbarbot"


def send_telegram_message(telegram_id: int, text: str):
    data = {"chat_id": telegram_id, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(TELEGRAM_API_URL, data=data, timeout=3)
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")


def send_telegram_message_rate(user_tg_id: int, driver_id: int, trip_id: int):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    mini_app_url = f"https://t.me/{BOT_USERNAME}?startapp=rate_{driver_id}_{trip_id}"
    text = "🚘 Ваша поездка завершена!\nПожалуйста, оцените водителя!"
    reply_markup = {
        "inline_keyboard": [[{"text": "Оценить поездку", "url": mini_app_url}]]
    }
    data = {
        "chat_id": user_tg_id,
        "text": text,
        "reply_markup": reply_markup,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=data, timeout=5)
        print("Telegram send result:", r.text)
        r.raise_for_status()
    except Exception as e:
        print(f"Ошибка отправки сообщения для оценки: {e}")


def send_new_booking_notification(driver_tg_id: int, trip_id: int):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    mini_app_url = f"https://t.me/{BOT_USERNAME}?startapp=trip_{trip_id}"
    text = "📬 У вас новая заявка на поездку!"
    reply_markup = {
        "inline_keyboard": [[{"text": "Посмотреть заявку", "url": mini_app_url}]]
    }
    data = {
        "chat_id": driver_tg_id,
        "text": text,
        "reply_markup": reply_markup,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=data, timeout=5)
        print("Telegram send result:", r.text)
        r.raise_for_status()
    except Exception as e:
        print(f"Ошибка отправки уведомления о заявке: {e}")


def send_booking_cancelled_notification(driver_tg_id: int, trip_id: int):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    mini_app_url = f"https://t.me/{BOT_USERNAME}?startapp=trip_{trip_id}"
    text = (
        "❗️Пассажир отменил бронь на вашу поездку.\n"
        "Место снова доступно для бронирования.\n"
        "Посмотреть детали:"
    )
    reply_markup = {
        "inline_keyboard": [[{"text": "Открыть поездку", "url": mini_app_url}]]
    }
    data = {
        "chat_id": driver_tg_id,
        "text": text,
        "reply_markup": reply_markup,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=data, timeout=5)
        print("Telegram send result:", r.text)
        r.raise_for_status()
    except Exception as e:
        print(f"Ошибка отправки уведомления об отмене брони: {e}")
