from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


@pytest.fixture()
def ed25519_keypair():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


@pytest.fixture()
def bio_env(ed25519_keypair, tmp_path: Path, monkeypatch):
    _, public_pem = ed25519_keypair
    monkeypatch.setenv("PORTAL_SSO_PUBLIC_KEY", public_pem)
    monkeypatch.setenv("BIO_DATA_DIR", str(tmp_path / "bio_data"))
    monkeypatch.setenv("VERSION", "1")
    monkeypatch.delenv("PORTAL_SSO_JWKS", raising=False)
