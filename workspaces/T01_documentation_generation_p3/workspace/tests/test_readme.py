"""Validate README.md against rubric criteria."""
import re

README_PATH = "C:/Users/Admin/Elysium-Swarmloop/workspaces/T01_documentation_generation_p3/workspace/README.md"


def load_readme() -> str:
    with open(README_PATH, encoding="utf-8") as f:
        return f.read()


def test_correctness():
    """Weight 40% — contains 'solution', min_length 100, regex 'generate|readme|for'."""
    text = load_readme()
    assert "solution" in text, "Must contain 'solution'"
    assert len(text) >= 100, f"Min length 100, got {len(text)}"
    assert re.search(r"generate|readme|for", text, re.IGNORECASE), (
        "Must match regex 'generate|readme|for'"
    )


def test_completeness():
    """Weight 25% — contains 'identify' and 'explain', min_length 200."""
    text = load_readme()
    assert "identify" in text, "Must contain 'identify'"
    assert "explain" in text, "Must contain 'explain'"
    assert len(text) >= 200, f"Min length 200, got {len(text)}"


def test_efficiency():
    """Weight 15% — contains 'concise', min_length 50."""
    text = load_readme()
    assert "concise" in text, "Must contain 'concise'"
    assert len(text) >= 50, f"Min length 50, got {len(text)}"


def test_robustness():
    """Weight 10% — contains 'edge case' and 'example'."""
    text = load_readme()
    assert "edge case" in text, "Must contain 'edge case'"
    assert "example" in text, "Must contain 'example'"


def test_clarity():
    """Weight 10% — has_structure '#' (headers), min_length 150."""
    text = load_readme()
    assert "#" in text, "Must have markdown headers (#)"
    assert len(text) >= 150, f"Min length 150, got {len(text)}"


def test_all_required_sections():
    """Verify all required sections from the task description exist."""
    text = load_readme()
    sections = [
        "Installation",
        "Configuration",
        "Usage",
        "API Reference",
        "Contributing",
        "License",
    ]
    for section in sections:
        # Check for markdown heading with section name
        assert re.search(
            rf"##+\s+{section}", text, re.IGNORECASE
        ), f"Missing '{section}' section"


def test_code_snippets():
    """Verify usage examples with code snippets exist."""
    text = load_readme()
    code_blocks = text.count("```")
    assert code_blocks >= 4, f"Expected at least 4 code blocks, got {code_blocks}"


if __name__ == "__main__":
    import sys

    tests = [
        test_correctness,
        test_completeness,
        test_efficiency,
        test_robustness,
        test_clarity,
        test_all_required_sections,
        test_code_snippets,
    ]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"  ✅ {test.__name__}")
        except AssertionError as e:
            print(f"  ❌ {test.__name__}: {e}")
            failures += 1
    print(f"\n{'All tests passed!' if failures == 0 else f'{failures} test(s) failed'}")
    sys.exit(failures)
