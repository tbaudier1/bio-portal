"""Portal SSO: EdDSA JWT in portal_token_bio cookie."""

import json
from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import Request

from bio.config import COOKIE_NAME, portal_sso_jwks, portal_sso_public_key_pem


class SSOConfigurationError(Exception):
    """Invalid or empty Portal key material (e.g. keys=[])."""


@dataclass
class PortalUser:
    sub: str
    email: str | None = None
    name: str | None = None
    raw: dict[str, Any] | None = None


def _normalize_pem(pem: str) -> str:
    pem = pem.strip()
    if "\\n" in pem and "\n" not in pem:
        pem = pem.replace("\\n", "\n")
    return pem


def jwks_keys_empty(jwks_json: str) -> bool:
    if not jwks_json:
        return False
    try:
        doc = json.loads(jwks_json)
    except json.JSONDecodeError:
        return False
    keys = doc.get("keys")
    return isinstance(keys, list) and len(keys) == 0


def assert_sso_configured() -> None:
    """Fail closed when JWKS is explicitly keys=[] or no PEM key is configured."""
    if jwks_keys_empty(portal_sso_jwks()):
        raise SSOConfigurationError("Portal SSO JWKS has keys=[]; refusing to authenticate")
    pem = _normalize_pem(portal_sso_public_key_pem())
    if not pem:
        raise SSOConfigurationError("PORTAL_SSO_PUBLIC_KEY is not configured")


def load_verification_key() -> str:
    assert_sso_configured()
    return _normalize_pem(portal_sso_public_key_pem())


def decode_portal_token(token: str) -> PortalUser:
    key = load_verification_key()
    payload = jwt.decode(
        token,
        key,
        algorithms=["EdDSA", "Ed25519"],
        options={"require": ["exp", "sub"]},
    )
    return PortalUser(
        sub=str(payload["sub"]),
        email=payload.get("email"),
        name=payload.get("name") or payload.get("display_name"),
        raw=payload,
    )


def get_token_from_request(request: Request) -> str | None:
    return request.cookies.get(COOKIE_NAME)


def get_user_from_request(request: Request) -> PortalUser | None:
    try:
        token = get_token_from_request(request)
        if not token:
            return None
        return decode_portal_token(token)
    except (jwt.PyJWTError, SSOConfigurationError):
        return None
