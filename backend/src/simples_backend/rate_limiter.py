from __future__ import annotations

import threading
import time


class RateLimitExceeded(Exception):
    def __init__(self, key: str, max_requests: int, window_s: int):
        self.key = key
        self.max_requests = max_requests
        self.window_s = window_s
        super().__init__(f"rate limit exceeded: {max_requests} per {window_s}s")


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_s: int = 60):
        self.max_requests = max_requests
        self.window_s = window_s
        self._lock = threading.Lock()
        self._buckets: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_s
        with self._lock:
            timestamps = self._buckets.get(key, [])
            timestamps = [t for t in timestamps if t > cutoff]
            if len(timestamps) >= self.max_requests:
                self._buckets[key] = timestamps
                return False
            timestamps.append(now)
            self._buckets[key] = timestamps
            return True

    def remaining(self, key: str) -> int:
        now = time.monotonic()
        cutoff = now - self.window_s
        with self._lock:
            timestamps = self._buckets.get(key, [])
            timestamps = [t for t in timestamps if t > cutoff]
            self._buckets[key] = timestamps
            return max(0, self.max_requests - len(timestamps))

    def reset(self, key: str) -> None:
        with self._lock:
            self._buckets.pop(key, None)

    def check(self, key: str) -> None:
        if not self.is_allowed(key):
            raise RateLimitExceeded(key, self.max_requests, self.window_s)
