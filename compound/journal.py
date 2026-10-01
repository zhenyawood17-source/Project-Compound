"""Log: append every decision (approved or rejected) as one JSON line."""
import json
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path


def log(path: Path, event: str, **payload) -> dict:
    record = {"ts": datetime.now(timezone.utc).isoformat(), "event": event,
              **{k: asdict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in payload.items()}}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, default=lambda o: o.isoformat() if isinstance(o, date) else str(o)) + "\n")
    return record
