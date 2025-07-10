import requests

TELEGRAM_BOT_TOKEN = (
    "8190058603:AAGDpggm-K1lZgGudQM_7tcOfod8AlpHJ4M"  # ← сюда вставь токен своего бота!
)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send_telegram_message(telegram_id: int, text: str):
    data = {"chat_id": telegram_id, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(TELEGRAM_API_URL, data=data, timeout=3)
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")

