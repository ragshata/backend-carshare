from jose import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "CARSHARE"  # !!! замени на свой секрет в .env
ALGORITHM = "HS256"

def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(days=7)  # Сначала прибавь timedelta!
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
