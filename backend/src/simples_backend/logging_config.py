from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from flask import g, has_request_context


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = ""
        record.user_id = ""
        if has_request_context():
            if not hasattr(g, "request_id"):
                g.request_id = str(uuid.uuid4())
            record.request_id = g.request_id
            identity = getattr(g, "identity", None)
            if identity:
                record.user_id = identity.get("user_id", "")
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        obj = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if getattr(record, "request_id", None):
            obj["request_id"] = record.request_id
        if getattr(record, "user_id", None):
            obj["user_id"] = record.user_id
        if getattr(record, "duration_ms", None) is not None:
            obj["duration_ms"] = record.duration_ms
        if record.exc_info and record.exc_info[0]:
            obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(obj, ensure_ascii=False)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
