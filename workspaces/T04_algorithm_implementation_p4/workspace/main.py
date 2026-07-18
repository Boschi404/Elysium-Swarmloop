"""Graph BFS/DFS Traversal — adjacency list representation.

Provides:
  - bfs(graph, start)  → list of nodes in BFS order
  - dfs(graph, start)  → list of nodes in DFS order
  - has_path(graph, start, end)  → bool
  - shortest_path(graph, start, end)  → list of nodes

All algorithms handle cycles via a visited set. Graph is a dict
mapping node → list of neighbour nodes (adjacency list).
"""

from collections import deque
from typing import Any


def bfs(graph: dict[Any, list[Any]], start: Any) -> list[Any]:
    """Breadth-first search traversal.

    Input:  graph as adjacency list, start node.
    Output: list of nodes in BFS order (level-order).
    Handles cycles and disconnected neighbours.
    """
    if start not in graph:
        return []

    visited: set[Any] = {start}
    queue: deque[Any] = deque([start])
    order: list[Any] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return order


def dfs(graph: dict[Any, list[Any]], start: Any) -> list[Any]:
    """Depth-first search traversal (iterative).

    Input:  graph as adjacency list, start node.
    Output: list of nodes in DFS order (pre-order).
    Handles cycles and disconnected neighbours.
    """
    if start not in graph:
        return []

    visited: set[Any] = {start}
    stack: list[Any] = [start]
    order: list[Any] = []

    while stack:
        node = stack.pop()
        order.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                visited.add(neighbour)
                stack.append(neighbour)

    return order


def has_path(graph: dict[Any, list[Any]], start: Any, end: Any) -> bool:
    """Check if a path exists between *start* and *end* using BFS.

    Input:  graph as adjacency list, start node, end node.
    Output: True if *end* is reachable from *start*, False otherwise.
    """
    if start not in graph or end not in graph:
        return False
    if start == end:
        return True

    visited: set[Any] = {start}
    queue: deque[Any] = deque([start])

    while queue:
        node = queue.popleft()
        for neighbour in graph.get(node, []):
            if neighbour == end:
                return True
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return False


def shortest_path(
    graph: dict[Any, list[Any]], start: Any, end: Any,
) -> list[Any]:
    """Find the shortest path between *start* and *end* using BFS.

    Input:  graph as adjacency list, start node, end node.
    Output: list of nodes forming the shortest path (start → … → end),
            or an empty list if no path exists.
    """
    if start not in graph or end not in graph:
        return []
    if start == end:
        return [start]

    visited: set[Any] = {start}
    queue: deque[Any] = deque([start])
    # parent[node] = previous node on the shortest path from start
    parent: dict[Any, Any | None] = {start: None}

    while queue:
        node = queue.popleft()
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                visited.add(neighbour)
                parent[neighbour] = node
                queue.append(neighbour)
                if neighbour == end:
                    # Reconstruct path by walking backwards
                    path: list[Any] = []
                    curr: Any | None = end
                    while curr is not None:
                        path.append(curr)
                        curr = parent[curr]
                    path.reverse()
                    return path

    return []
