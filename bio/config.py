import os
from pathlib import Path

VERSION = os.environ.get("VERSION", "1")
APP_NAME = "BIO — Business Intelligence Officer"
COMPANY = "Tereo, LLC"

PORT = int(os.environ.get("BIO_PORT", "8504"))
MOUNT_PATH = os.environ.get("BIO_MOUNT_PATH", "/bio").rstrip("/") or "/bio"

COOKIE_NAME = "portal_token_bio"
LAUNCH_PATH = os.environ.get("PORTAL_LAUNCH_PATH", "/portal/launch/bio")

def portal_sso_public_key_pem() -> str:
    """PEM string (EdDSA public key). Never accept empty JWKS keys=[]."""
    return os.environ.get("PORTAL_SSO_PUBLIC_KEY", "").strip()


def portal_sso_jwks() -> str:
    """Optional JWKS JSON string; if present and keys is [], auth must fail closed."""
    return os.environ.get("PORTAL_SSO_JWKS", "").strip()

# Persistent data — never wiped by the app on boot.
_default_data = Path(__file__).resolve().parent.parent / "data" / "bio"
BIO_DATA_DIR = Path(os.environ.get("BIO_DATA_DIR", str(_default_data))).resolve()

PORTAL_FRAME_ANCESTORS = os.environ.get(
    "PORTAL_FRAME_ANCESTORS",
    "'self' https://portal.tereo.llc https://*.tereo.llc",
)
