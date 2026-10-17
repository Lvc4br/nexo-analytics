import hmac

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.config import settings
from app.security import create_access_token, password_hasher, read_access_token


router = APIRouter(prefix="/auth", tags=["authentication"])
bearer_scheme = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    email: str


def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Entre para acessar esta área.")

    email = read_access_token(credentials.credentials)
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão expirada. Entre novamente.")
    return email


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest) -> TokenResponse:
    if not settings.dashboard_email or not settings.dashboard_password_hash:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configure DASHBOARD_EMAIL e DASHBOARD_PASSWORD_HASH no arquivo .env.",
        )

    email_matches = hmac.compare_digest(
        credentials.email.strip().casefold(),
        settings.dashboard_email.strip().casefold(),
    )
    try:
        password_matches = password_hasher.verify(credentials.password, settings.dashboard_password_hash)
    except Exception:
        password_matches = False

    if not email_matches or not password_matches:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos.")

    return TokenResponse(
        access_token=create_access_token(settings.dashboard_email),
        expires_in=settings.session_ttl_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
def current_user(email: str = Depends(require_user)) -> UserResponse:
    return UserResponse(email=email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(_: str = Depends(require_user)) -> None:
    return None
