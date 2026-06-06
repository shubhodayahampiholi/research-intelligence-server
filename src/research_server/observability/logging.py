import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from typing import Any

class StructuredFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects.

    Extra fields passed via logger.info("msg", extra={"key": "value"})
    are included alongside timestamp, level, logger, and message.
    """

    # Baseline set of keys present on every LogRecord with no extras.
    # Built once at class definition time — not hardcoded, derived from
    # an actual LogRecord instance.
    _BASELINE_KEYS = frozenset(logging.LogRecord(
        name="", level=0, pathname="", lineno=0,
        msg="", args=(), exc_info=None
    ).__dict__.keys())

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Only include keys that were not present on a baseline LogRecord —
        # these are the fields explicitly added via extra={}
        for key, value in record.__dict__.items():
            if key not in self._BASELINE_KEYS:
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = traceback.format_exception(*record.exc_info)

        return json.dumps(log_entry, default=str)

def configure_logging(level: str = "INFO") -> None:
    """
    Configure the root logger to write structured JSON to stderr.

    MUST be called before the MCP server starts. After this call, all
    logging.getLogger(...) instances in the application emit structured
    JSON to stderr — never to stdout.

    Args:
        level: one of "DEBUG", "INFO", "WARNING", "ERROR"
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers first — prevents duplicate output if
    # configure_logging is called more than once (e.g. in tests)
    root_logger.handlers.clear()

    # Explicit stderr handler — never stdout
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(stderr_handler)

    # Silence noisy third-party loggers
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a module.

    Usage:
        logger = get_logger(__name__)
        logger.info("Tool called", extra={"tool": "search_papers", "query": query})

    The `extra` dict fields are merged into the JSON log record alongside
    timestamp, level, and message.
    """
    return logging.getLogger(name)
