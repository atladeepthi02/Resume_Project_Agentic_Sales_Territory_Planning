from typing import Any, Dict


class MemoryService:
    def __init__(self):
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self._store[key] = value

    def get(self, key: str, default: Any = None):
        return self._store.get(key, default)
