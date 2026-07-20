"""Business logic layer for Task Manager API.

This module contains all core business rules, data validation
beyond schema-level checks, and orchestrates operations between
the storage layer and the API handlers.
"""

from datetime import datetime
from typing import Sequence

from src.models import Task, TaskCreate, TaskStatus, TaskUpdate


class TaskNotFoundError(Exception):
    """Raised when a requested task does not exist."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task with id={task_id} not found")


class TaskService:
    """In-memory task store with business logic.

    Provides CRUD operations with validation rules such as:
    - Completed/cancelled tasks cannot be re-opened.
    - Priority clamping between 1 and 5.
    - Automatic timestamp updates on modification.
    """

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, payload: TaskCreate) -> Task:
        """Create a new task from the given payload.

        Args:
            payload: Validated creation data.

        Returns:
            The newly created Task with system-assigned id and timestamps.
        """
        now = datetime.utcnow()
        task = Task(
            id=self._next_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_all(self, page: int = 1, page_size: int = 20) -> tuple[Sequence[Task], int]:
        """Return a paginated snapshot of all tasks.

        Args:
            page: 1-indexed page number.
            page_size: Number of items per page (max 100).

        Returns:
            Tuple of (items_on_page, total_count).
        """
        sorted_tasks = sorted(self._tasks.values(), key=lambda t: t.created_at, reverse=True)
        total = len(sorted_tasks)
        start = (page - 1) * page_size
        end = start + page_size
        return sorted_tasks[start:end], total

    def get_by_id(self, task_id: int) -> Task:
        """Retrieve a single task by its id.

        Args:
            task_id: The unique identifier.

        Returns:
            The matching Task.

        Raises:
            TaskNotFoundError: If no task with the given id exists.
        """
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def update(self, task_id: int, payload: TaskUpdate) -> Task:
        """Apply a partial update to an existing task.

        Rules enforced:
        - Completed or cancelled tasks cannot change status.
        - Title must be non-empty if provided.
        - Priority must stay within [1, 5].

        Args:
            task_id: Target task identifier.
            payload: Fields to update.

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If the task does not exist.
            ValueError: If the update violates business rules.
        """
        task = self.get_by_id(task_id)

        if payload.status is not None:
            if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
                raise ValueError(
                    f"Cannot change status of a {task.status.value} task"
                )

        update_data = payload.model_dump(exclude_unset=True)

        if "title" in update_data and not update_data["title"].strip():
            raise ValueError("Title must not be empty")

        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        return task

    def delete(self, task_id: int) -> None:
        """Delete a task by its id.

        Args:
            task_id: The unique identifier of the task to remove.

        Raises:
            TaskNotFoundError: If no task with the given id exists.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]
