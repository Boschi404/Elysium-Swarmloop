"""
LRU Cache — O(1) get/put/delete with configurable capacity.

Uses a custom doubly-linked list + hash map for O(1) operations.
Thread-safe via threading.RLock. Tracks hits, misses, and size.
"""

from __future__ import annotations

import threading
from typing import Any, Optional


class _DLNode:
    """Doubly-linked list node holding a key-value pair."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: Any, value: Any) -> None:
        self.key = key
        self.value = value
        self.prev: Optional[_DLNode] = None
        self.next: Optional[_DLNode] = None


class LRUCache:
    """Least Recently Used cache with O(1) operations.

    Args:
        capacity: Maximum number of items before eviction.

    Raises:
        ValueError: If capacity < 1.
    """

    def __init__(self, capacity: int = 100) -> None:
        if capacity < 1:
            raise ValueError("Capacity must be >= 1")

        self._capacity = capacity
        self._cache: dict[Any, _DLNode] = {}  # key → node
        self._lock = threading.RLock()

        # Sentinel nodes for the doubly-linked list (head = MRU, tail = LRU)
        self._head = _DLNode(None, None)  # sentinel
        self._tail = _DLNode(None, None)  # sentinel
        self._head.next = self._tail
        self._tail.prev = self._head

        # Statistics
        self._hits = 0
        self._misses = 0

    # ── Public Interface ──────────────────────────────────────────────

    @property
    def capacity(self) -> int:
        """Maximum number of entries the cache can hold."""
        return self._capacity

    @property
    def size(self) -> int:
        """Current number of entries in the cache."""
        return len(self._cache)

    @property
    def hits(self) -> int:
        """Number of successful get() calls."""
        return self._hits

    @property
    def misses(self) -> int:
        """Number of failed get() calls (returned -1)."""
        return self._misses

    def get(self, key: Any) -> Any:
        """Retrieve value for *key*, or -1 if missing.

        Accessing a key promotes it to MRU (most recently used).
        """
        with self._lock:
            node = self._cache.get(key)
            if node is None:
                self._misses += 1
                return -1

            self._hits += 1
            self._move_to_front(node)
            return node.value

    def put(self, key: Any, value: Any) -> None:
        """Insert or update *key* → *value*.

        If inserting over capacity, the LRU (least recently used) entry
        is evicted first.
        """
        with self._lock:
            existing = self._cache.get(key)
            if existing is not None:
                # Update in place and promote.
                existing.value = value
                self._move_to_front(existing)
                return

            # New entry — evict if at capacity.
            if len(self._cache) >= self._capacity:
                self._evict_lru()

            node = _DLNode(key, value)
            self._cache[key] = node
            self._add_to_front(node)

    def delete(self, key: Any) -> bool:
        """Remove *key* from the cache.

        Returns:
            True if the key existed and was removed, False otherwise.
        """
        with self._lock:
            node = self._cache.pop(key, None)
            if node is None:
                return False
            self._remove_node(node)
            return True

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._cache.clear()
            # Reset list.
            self._head.next = self._tail
            self._tail.prev = self._head
            self._hits = 0
            self._misses = 0

    # ── Internal helpers ──────────────────────────────────────────────

    def _add_to_front(self, node: _DLNode) -> None:
        """Insert *node* immediately after the sentinel head (MRU position)."""
        after = self._head.next  # type: ignore[union-attr]
        self._head.next = node
        node.prev = self._head
        node.next = after
        if after is not None:
            after.prev = node

    def _remove_node(self, node: _DLNode) -> None:
        """Unlink *node* from the doubly-linked list."""
        prev_node = node.prev
        next_node = node.next
        if prev_node is not None:
            prev_node.next = next_node
        if next_node is not None:
            next_node.prev = prev_node
        node.prev = None
        node.next = None

    def _move_to_front(self, node: _DLNode) -> None:
        """Unlink *node* and re-insert it at the MRU position."""
        self._remove_node(node)
        self._add_to_front(node)

    def _evict_lru(self) -> None:
        """Remove the entry just before the tail sentinel (the LRU entry)."""
        lru = self._tail.prev
        if lru is None or lru is self._head:
            return
        self._remove_node(lru)
        del self._cache[lru.key]

    def __len__(self) -> int:
        """Same as :attr:`size`."""
        return self.size

    def __contains__(self, key: Any) -> bool:
        """``key in cache`` check without affecting recency."""
        return key in self._cache

    def __repr__(self) -> str:
        return (
            f"LRUCache(capacity={self._capacity}, "
            f"size={len(self._cache)}, "
            f"hits={self._hits}, "
            f"misses={self._misses})"
        )
