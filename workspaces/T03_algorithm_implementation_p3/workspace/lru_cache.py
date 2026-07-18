"""
LRU Cache — Least Recently Used cache with O(1) operations.

Implementation uses OrderedDict (Python's built-in dict + linked list)
backed by a threading.Lock for thread safety.

Supports:
    - get(key) → value or -1
    - put(key, value)
    - delete(key)
    - Configurable capacity
    - Tracking: size, hits, misses
    - Thread-safe via Lock
"""

from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")

_MISS = object()  # sentinel for missing key


class LRUCache(Generic[K, V]):
    """LRU Cache with O(1) get/put/delete, thread-safe."""

    def __init__(self, capacity: int) -> None:
        """
        Initialize the cache with a fixed capacity.

        Args:
            capacity: Maximum number of items before eviction.
        Raises:
            ValueError: If capacity <= 0.
        """
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self._capacity: int = capacity
        self._store: OrderedDict[K, V] = OrderedDict()
        self._lock: threading.Lock = threading.Lock()
        self._hits: int = 0
        self._misses: int = 0

    # ── Public API ────────────────────────────────────────────

    def get(self, key: K) -> V | int:
        """
        Retrieve a value by key and mark it as recently used.

        Args:
            key: The key to look up.

        Returns:
            The associated value if present, otherwise -1.
        """
        with self._lock:
            if key not in self._store:
                self._misses += 1
                return -1
            # Move to end (most recently used)
            value = self._store.pop(key)
            self._store[key] = value
            self._hits += 1
            return value

    def put(self, key: K, value: V) -> None:
        """
        Insert or update a key-value pair.

        If the key already exists, it is moved to most recently used.
        If the cache is at capacity, the least recently used item is evicted.

        Args:
            key: The key to insert or update.
            value: The value to associate.
        """
        with self._lock:
            if key in self._store:
                # Update existing — move to end
                self._store.pop(key)
            elif len(self._store) >= self._capacity:
                # Evict the least recently used (first item)
                self._store.popitem(last=False)
            self._store[key] = value

    def delete(self, key: K) -> bool:
        """
        Remove a key from the cache if it exists.

        Args:
            key: The key to remove.

        Returns:
            True if the key existed and was removed, False otherwise.
        """
        with self._lock:
            if key not in self._store:
                return False
            self._store.pop(key)
            return True

    # ── Accessors ─────────────────────────────────────────────

    @property
    def size(self) -> int:
        """Return the current number of items in the cache."""
        return len(self._store)

    @property
    def capacity(self) -> int:
        """Return the maximum capacity of the cache."""
        return self._capacity

    @property
    def hits(self) -> int:
        """Return the number of cache hits."""
        return self._hits

    @property
    def misses(self) -> int:
        """Return the number of cache misses."""
        return self._misses

    @property
    def hit_rate(self) -> float:
        """
        Return the hit rate as a float between 0.0 and 1.0.

        Returns 0.0 if no lookups have been made.
        """
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    # ── Convenience ───────────────────────────────────────────

    def clear(self) -> None:
        """Remove all items from the cache and reset counters."""
        with self._lock:
            self._store.clear()
            self._hits = 0
            self._misses = 0

    def __contains__(self, key: object) -> bool:
        """Check if a key is in the cache (without affecting LRU order)."""
        return key in self._store

    def __len__(self) -> int:
        """Return the number of items in the cache."""
        return len(self._store)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(capacity={self._capacity}, size={len(self._store)}, "
            f"hits={self._hits}, misses={self._misses})"
        )
