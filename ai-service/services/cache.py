from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any


class ResponseCache:
    def __init__(self, ttl_s: int = 600, max_entries: int = 1024):
        self._ttl_s = max(0, int(ttl_s))
        self._max_entries = max(1, int(max_entries))
        self._store: "OrderedDict[str, tuple[float, Any]]" = OrderedDict()

    def get(self, key: str) -> Any | None:
        now = time.monotonic()
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at < now:
            self._store.pop(key, None)
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any) -> None:
        now = time.monotonic()
        expires_at = now + self._ttl_s
        self._store[key] = (expires_at, value)
        self._store.move_to_end(key)
        self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        if len(self._store) <= self._max_entries:
            return
        now = time.monotonic()
        expired_keys: list[str] = []
        for k, (expires_at, _) in self._store.items():
            if expires_at < now:
                expired_keys.append(k)
        for k in expired_keys:
            self._store.pop(k, None)
        while len(self._store) > self._max_entries:
            self._store.popitem(last=False)

