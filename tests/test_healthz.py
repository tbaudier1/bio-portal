from fastapi.testclient import TestClient

from bio.main import app


def test_healthz_open_without_auth(bio_env):
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["version"] == "1"
    assert body["service"] == "bio"
