"""Tests for Graph BFS/DFS Traversal (T04_algorithm_implementation)."""

import pytest
import time
import random


class TestGraphTraversal:

    @pytest.fixture
    def solution(self):
        """Import the solution module."""
        try:
            import main
            return main
        except ImportError:
            pytest.skip("main.py not found")

    # ── Standard test graph ───────────────────────────────────────────────

    @pytest.fixture
    def simple_graph(self):
        """A simple linear-ish graph (no cycles)."""
        return {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["E"],
            "D": [],
            "E": [],
        }

    @pytest.fixture
    def cyclic_graph(self):
        """A graph with multiple cycles."""
        return {
            "A": ["B", "C"],
            "B": ["D", "E"],
            "C": ["F"],
            "D": ["A"],       # back to A (cycle)
            "E": ["B"],       # back to B (cycle)
            "F": ["C", "G"],  # back to C (cycle)
            "G": [],
        }

    @pytest.fixture
    def disconnected_graph(self):
        """Graph with disconnected components."""
        return {
            "A": ["B"],
            "B": ["A"],
            "C": ["D"],
            "D": ["C"],
            "E": [],
        }

    @pytest.fixture
    def small_graph(self):
        """Small graph for exhaustive BFS/DFS tests."""
        return {
            "0": ["1", "2"],
            "1": ["0", "3", "4"],
            "2": ["0", "5"],
            "3": ["1"],
            "4": ["1"],
            "5": ["2"],
        }

    # ── Module import ─────────────────────────────────────────────────────

    def test_module_imports(self, solution):
        """Verify the solution module is importable."""
        assert solution is not None

    def test_basic_case(self, solution):
        """Verify basic functionality: at least one callable function."""
        funcs = [f for f in dir(solution) if callable(getattr(solution, f))
                 and not f.startswith('_') and f not in ('app', 'main')]
        assert len(funcs) > 0, \
            f"No public functions found in module. Found: {dir(solution)}"

    # ── Graph class instantiation ─────────────────────────────────────────

    def test_graph_construction(self, solution):
        """Verify Graph can be constructed from an adjacency dict."""
        G = solution.Graph({"A": ["B"], "B": []})
        assert G is not None

    def test_graph_invalid_input(self, solution):
        """Verify ValueError/TypeError on bad input."""
        with pytest.raises(TypeError):
            solution.Graph("not a dict")
        with pytest.raises(ValueError):
            solution.Graph({"A": "not a list"})
        with pytest.raises(ValueError):
            solution.Graph({"A": ["B"]})  # B is missing as a key

    # ── BFS — correctness ─────────────────────────────────────────────────

    def test_bfs_simple(self, solution, simple_graph):
        """BFS on a small acyclic graph."""
        result = solution.bfs(simple_graph, "A")
        # BFS should visit A → B → C → D → E
        assert result == ["A", "B", "C", "D", "E"], f"Got {result}"

    def test_bfs_cyclic(self, solution, cyclic_graph):
        """BFS on a graph with cycles must not loop."""
        result = solution.bfs(cyclic_graph, "A")
        assert len(result) == len(cyclic_graph), \
            f"Expected {len(cyclic_graph)} nodes, got {result}"
        assert "A" in result
        assert result[0] == "A"

    def test_bfs_disconnected(self, solution, disconnected_graph):
        """BFS from a node should not reach other components."""
        result = solution.bfs(disconnected_graph, "A")
        assert "A" in result
        assert "B" in result
        assert "C" not in result  # different component
        assert "D" not in result
        assert "E" not in result

    def test_bfs_nonexistent_start(self, solution, simple_graph):
        """BFS on a non-existent start returns empty list."""
        result = solution.bfs(simple_graph, "Z")
        assert result == []

    def test_bfs_single_node(self, solution):
        """BFS on a single-node graph returns just that node."""
        graph = {"X": []}
        result = solution.bfs(graph, "X")
        assert result == ["X"]

    # ── DFS — correctness ─────────────────────────────────────────────────

    def test_dfs_simple(self, solution, simple_graph):
        """DFS on a small acyclic graph (pre-order)."""
        result = solution.dfs(simple_graph, "A")
        # DFS: A → C → E (back) → B → D
        assert set(result) == set(["A", "B", "C", "D", "E"]), f"Got {result}"
        assert result[0] == "A"
        # Every node appears exactly once
        assert len(result) == len(set(result))

    def test_dfs_cyclic(self, solution, cyclic_graph):
        """DFS on cyclic graph must not loop."""
        result = solution.dfs(cyclic_graph, "A")
        # Every node appears exactly once (no repeats)
        assert len(result) == len(set(result)), f"Duplicates in {result}"
        assert len(result) == len(cyclic_graph)

    def test_dfs_disconnected(self, solution, disconnected_graph):
        """DFS from a node should not traverse other components."""
        result = solution.dfs(disconnected_graph, "A")
        assert "A" in result
        assert "B" in result
        assert "C" not in result

    def test_dfs_nonexistent_start(self, solution, simple_graph):
        """DFS on a non-existent start returns empty list."""
        result = solution.dfs(simple_graph, "Z")
        assert result == []

    def test_dfs_single_node(self, solution):
        """DFS on a single-node graph returns just that node."""
        graph = {"X": []}
        result = solution.dfs(graph, "X")
        assert result == ["X"]

    def test_dfs_all_visited(self, solution, small_graph):
        """DFS visits all reachable nodes exactly once."""
        result = solution.dfs(small_graph, "0")
        assert len(result) == len(small_graph)
        assert len(result) == len(set(result)), f"Duplicates in {result}"

    # ── has_path — correctness ────────────────────────────────────────────

    def test_has_path_existing(self, solution, simple_graph):
        """has_path returns True when a path exists."""
        assert solution.has_path(simple_graph, "A", "D") is True
        assert solution.has_path(simple_graph, "A", "E") is True
        assert solution.has_path(simple_graph, "B", "D") is True

    def test_has_path_missing(self, solution, simple_graph):
        """has_path returns False when no path exists."""
        assert solution.has_path(simple_graph, "D", "A") is False

    def test_has_path_disconnected(self, solution, disconnected_graph):
        """has_path returns False across disconnected components."""
        assert solution.has_path(disconnected_graph, "A", "C") is False
        assert solution.has_path(disconnected_graph, "E", "A") is False

    def test_has_path_cyclic(self, solution, cyclic_graph):
        """has_path works correctly on cyclic graphs."""
        assert solution.has_path(cyclic_graph, "A", "G") is True
        assert solution.has_path(cyclic_graph, "D", "E") is True
        assert solution.has_path(cyclic_graph, "G", "A") is False

    def test_has_path_same_node(self, solution, simple_graph):
        """has_path from a node to itself returns True."""
        assert solution.has_path(simple_graph, "A", "A") is True

    def test_has_path_nonexistent(self, solution, simple_graph):
        """has_path with a missing node returns False."""
        assert solution.has_path(simple_graph, "Z", "A") is False
        assert solution.has_path(simple_graph, "A", "Z") is False

    # ── shortest_path — correctness ───────────────────────────────────────

    def test_shortest_path_direct(self, solution, simple_graph):
        """Shortest path between directly connected nodes."""
        result = solution.shortest_path(simple_graph, "A", "B")
        assert result == ["A", "B"], f"Got {result}"

    def test_shortest_path_indirect(self, solution, simple_graph):
        """Shortest path between indirectly connected nodes."""
        result = solution.shortest_path(simple_graph, "A", "D")
        # A → B → D (2 edges)
        assert result == ["A", "B", "D"], f"Got {result}"

    def test_shortest_path_cyclic(self, solution, cyclic_graph):
        """Shortest path on cyclic graph should still be shortest."""
        result = solution.shortest_path(cyclic_graph, "A", "G")
        # A → C → F → G (3 edges — the shortest)
        assert result == ["A", "C", "F", "G"], f"Got {result}"

    def test_shortest_path_no_path(self, solution, simple_graph):
        """No path returns empty list."""
        result = solution.shortest_path(simple_graph, "D", "A")
        assert result == []

    def test_shortest_path_same_node(self, solution, simple_graph):
        """Shortest path to self returns [node]."""
        result = solution.shortest_path(simple_graph, "A", "A")
        assert result == ["A"], f"Got {result}"

    def test_shortest_path_nonexistent(self, solution, simple_graph):
        """Missing nodes return empty list."""
        assert solution.shortest_path(simple_graph, "Z", "A") == []
        assert solution.shortest_path(simple_graph, "A", "Z") == []

    def test_shortest_path_disconnected(self, solution, disconnected_graph):
        """Across disconnected components returns empty list."""
        assert solution.shortest_path(disconnected_graph, "A", "C") == []

    # ── Edge cases ────────────────────────────────────────────────────────

    def test_edge_case_duplicates(self, solution):
        """Verify handling of a graph with duplicate connections."""
        graph = {"A": ["B", "B", "C"], "B": ["A"], "C": []}
        # BFS should handle duplicate neighbours gracefully
        bfs_result = solution.bfs(graph, "A")
        assert len(bfs_result) == len(set(bfs_result)), \
            f"Duplicates in BFS: {bfs_result}"

    def test_empty_graph(self, solution):
        """Empty adjacency dict should not break anything."""
        graph = {}
        assert solution.bfs(graph, "A") == []
        assert solution.dfs(graph, "A") == []
        assert solution.has_path(graph, "A", "B") is False
        assert solution.shortest_path(graph, "A", "B") == []

    def test_no_stubs(self, solution):
        """Verify no stub code."""
        import inspect
        source = inspect.getsource(solution)
        assert "TODO" not in source, "TODO found"
        assert "pass" not in source.split('\n'), "Empty pass statement found"
        assert "raise NotImplementedError" not in source

    def test_type_hints(self, solution):
        """Verify functions have basic type hints."""
        import inspect
        funcs = inspect.getmembers(solution, inspect.isfunction)
        public_funcs = [(n, f) for n, f in funcs if not n.startswith('_')]
        if public_funcs:
            hints_found = False
            for name, fn in public_funcs:
                sig = inspect.signature(fn)
                if (sig.return_annotation is not inspect.Parameter.empty or
                    any(p.annotation is not inspect.Parameter.empty
                        for p in sig.parameters.values())):
                    hints_found = True
                    break
            assert hints_found, "No type hints in any public function"

    # ── Performance ───────────────────────────────────────────────────────

    def test_performance_large_input(self, solution):
        """Verify the algorithm handles large graphs within time constraints."""
        # Build a chain graph with 10 000 nodes
        n = 10000
        graph = {str(i): [str(i + 1)] for i in range(n - 1)}
        graph[str(n - 1)] = []

        start = time.time()
        result = solution.bfs(graph, "0")
        elapsed = time.time() - start

        assert len(result) == n, f"Only visited {len(result)}/{n} nodes"
        assert elapsed < 5.0, f"Performance issue: {elapsed:.2f}s for {n} nodes"

    def test_performance_shortest_path(self, solution):
        """Shortest path on a large graph must complete quickly."""
        n = 5000
        graph = {str(i): [str(i + 1)] for i in range(n - 1)}
        graph[str(n - 1)] = []

        start = time.time()
        result = solution.shortest_path(graph, "0", str(n - 1))
        elapsed = time.time() - start

        assert len(result) == n, f"Path length {len(result)} vs expected {n}"
        assert elapsed < 5.0, f"Performance: {elapsed:.2f}s for {n} nodes"
