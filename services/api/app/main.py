from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import initialize_database, purge_expired_events
from app.routers import analytics, auth, collector


if settings.app_env.casefold() == "production" and (
    settings.session_secret == "local-only-change-me"
    or settings.session_secret.startswith("replace-with-")
    or len(settings.session_secret) < 32
):
    raise RuntimeError("Defina uma SESSION_SECRET forte antes de executar em produção.")

if settings.app_env.casefold() == "production" and not settings.durable_database_configured:
    raise RuntimeError("Configure DATABASE_URL com PostgreSQL durável antes de executar em produção.")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    purge_expired_events()
    yield


app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(analytics.router, prefix=settings.api_v1_prefix)
app.include_router(collector.router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
