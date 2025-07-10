import requests

TELEGRAM_BOT_TOKEN = (
    "8190058603:AAGDpggm-K1lZgGudQM_7tcOfod8AlpHJ4M"  # ← сюда вставь токен своего бота!
)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

BOT_USERNAME = "fortestingfortesting_bot"

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
        "inline_keyboard": [
            [
                {"text": "Оценить поездку", "url": mini_app_url}
            ]
        ]
    }
    data = {
        "chat_id": user_tg_id,
        "text": text,
        "reply_markup": reply_markup,
        "parse_mode": "HTML"
    }
    requests.post(url, json=data)