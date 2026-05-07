import hashlib
import json
from typing import Any

from flask import Request


def require_json(request: Request) -> dict[str, Any]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object request body.")
    return payload


def stable_key(prefix: str, obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    return f"{prefix}:{hashlib.sha256(raw).hexdigest()}"

