"""ASGI entry: BIO on port 8504, mounted at BIO_MOUNT_PATH when not behind path-stripping proxy."""

import os

from fastapi import FastAPI

from bio.config import MOUNT_PATH
from bio.main import app as bio_app

prefix = MOUNT_PATH if MOUNT_PATH.startswith("/") else f"/{MOUNT_PATH}"

if prefix == "/" or os.environ.get("BIO_STRIP_PREFIX", "").lower() in ("1", "true", "yes"):
    application = bio_app
else:
    root = FastAPI(title="BIO mount", docs_url=None, redoc_url=None)
    root.mount(prefix, bio_app)
    application = root
