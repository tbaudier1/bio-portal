from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from bio import VERSION as APP_VERSION
from bio.config import (
    APP_NAME,
    COMPANY,
    MOUNT_PATH,
    PORTAL_FRAME_ANCESTORS,
    portal_sso_jwks,
)
from bio.data_guard import ensure_data_dir
from bio.portal_bounce import (
    portal_launch_bounce_url,
    portal_sso_return_attempt,
    unauthenticated_stop_response,
)
from bio.sso import get_user_from_request, jwks_keys_empty

templates = Jinja2Templates(directory="templates")


def _mount_prefix() -> str:
    return MOUNT_PATH if MOUNT_PATH.startswith("/") else f"/{MOUNT_PATH}"


class PortalSecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            f"frame-ancestors {PORTAL_FRAME_ANCESTORS}; default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        )
        if "X-Frame-Options" in response.headers:
            del response.headers["X-Frame-Options"]
        return response


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_data_dir()
    yield


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan, docs_url=None, redoc_url=None)
app.add_middleware(PortalSecurityHeadersMiddleware)


def _sso_misconfigured() -> bool:
    return jwks_keys_empty(portal_sso_jwks())


@app.get("/healthz")
async def healthz():
    status = "ok"
    detail: dict = {"service": "bio", "version": APP_VERSION}
    if _sso_misconfigured():
        status = "degraded"
        detail["sso"] = "jwks_keys_empty"
    return JSONResponse({"status": status, **detail})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if _sso_misconfigured():
        return HTMLResponse("<h1>SSO misconfigured</h1><p>Portal JWKS keys=[] is not allowed.</p>", status_code=503)
    user = get_user_from_request(request)
    if user is None:
        if portal_sso_return_attempt(request):
            return unauthenticated_stop_response(request)
        return RedirectResponse(url=portal_launch_bounce_url(request), status_code=303)
    metrics = [
        {"label": "Active leases (example)", "value": "128", "note": "Placeholder — not real data"},
        {"label": "Occupancy % (example)", "value": "94.2%", "note": "Placeholder — not real data"},
        {"label": "Open work orders (example)", "value": "17", "note": "Placeholder — not real data"},
        {"label": "MTD revenue (example)", "value": "$412,500", "note": "Placeholder — not real data"},
    ]
    return templates.TemplateResponse(
        request,
        "home.html",
        {"app_name": APP_NAME, "company": COMPANY, "version": APP_VERSION, "user": user, "metrics": metrics, "mount_path": _mount_prefix()},
    )
