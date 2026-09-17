"""Ensure BIO_DATA_DIR exists and is never wiped by the application."""

from pathlib import Path

from bio.config import BIO_DATA_DIR

_MARKER = ".bio_never_wipe"


def ensure_data_dir() -> Path:
    BIO_DATA_DIR.mkdir(parents=True, exist_ok=True)
    marker = BIO_DATA_DIR / _MARKER
    if not marker.exists():
        marker.write_text(
            "BIO_DATA_DIR is persistent. The BIO app does not delete or truncate this directory on startup.\n",
            encoding="utf-8",
        )
    return BIO_DATA_DIR
