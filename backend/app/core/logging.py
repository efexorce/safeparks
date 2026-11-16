import logging
import json
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger


class ISO27001Formatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["service"] = "safeparks-backend"
        if not log_record.get("event_type"):
            log_record["event_type"] = "system"


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    formatter = ISO27001Formatter(
        fmt="%(timestamp)s %(level)s %(logger)s %(message)s %(event_type)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers = [handler]

    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = True


def get_audit_logger() -> logging.Logger:
    return logging.getLogger("safeparks.audit")


def log_audit_event(
    event_type: str,
    user_id: Optional[str],
    resource: str,
    action: str,
    result: str,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    logger = get_audit_logger()
    log_data = {
        "event_type": event_type,
        "user_id": user_id,
        "resource": resource,
        "action": action,
        "result": result,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if extra:
        log_data.update(extra)
    logger.info(json.dumps(log_data))


from typing import Optional
