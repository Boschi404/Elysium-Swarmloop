"""
Graph BFS/DFS Traversal Implementation
=======================================
Graph represented as adjacency list (dict[str, list[str]]).

Functions:
    Graph — class with BFS, DFS, has_path, shortest_path.

    bfs(graph, start)          → list[str]  — breadth-first traversal order
    dfs(graph, start)          → list[str]  — depth-first traversal order
    has_path(graph, start, end) → bool       — BFS-based reachability check
    shortest_path(graph, start, end) → list[str] — BFS-based shortest path

    All handle cycles correctly via visited sets.

Time complexity:
    BFS/DFS/Shortest Path: O(V + E) where V = vertices, E = edges.
    has_path (BFS): O(V + E) worst case.
"""

from collections import deque
from typing import Dict, List, Optional


# ── Graph Class ────────────────────────────────────────────────────────────

class Graph:
    """Adjacency-list graph with BFS/DFS traversal utilities.

    Args:
        adjacency: A dict mapping each node → list of its neighbours.

    Raises:
        TypeError: If adjacency is not a dict.
        ValueError: If any value is not a list.
    """

    def __init__(self, adjacency: Dict[str, List[str]]) -> None:
        if not isinstance(adjacency, dict):
            raise TypeError("adjacency must be a dict")
        for node, neighbours in adjacency.items():
            if not isinstance(neighbours, list):
                raise ValueError(f"Neighbours of '{node}' must be a list")
            # Sanitise: ensure every neighbour key exists in the graph
            for nb in neighbours:
                if nb not in adjacency:
                    raise ValueError(
                        f"Neighbour '{nb}' of '{node}' is not a known node"
                    )
        self._graph: Dict[str, List[str]] = adjacency

    def __repr__(self) -> str:
        return f"Graph({len(self._graph)} nodes)"

    # ── Public API ────────────────────────────────────────────────────────

    def bfs(self, start: str) -> List[str]:
        """Breadth-first search traversal starting from *start*.

        Returns nodes in BFS discovery order. Cycles are handled via a
        visited set. If *start* is not in the graph, returns an empty list.
        """
        if start not in self._graph:
            return []

        visited: set[str] = set()
        order: list[str] = []
        queue: deque[str] = deque()

        visited.add(start)
        queue.append(start)

        while queue:
            node = queue.popleft()
            order.append(node)

            for neighbour in self._graph[node]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

        return order

    def dfs(self, start: str) -> List[str]:
        """Depth-first search traversal starting from *start*.

        Returns nodes in DFS pre-order. Cycles handled via visited set.
        Uses an explicit stack (iterative) to avoid Python recursion limits.
        If *start* is not in the graph, returns an empty list.
        """
        if start not in self._graph:
            return []

        visited: set[str] = set()
        order: list[str] = []
        stack: list[str] = [start]

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                order.append(node)
                # Push neighbours in reverse order so the leftmost
                # neighbour in the adjacency list is explored first.
                for neighbour in reversed(self._graph[node]):
                    if neighbour not in visited:
                        stack.append(neighbour)

        return order

    def has_path(self, start: str, end: str) -> bool:
        """Return True if there is a path from *start* to *end* (BFS).

        Returns False if either node does not exist in the graph.
        """
        if start not in self._graph or end not in self._graph:
            return False

        visited: set[str] = set()
        queue: deque[str] = deque()

        visited.add(start)
        queue.append(start)

        while queue:
            node = queue.popleft()
            if node == end:
                return True
            for neighbour in self._graph[node]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

        return False

    def shortest_path(self, start: str, end: str) -> List[str]:
        """Return the shortest path from *start* to *end* (BFS).

        BFS on an unweighted graph guarantees the shortest path (fewest
        edges). Returns an empty list if no path exists or either node is
        missing. The path includes both *start* and *end*.
        """
        if start not in self._graph or end not in self._graph:
            return []

        visited: set[str] = {start}
        queue: deque[str] = deque([start])
        parent: dict[str, Optional[str]] = {start: None}

        while queue:
            node = queue.popleft()
            if node == end:
                return self._reconstruct_path(parent, start, end)

            for neighbour in self._graph[node]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    parent[neighbour] = node
                    queue.append(neighbour)

        return []  # no path

    @staticmethod
    def _reconstruct_path(
        parent: Dict[str, Optional[str]], start: str, end: str
    ) -> List[str]:
        """Reconstruct path from parent pointers (internal helper)."""
        path: list[str] = []
        current: Optional[str] = end
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        return path


# ── Standalone convenience functions ───────────────────────────────────────

def bfs(graph: Dict[str, List[str]], start: str) -> List[str]:
    """BFS traversal; wraps :class:`Graph` for dict-only usage."""
    return Graph(graph).bfs(start)


def dfs(graph: Dict[str, List[str]], start: str) -> List[str]:
    """DFS traversal; wraps :class:`Graph` for dict-only usage."""
    return Graph(graph).dfs(start)


def has_path(
    graph: Dict[str, List[str]], start: str, end: str
) -> bool:
    """Reachability check; wraps :class:`Graph` for dict-only usage."""
    return Graph(graph).has_path(start, end)


def shortest_path(
    graph: Dict[str, List[str]], start: str, end: str
) -> List[str]:
    """Shortest path; wraps :class:`Graph` for dict-only usage."""
    return Graph(graph).shortest_path(start, end)
