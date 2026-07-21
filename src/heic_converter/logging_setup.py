from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path


def application_data_dir() -> Path:
    base = os.getenv("LOCALAPPDATA")
    if base:
        return Path(base) / "TCDOVERLORD" / "HEIC_to_JPG_Converter"
    return Path.home() / ".local" / "share" / "TCDOVERLORD" / "HEIC_to_JPG_Converter"


def configure_logging() -> Path:
    log_dir = application_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"session_{datetime.now():%Y%m%d_%H%M%S}.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not any(isinstance(handler, logging.FileHandler) for handler in root_logger.handlers):
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )
        root_logger.addHandler(file_handler)

    logging.getLogger(__name__).info("Logging started: %s", log_path)
    return log_path
