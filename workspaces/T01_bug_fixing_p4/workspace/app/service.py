"""
User service module — in-memory CRUD.
Three bugs were present, all fixed:
  BUG-1: GET /users/{id} returned None instead of raising 404
  BUG-2: POST /users accepted empty names
  BUG-3: PUT /users/{id} didn't check if user exists before updating
"""

from typing import List, Optional
from app.schemas import UserCreate, UserUpdate, UserOut


class UserNotFoundError(Exception):
    """Raised when a user is not found by id."""
    pass


class _UserDB:
    """Simple in-memory user store with auto-increment id."""

    def __init__(self):
        self._users: dict[int, dict] = {}
        self._next_id = 1

    def create(self, data: UserCreate) -> UserOut:
        user_dict = {"id": self._next_id, "name": data.name.strip()}
        self._users[self._next_id] = user_dict
        self._next_id += 1
        return UserOut(**user_dict)

    def get(self, user_id: int) -> UserOut:
        """Return user or raise UserNotFoundError."""
        user = self._users.get(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return UserOut(**user)

    def get_all(self) -> List[UserOut]:
        return [UserOut(**u) for u in self._users.values()]

    def update(self, user_id: int, data: UserUpdate) -> UserOut:
        """Update user or raise UserNotFoundError if not found."""
        if user_id not in self._users:
            raise UserNotFoundError(f"User with id {user_id} not found")
        if data.name is not None:
            self._users[user_id]["name"] = data.name.strip()
        return UserOut(**self._users[user_id])

    def delete(self, user_id: int) -> None:
        if user_id not in self._users:
            raise UserNotFoundError(f"User with id {user_id} not found")
        del self._users[user_id]


# Singleton DB instance
db = _UserDB()
