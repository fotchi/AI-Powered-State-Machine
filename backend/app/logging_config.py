"""
Centralized logging -- per the Technical Design Document §9: "centralized
logging of requests, agent executions, and failures." Everything (HTTP
request/response timing, unhandled exceptions, pipeline lifecycle events)
goes through this one logger into one file, instead of being scattered
across print() calls and whatever uvicorn happens to echo to stdout.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "backend" / "logs"
LOG_FILE = LOG_DIR / "app.log"


def _configure() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("flync")
    if logger.handlers:
        return logger  # already configured (e.g. re-imported under --reload)

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.propagate = False
    return logger


logger = _configure()
