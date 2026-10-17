from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pwdlib import PasswordHash

from app.config import settings


password_hasher = PasswordHash.recommended()
token_serializer = URLSafeTimedSerializer(settings.session_secret, salt="nexo-dashboard-session")


def create_access_token(email: str) -> str:
    return token_serializer.dumps({"sub": email})


def read_access_token(token: str) -> str | None:
    try:
        payload = token_serializer.loads(token, max_age=settings.session_ttl_minutes * 60)
    except (BadSignature, SignatureExpired):
        return None

    subject = payload.get("sub") if isinstance(payload, dict) else None
    return subject if isinstance(subject, str) else None
