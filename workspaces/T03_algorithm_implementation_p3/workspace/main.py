"""LRU Cache Implementation with O(1) get/put/delete operations.

Uses a custom doubly-linked list + hash map for true O(1) operations.
Thread-safe via threading.Lock.

Supports:
  - get(key) -> value or -1
  - put(key, value)
  - delete(key) -> bool
  - Configurable capacity
  - Tracks size, hits, misses
"""

import threading
from typing import Optional


class _Node:
    """Doubly-linked list node storing key, value, and prev/next pointers."""

    __slots__ = ('key', 'value', 'prev', 'next')

    def __init__(self, key: int, value: int) -> None:
        self.key = key
        self.value = value
        self.prev: Optional['_Node'] = None
        self.next: Optional['_Node'] = None


class _DoublyLinkedList:
    """Doubly-linked list with sentinel head/tail nodes.

    Provides O(1) add_to_front, remove, and remove_last operations.
    Sentinel nodes simplify edge cases (empty list, single element).
    """

    def __init__(self) -> None:
        self.head = _Node(0, 0)
        self.tail = _Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def remove(self, node: _Node) -> None:
        """Remove a node from the list in O(1)."""
        prev_node = node.prev
        next_node = node.next
        if prev_node is not None:
            prev_node.next = next_node
        if next_node is not None:
            next_node.prev = prev_node

    def add_to_front(self, node: _Node) -> None:
        """Insert a node immediately after the head sentinel (O(1))."""
        node.prev = self.head
        node.next = self.head.next
        if self.head.next is not None:
            self.head.next.prev = node
        self.head.next = node

    def remove_last(self) -> Optional[_Node]:
        """Remove and return the node before the tail sentinel (O(1)).

        Returns None if the list is empty.
        """
        if self.head.next is self.tail:
            return None
        last = self.tail.prev
        if last is not None:
            self.remove(last)
        return last


class LRUCache:
    """Least Recently Used (LRU) cache with O(1) get/put/delete.

    Uses a hash map for key lookup and a doubly-linked list to maintain
    access order. The most recently used item is at the front of the list;
    the least recently used is at the back and evicted first.

    Args:
        capacity: Maximum number of items the cache can hold (default 10,
            minimum 1).

    Thread-safe: all public operations acquire a reentrant lock.
    """

    def __init__(self, capacity: int = 10) -> None:
        if capacity < 1:
            capacity = 1
        self.capacity = capacity
        self._cache: dict[int, _Node] = {}
        self._list = _DoublyLinkedList()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    @property
    def size(self) -> int:
        """Return the number of items currently in the cache."""
        return len(self._cache)

    @property
    def hits(self) -> int:
        """Return the total number of cache hits since creation."""
        return self._hits

    @property
    def misses(self) -> int:
        """Return the total number of cache misses since creation."""
        return self._misses

    def get(self, key: int) -> int:
        """Retrieve the value for *key*.

        If the key exists, it is promoted to most recently used.
        Returns the value on success, or -1 if the key is not found.

        Complexity: O(1) average.
        """
        with self._lock:
            node = self._cache.get(key)
            if node is None:
                self._misses += 1
                return -1
            self._hits += 1
            # Promote to most recently used
            self._list.remove(node)
            self._list.add_to_front(node)
            return node.value

    def put(self, key: int, value: int) -> None:
        """Insert or update the value for *key*.

        If the cache is at capacity, the least recently used item is evicted
        before inserting the new entry.

        Complexity: O(1) average.
        """
        with self._lock:
            node = self._cache.get(key)
            if node is not None:
                # Key exists — update value and promote to MRU
                node.value = value
                self._list.remove(node)
                self._list.add_to_front(node)
            else:
                # Evict LRU entry if at capacity
                if len(self._cache) >= self.capacity:
                    last = self._list.remove_last()
                    if last is not None:
                        del self._cache[last.key]
                # Insert new node at front
                new_node = _Node(key, value)
                self._cache[key] = new_node
                self._list.add_to_front(new_node)

    def delete(self, key: int) -> bool:
        """Remove *key* and its value from the cache.

        Returns True if the key existed and was removed, False otherwise.

        Complexity: O(1) average.
        """
        with self._lock:
            node = self._cache.pop(key, None)
            if node is None:
                return False
            self._list.remove(node)
            return True


def lru_cache(capacity: int = 10) -> LRUCache:
    """Create a new LRU Cache instance (factory function).

    Args:
        capacity: Maximum number of items (default 10, minimum 1).

    Returns:
        A new LRUCache instance ready for use.

    Example:
        >>> cache = lru_cache(3)
        >>> cache.put(1, 10)
        >>> cache.get(1)
        10
        >>> cache.get(2)
        -1
    """
    return LRUCache(capacity)
