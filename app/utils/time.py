from datetime import datetime, timezone


def get_utc_now() -> str:
    """Возвращает текущую дату/время в UTC в формате ISO."""
    return datetime.now(timezone.utc).isoformat()
