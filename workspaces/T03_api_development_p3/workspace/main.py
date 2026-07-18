"""
Task Management API (FastAPI)

Endpoints:
  - GET    /tasks          List tasks (filter by ?status=todo|done|all)
  - GET    /tasks/{id}     Get a single task
  - POST   /tasks          Create a new task
  - PUT    /tasks/{id}     Update all fields of a task
  - PATCH  /tasks/{id}/status  Toggle task status
  - DELETE /tasks/{id}     Delete a task
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Task API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TaskStatus(str, Enum):
    """Allowed task statuses."""

    todo = "todo"
    done = "done"


class TaskCreate(BaseModel):
    """Request body for POST /tasks."""

    title: str = Field(..., min_length=1, description="Task title (required)")
    description: Optional[str] = Field(None, description="Optional description")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                date.fromisoformat(v)
            except (ValueError, TypeError):
                raise ValueError("due_date must be a valid date in YYYY-MM-DD format")
        return v

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    """Request body for PUT /tasks/{id}."""

    title: Optional[str] = Field(None, min_length=1, description="Task title")
    description: Optional[str] = Field(None, description="Optional description")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    status: Optional[TaskStatus] = Field(None, description="Task status")

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                date.fromisoformat(v)
            except (ValueError, TypeError):
                raise ValueError("due_date must be a valid date in YYYY-MM-DD format")
        return v

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("title must not be empty")
        return v.strip() if v else v


class TaskOut(BaseModel):
    """Response model for a task."""

    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    due_date: Optional[str] = None
    created_at: str


# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_tasks: list[dict] = []
_next_id: int = 1


def _now_iso() -> str:
    return datetime.now().isoformat()


def _sorted_by_due_date(tasks: list[dict]) -> list[dict]:
    """Sort tasks ascending by due_date (None sorts last)."""
    def sort_key(t: dict) -> tuple:
        d = t.get("due_date")
        if d is None:
            return (1, "")  # None after any date
        return (0, d)
    return sorted(tasks, key=sort_key)


def _find_task(task_id: int) -> Optional[dict]:
    for t in _tasks:
        if t["id"] == task_id:
            return t
    return None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(status: str = Query("all", description="Filter by status: todo, done, or all")) -> list[dict]:
    """Return tasks sorted by due_date ascending.  Optional ?status filter."""
    if status not in ("todo", "done", "all"):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status '{status}'. Must be 'todo', 'done', or 'all'.",
        )

    filtered = _tasks
    if status != "all":
        filtered = [t for t in _tasks if t["status"].value == status]

    return _sorted_by_due_date(filtered)


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int) -> dict:
    """Return a single task by id."""
    task = _find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(body: TaskCreate) -> dict:
    """Create a new task."""
    global _next_id

    task: dict = {
        "id": _next_id,
        "title": body.title,
        "description": body.description,
        "status": TaskStatus.todo,
        "due_date": body.due_date,
        "created_at": _now_iso(),
    }
    _next_id += 1
    _tasks.append(task)
    return task


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, body: TaskUpdate) -> dict:
    """Update fields of an existing task."""
    task = _find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    if body.title is not None:
        task["title"] = body.title
    if body.description is not None:
        task["description"] = body.description
    if body.due_date is not None:
        task["due_date"] = body.due_date
    if body.status is not None:
        task["status"] = body.status

    return task


@app.patch("/tasks/{task_id}/status", response_model=TaskOut)
def toggle_status(task_id: int) -> dict:
    """Toggle a task's status between todo and done."""
    task = _find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    task["status"] = TaskStatus.done if task["status"] == TaskStatus.todo else TaskStatus.todo
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    """Delete a task by id."""
    task = _find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    _tasks.remove(task)
