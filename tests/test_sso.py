import time

import pytest
import jwt
from fastapi.testclient import TestClient

from bio.main import app
from bio.sso import SSOConfigurationError, assert_sso_configured, jwks_keys_empty


def _token(private_pem: str, sub: str = "user-1") -> str:
    return jwt.encode(
        {"sub": sub, "email": "analyst@tereo.llc", "name": "Test Analyst", "exp": int(time.time()) + 3600},
        private_pem,
        algorithm="EdDSA",
    )


def test_home_redirects_to_portal_launch_without_cookie(bio_env):
    client = TestClient(app)
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"].startswith("/portal/launch/bio")


def test_home_renders_with_valid_portal_token(bio_env, ed25519_keypair):
    private_pem, _ = ed25519_keypair
    client = TestClient(app)
    token = _token(private_pem)
    r = client.get("/", cookies={"portal_token_bio": token})
    assert r.status_code == 200
    assert "Tereo, LLC" in r.text


def test_jwks_keys_empty_reject(bio_env, monkeypatch):
    monkeypatch.setenv("PORTAL_SSO_JWKS", '{"keys":[]}')
    with pytest.raises(SSOConfigurationError):
        assert_sso_configured()


def test_home_503_when_jwks_keys_empty(bio_env, monkeypatch):
    monkeypatch.setenv("PORTAL_SSO_JWKS", '{"keys":[]}')
    client = TestClient(app)
    assert client.get("/").status_code == 503
    assert client.get("/healthz").json()["status"] == "degraded"
