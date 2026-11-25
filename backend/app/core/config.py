"""Application settings, loaded from environment variables.

Settings are validated once at startup so a bad deployment fails fast instead of
misbehaving at runtime. Secrets are never given defaults here.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    app_name: str = "ResumeAI API"
    app_version: str = "0.1.0"
    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalise_log_level(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().upper()
            if value not in _LOG_LEVELS:
                raise ValueError(f"log_level must be one of {sorted(_LOG_LEVELS)}")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return tuple(o.strip().rstrip("/") for o in value.split(",") if o.strip())
        return value

    @field_validator("cors_origins", mode="after")
    @classmethod
    def _validate_origins(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("at least one CORS origin is required")
        for origin in value:
            if origin == "*":
                raise ValueError("wildcard CORS origins are not allowed; list explicit origins")
            if not origin.startswith(("http://", "https://")):
                raise ValueError(f"CORS origin must start with http:// or https://: {origin!r}")
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        env = os.environ if environ is None else environ

        if env.get("APP_ENV") == "production" and not env.get("CORS_ORIGINS"):
            raise ValueError("CORS_ORIGINS must be set explicitly when APP_ENV=production")

        mapping = {
            "APP_ENV": "app_env",
            "LOG_LEVEL": "log_level",
            "CORS_ORIGINS": "cors_origins",
        }
        # Empty values are treated as "not set" so the defaults apply.
        values = {field: env[key] for key, field in mapping.items() if env.get(key)}
        return cls(**values)


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
