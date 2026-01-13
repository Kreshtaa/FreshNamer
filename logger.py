import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, "app.log")

    logger = logging.getLogger("renamer")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    # Rotating file: 5 MB per file, keep 5 backups
    handler = RotatingFileHandler(
        log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Optional: also log to console during development
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger
