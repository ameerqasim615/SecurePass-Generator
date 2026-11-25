import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_defaults_are_safe_for_local_development():
    s = Settings.from_env({})
    assert s.app_env == "development"
    assert s.log_level == "INFO"
    assert s.cors_origins == ("http://localhost:5173",)
    assert s.is_production is False


def test_cors_origins_are_split_trimmed_and_normalised():
    s = Settings.from_env({"CORS_ORIGINS": " http://localhost:5173/ , https://app.example.com "})
    assert s.cors_origins == ("http://localhost:5173", "https://app.example.com")


def test_empty_env_values_fall_back_to_defaults():
    s = Settings.from_env({"APP_ENV": "", "LOG_LEVEL": "", "CORS_ORIGINS": ""})
    assert s.app_env == "development"
    assert s.cors_origins == ("http://localhost:5173",)


def test_wildcard_cors_origin_is_rejected():
    with pytest.raises(ValidationError):
        Settings.from_env({"CORS_ORIGINS": "*"})
    with pytest.raises(ValidationError):
        Settings.from_env({"CORS_ORIGINS": "https://ok.example.com,*"})


def test_cors_origin_without_scheme_is_rejected():
    with pytest.raises(ValidationError):
        Settings.from_env({"CORS_ORIGINS": "app.example.com"})


def test_production_requires_explicit_cors_origins():
    with pytest.raises(ValueError, match="CORS_ORIGINS"):
        Settings.from_env({"APP_ENV": "production"})

    s = Settings.from_env({"APP_ENV": "production", "CORS_ORIGINS": "https://app.example.com"})
    assert s.is_production is True


def test_unknown_environment_is_rejected():
    with pytest.raises(ValidationError):
        Settings.from_env({"APP_ENV": "staging-ish"})


def test_log_level_is_case_insensitive_and_validated():
    assert Settings.from_env({"LOG_LEVEL": "debug"}).log_level == "DEBUG"
    with pytest.raises(ValidationError):
        Settings.from_env({"LOG_LEVEL": "loud"})


def test_settings_are_immutable():
    s = Settings.from_env({})
    with pytest.raises(ValidationError):
        s.app_env = "production"
