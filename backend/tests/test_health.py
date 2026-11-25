"""API-level tests: health route, security headers, CORS, and the error envelope.

Requires fastapi + httpx (pip install -r requirements-dev.txt).
Note: no `from __future__ import annotations` here on purpose - FastAPI must be
able to resolve the module-level Payload annotation on the test routes below.
"""

from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.core.errors import AppError
from app.main import create_app

ALLOWED_ORIGIN = "http://localhost:5173"


class Payload(BaseModel):
    name: str = Field(min_length=20)


def test_health_returns_ok(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ResumeAI API", "version": "0.1.0"}


def test_security_headers_are_present(client):
    headers = client.get("/api/v1/health").headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["referrer-policy"] == "no-referrer"
    assert headers["cache-control"] == "no-store"


def test_unknown_route_uses_error_envelope(client):
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    body = response.json()["error"]
    assert body["code"] == "http_404"
    assert isinstance(body["message"], str)


def test_wrong_method_uses_error_envelope_and_keeps_allow_header(client):
    response = client.post("/api/v1/health")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "http_405"
    assert "GET" in response.headers["allow"]


def test_cors_allows_configured_origin(client):
    response = client.options(
        "/api/v1/health",
        headers={"Origin": ALLOWED_ORIGIN, "Access-Control-Request-Method": "GET"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


def test_cors_rejects_unconfigured_origin(client):
    preflight = client.options(
        "/api/v1/health",
        headers={"Origin": "https://evil.example.com", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" not in preflight.headers

    simple = client.get("/api/v1/health", headers={"Origin": "https://evil.example.com"})
    assert "access-control-allow-origin" not in simple.headers


def test_docs_available_in_test_env_but_hidden_in_production(client):
    assert client.get("/docs").status_code == 200

    prod = Settings(app_env="production", cors_origins=("https://app.example.com",))
    with TestClient(create_app(prod)) as prod_client:
        assert prod_client.get("/docs").status_code == 404
        assert prod_client.get("/openapi.json").status_code == 404


def test_app_error_is_rendered_with_details(fastapi_app, client):
    @fastapi_app.get("/_test/conflict")
    async def conflict():
        raise AppError(409, "conflict", "Already exists", [{"field": "name", "message": "taken"}])

    response = client.get("/_test/conflict")
    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "conflict",
            "message": "Already exists",
            "details": [{"field": "name", "message": "taken"}],
        }
    }


def test_validation_errors_name_fields_but_never_echo_input(fastapi_app, client):
    @fastapi_app.post("/_test/validate")
    async def validate(payload: Payload):
        return payload

    submitted = "short-secret-value"
    response = client.post("/_test/validate", json={"name": submitted})

    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "validation_error"
    assert body["details"][0]["field"] == "name"
    assert submitted not in response.text


def test_unhandled_exception_returns_generic_500(fastapi_app, client):
    @fastapi_app.get("/_test/boom")
    async def boom():
        raise RuntimeError("db password is hunter2")

    response = client.get("/_test/boom")
    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "message": "An unexpected error occurred."}
    }
    assert "hunter2" not in response.text
