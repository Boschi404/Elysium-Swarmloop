"""Explicit tests verifying each of the 3 bug fixes for the User Service."""
import pytest


class TestBugFixVerification:
    """Explicitly verifies each of the 3 reported bugs is fixed."""

    # ------------------------------------------------------------------ #
    # Bug 1: GET /users/{id} crashes when user not found
    #   Instead of returning None (which FastAPI can't serialize),
    #   should return HTTP 404.
    # ------------------------------------------------------------------ #

    def test_bug1_get_nonexistent_user_returns_404(self, client):
        """GET /users/999 should return 404, not crash with 500."""
        response = client.get("/users/999")
        assert response.status_code == 404, (
            f"Expected 404 for missing user, got {response.status_code}"
        )
        data = response.json()
        assert "detail" in data, "Response should contain error detail"

    def test_bug1_get_existing_user_still_works(self, client):
        """Existing user lookup must still succeed after fix."""
        # Create a user first
        client.post("/users", json={"name": "Alice", "email": "a@b.com", "age": 30})
        response = client.get("/users/1")
        assert response.status_code == 200
        assert response.json()["name"] == "Alice"

    # ------------------------------------------------------------------ #
    # Bug 2: POST /users accepts empty names
    #   Should reject empty, whitespace-only, or too-short names.
    # ------------------------------------------------------------------ #

    @pytest.mark.parametrize("bad_name", ["", "   ", "\t\n"])
    def test_bug2_rejects_empty_name(self, client, bad_name):
        """POST with empty/whitespace name should return 422, not 201."""
        response = client.post(
            "/users", json={"name": bad_name, "email": "a@b.com", "age": 25}
        )
        assert response.status_code == 422, (
            f"Expected 422 for empty name, got {response.status_code}"
        )

    def test_bug2_valid_name_still_works(self, client):
        """Valid names must still be accepted."""
        response = client.post(
            "/users", json={"name": "Bob", "email": "b@c.com", "age": 28}
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Bob"

    # ------------------------------------------------------------------ #
    # Bug 3: PUT /users/{id} doesn't check if user exists
    #   Should return 404 when updating a non-existent user.
    # ------------------------------------------------------------------ #

    def test_bug3_update_nonexistent_user_returns_404(self, client):
        """PUT /users/999 should return 404, not silently fail or crash."""
        response = client.put(
            "/users/999", json={"name": "Ghost"}
        )
        assert response.status_code == 404, (
            f"Expected 404 for updating missing user, got {response.status_code}"
        )

    def test_bug3_update_existing_user_still_works(self, client):
        """Updates to existing users must still succeed."""
        client.post("/users", json={"name": "Carol", "email": "c@d.com", "age": 35})
        response = client.put(
            "/users/1", json={"name": "Carol Updated"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Carol Updated"

    # ------------------------------------------------------------------ #
    # Also verify PUT with empty name (cross-check with Bug 2 pattern)
    # ------------------------------------------------------------------ #

    def test_bug3_update_with_empty_name_rejected(self, client):
        """PUT should also reject empty name updates."""
        client.post("/users", json={"name": "Dave", "email": "d@e.com", "age": 40})
        response = client.put(
            "/users/1", json={"name": ""}
        )
        assert response.status_code == 422, (
            f"Expected 422 for empty name in PUT, got {response.status_code}"
        )
