"""Task Management API — FastAPI implementation with in-memory storage.

Endpoints:
    GET    /tasks           — list tasks, optional ?status=todo|done|all
    GET    /tasks/{id}      — retrieve a single task
    POST   /tasks           — create a new task
    PUT    /tasks/{id}      — update all fields of a task
    PATCH  /tasks/{id}/status — toggle task status
    DELETE /tasks/{id}      — delete a task
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(title="Task Management API", version="1.0.0")

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TaskStatus(str, Enum):
    """Allowed status values for a task."""

    todo = "todo"
    done = "done"


class TaskCreate(BaseModel):
    """Request body for creating a new task."""

    title: str
    description: Optional[str] = None
    due_date: date

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be empty")
        return stripped

    @field_validator("due_date")
    @classmethod
    def due_date_must_not_be_in_past(cls, v: date) -> date:
        """Allow today or future dates."""
        if v < date.today():
            raise ValueError("due_date must be today or later")
        return v


class TaskUpdate(BaseModel):
    """Request body for updating a task (all fields optional except at least one required)."""

    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("title must not be empty")
            return stripped
        return v

    @field_validator("due_date")
    @classmethod
    def due_date_must_not_be_in_past(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v < date.today():
            raise ValueError("due_date must be today or later")
        return v


class Task(BaseModel):
    """Read-only representation of a task (returned by API)."""

    id: UUID
    title: str
    description: Optional[str] = None
    due_date: date
    status: TaskStatus = TaskStatus.todo
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_store: dict[UUID, Task] = {}


def _sorted_tasks() -> list[Task]:
    """Return all tasks sorted by due_date ascending (None last)."""
    return sorted(_store.values(), key=lambda t: (t.due_date if t.due_date else date.max, t.created_at))


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status: todo, done, or all"),
) -> list[Task]:
    """Return tasks, optionally filtered by status, sorted by due_date ascending."""
    tasks = _sorted_tasks()

    if status is not None and status != "all":
        try:
            filter_val = TaskStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status}'. Must be 'todo', 'done', or 'all'.",
            )
        tasks = [t for t in tasks if t.status == filter_val]

    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: UUID) -> Task:
    """Return a single task by ID."""
    task = _store.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found.",
        )
    return task


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(body: TaskCreate) -> Task:
    """Create a new task."""
    now = datetime.utcnow()
    task = Task(
        id=uuid4(),
        title=body.title,
        description=body.description,
        due_date=body.due_date,
        status=TaskStatus.todo,
        created_at=now,
        updated_at=now,
    )
    _store[task.id] = task
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: UUID, body: TaskUpdate) -> Task:
    """Update an existing task (partial update with at least one field)."""
    if body.title is None and body.description is None and body.due_date is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field (title, description, due_date) must be provided.",
        )

    existing = _store.get(task_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found.",
        )

    updated = existing.model_copy(
        update={
            k: v
            for k, v in {
                "title": body.title,
                "description": body.description,
                "due_date": body.due_date,
            }.items()
            if v is not None
        }
    )
    updated.updated_at = datetime.utcnow()
    _store[task_id] = updated
    return updated


@app.patch("/tasks/{task_id}/status", response_model=Task)
def toggle_task_status(task_id: UUID) -> Task:
    """Toggle the status of a task between todo ↔ done."""
    existing = _store.get(task_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found.",
        )

    new_status = TaskStatus.done if existing.status == TaskStatus.todo else TaskStatus.todo
    updated = existing.model_copy(update={"status": new_status, "updated_at": datetime.utcnow()})
    _store[task_id] = updated
    return updated


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID) -> None:
    """Delete a task by ID. Returns 204 on success."""
    if task_id not in _store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found.",
        )
    del _store[task_id]
