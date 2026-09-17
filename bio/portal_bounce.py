"""Portal SSO bounce loop guard (ForgeOS / QBW class)."""

from urllib.parse import quote

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

from bio.config import LAUNCH_PATH


def portal_sso_return_attempt(request: Request) -> bool:
    """True when Portal has returned the user but auth did not complete."""
    params = request.query_params
    return params.get("sso") == "1" or params.get("portal_sso") == "1"


def portal_launch_bounce_url(request: Request) -> str:
    """First unauthenticated visit: send user to Portal launch with sso=1."""
    return_url = request.url.path
    if request.url.query:
        return_url = f"{return_url}?{request.url.query}"
    return f"{LAUNCH_PATH}?sso=1&return_url={quote(return_url, safe='')}"


def unauthenticated_stop_response(request: Request) -> Response:
    """After sso=1 return with no cookie: never redirect to launch again."""
    accept = request.headers.get("accept", "")
    if accept.startswith("application/json") or (
        "application/json" in accept and "text/html" not in accept
    ):
        return JSONResponse({"error": "unauthorized", "sso": "incomplete"}, status_code=401)
    return HTMLResponse(
        "<!DOCTYPE html><html><body><h1>Sign-in required</h1>"
        "<p>Portal SSO did not complete. You are not signed in to BIO.</p></body></html>",
        status_code=401,
    )
