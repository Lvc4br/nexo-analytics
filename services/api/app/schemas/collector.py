from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CollectorEvent(BaseModel):
    event_id: UUID
    site_id: str = Field(min_length=1, max_length=100)
    session_id: UUID
    event_name: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z][a-zA-Z0-9_.:-]*$")
    path: str = Field(min_length=1, max_length=300)

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value.startswith("/") or "?" in value or "#" in value:
            raise ValueError("path must be a pathname without query or fragment")
        return value


class CollectorResponse(BaseModel):
    accepted: bool = True
    duplicate: bool = False
