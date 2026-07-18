"""
UserService — BUGGY VERSION

Known bugs:
  1. GET /users/{id} crashes when user is not found (returns None → 500 instead of 404)
  2. POST /users accepts empty names
  3. PUT /users/{id} doesn't check if user exists (creates phantom entry)
"""

from typing import Optional
from app.models import User, UserCreate, UserUpdate, generate_id


class UserService:
    """In-memory user service. Contains intentional bugs for T01."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def create_user(self, payload: UserCreate) -> User:
        """BUG 2: accepts empty names because it bypasses payload validation."""
        # BUG: strips whitespace but doesn't reject empty strings
        name = payload.name.strip()
        if not name:
            name = payload.name  # BUG: uses original (could be whitespace-only)
        user = User(id=generate_id(), name=name)
        self._users[user.id] = user
        return user

    def get_user(self, user_id: str) -> User:
        """BUG 1: returns None instead of raising an error when user not found."""
        return self._users.get(user_id)  # BUG: .get() returns None, caller gets 500

    def update_user(self, user_id: str, payload: UserUpdate) -> User:
        """BUG 3: doesn't check if user exists before updating."""
        user = self._users.get(user_id)
        # BUG: if user is None, this crashes on AttributeError
        if payload.name is not None:
            user.name = payload.name
        return user

    def delete_user(self, user_id: str) -> bool:
        """Delete a user. Returns True if deleted, False if not found."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def list_users(self) -> list[User]:
        return list(self._users.values())
