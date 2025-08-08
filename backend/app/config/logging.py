import logging
import logging.config
import os
from datetime import datetime
from typing import Dict, Any
from app.config.settings import get_settings

def setup_logging() -> None:
    settings = get_settings()

    # Ensure logs directory exists
    os.makedirs(settings.logs_directory, exist_ok=True)

    # Base log filename with daily timestamp
    base_log_filename = os.path.join(
        settings.logs_directory,
        f"warehouse_{datetime.now().strftime('%Y%m%d')}.log",
    )

    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "console": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            },
            # Detailed formatter for file logs
            "detailed": {
                "format": (
                    "%(asctime)s - %(levelname)s - %(name)s - "
                    "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
                ),
            },
            # JSON formatter for structured logs
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "fmt": (
                    "timestamp levelname name filename lineno funcName message"
                ),
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
        },

        "handlers": {
            # Console output handler
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "level": "INFO",
                "stream": "ext://sys.stdout",
            },

            # Rotating file handler for general app logs (INFO and DEBUG)
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": base_log_filename,
                "mode": "a",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 7,
                "encoding": "utf-8",
                "formatter": "detailed",
                "level": "DEBUG" if settings.debug else "INFO",
            },

            # Rotating file handler for JSON formatted error logs
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(settings.logs_directory, "errors.json.log"),
                "mode": "a",
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 10,
                "encoding": "utf-8",
                "formatter": "json",
                "level": "ERROR",
            },
        },

        "loggers": {
            # Root logger captures logs from all libraries
            "": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
            },
            # Core FastAPI backend app
            "app": {
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["console", "app_file", "error_file"],
                "propagate": False,
            },
            # Warehouse module (task manager, runner, registry)
            "app.warehouse": {
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["app_file", "error_file"],
                "propagate": False,
            },
            # Services layer (MinIO, cloud functions, upload, notification)
            "app.services": {
                "level": "INFO",
                "handlers": ["app_file", "error_file"],
                "propagate": False,
            },
            # Database access (Mongo, Redis)
            "app.db": {
                "level": "WARNING",
                "handlers": ["app_file"],
                "propagate": False,
            },
            # API endpoints layer
            "app.api": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False,
            },
            # Execution environments e.g., Fargate runner logs
            "app.warehouse.runners": {
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["app_file", "error_file"],
                "propagate": False,
            },
            # External libraries can stay default but you may tune as needed
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False,
            },
        },
    }

    # Conditionally enable third-party JSON formatter dependency
    try:
        import pythonjsonlogger
    except ImportError:
        # Fall back to simpler formatters if jsonlogger not installed
        logging.warning(
            "python-json-logger not installed, JSON formatting will fallback to plain text."
        )
        logging_config["formatters"]["json"] = {
            "format": "%(asctime)s - %(levelname)s - %(message)s"
        }

    logging.config.dictConfig(logging_config)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"app.{name}")

class LoggerMixin:
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__)
