from uuid import UUID

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class CollectorEvent(BaseModel):
    event_id: UUID
    site_id: str = Field(min_length=1, max_length=100)
    session_id: UUID
    event_name: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z][a-zA-Z0-9_.:-]*$")
    path: str = Field(min_length=1, max_length=300)
    device_type: Literal["desktop", "mobile", "tablet", "unknown"] = "unknown"
    browser_name: Literal["chrome", "chromium", "firefox", "safari", "edge", "opera", "samsung internet", "other", "unknown"] = "unknown"
    os_name: Literal["windows", "macos", "ios", "android", "linux", "chromeos", "other", "unknown"] = "unknown"
    duration_ms: int | None = Field(default=None, ge=0, le=86_400_000)

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value.startswith("/") or "?" in value or "#" in value:
            raise ValueError("path must be a pathname without query or fragment")
        return value

    @model_validator(mode="after")
    def validate_duration(self):
        if (self.event_name == "page_duration") != (self.duration_ms is not None):
            raise ValueError("duration_ms is only valid for page_duration events")
        return self


class CollectorResponse(BaseModel):
    accepted: bool = True
    duplicate: bool = False
