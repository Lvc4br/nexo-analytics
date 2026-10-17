from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "Nexo Analytics API"
    api_v1_prefix: str = "/api/v1"
    cors_allowed_origins: str = "http://localhost:5173"

    session_secret: str = "local-only-change-me"
    session_ttl_minutes: int = 30
    dashboard_email: str = ""
    dashboard_password_hash: str = ""

    vercel_access_token: str = ""
    vercel_project_id: str = ""
    vercel_team_id: str = ""
    vercel_team_slug: str = ""
    vercel_project_domain: str = "luca-toniolo.vercel.app"
    vercel_api_base_url: str = "https://api.vercel.com/v1/query/web-analytics"

    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def vercel_configured(self) -> bool:
        return bool(self.vercel_access_token and self.vercel_project_id)


settings = Settings()
