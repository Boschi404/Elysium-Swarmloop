"""Test: verify the syllogism counterexample using set logic."""


def test_syllogism_invalid():
    """Verify premises can be true while conclusion is false."""
    # Domain: Alice, Bob
    programmers = {"Alice"}
    logical = {"Alice", "Bob"}
    mathematicians = {"Bob"}

    # Premise 1: All programmers are logical
    assert programmers.issubset(logical), "All programmers must be logical"

    # Premise 2: Some logical people are mathematicians
    assert logical & mathematicians, "Some logical people must be mathematicians"

    # Conclusion: Some programmers are mathematicians (should FAIL)
    # programmers ∩ mathematicians should be empty
    assert not (programmers & mathematicians), (
        "Conclusion claims some programmers are mathematicians, "
        "but in the counterexample none are"
    )


def test_fallacy_type():
    """Document the specific fallacy."""
    fallacy = "Undistributed Middle Term"
    assert fallacy == "Undistributed Middle Term"
