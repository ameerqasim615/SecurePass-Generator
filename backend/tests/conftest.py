import pytest

from app.core.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(app_env="test", cors_origins=("http://localhost:5173",))


@pytest.fixture
def fastapi_app(settings):
    from app.main import create_app

    return create_app(settings)


@pytest.fixture
def client(fastapi_app):
    from fastapi.testclient import TestClient

    # raise_server_exceptions=False lets us assert on the real 500 response body.
    with TestClient(fastapi_app, raise_server_exceptions=False) as test_client:
        yield test_client
