"""HTTP API routes for the Task Manager.

This module defines the FastAPI router with all REST endpoints
for managing tasks. Input validation is handled by Pydantic
schemas from src.models; business logic lives in src.services.
"""

from typing import Sequence

from fastapi import APIRouter, HTTPException, Query, status

from src.models import Task, TaskCreate, TaskListResponse, TaskUpdate
from src.services import TaskNotFoundError, TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Singleton service instance (in production, injected via dependency)
_service = TaskService()


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> TaskListResponse:
    """Retrieve all tasks with pagination.

    Returns tasks sorted by creation date (newest first).
    """
    items: Sequence[Task]
    items, total = _service.list_all(page=page, page_size=page_size)
    return TaskListResponse(items=list(items), total=total, page=page, page_size=page_size)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate) -> Task:
    """Create a new task.

    The task is created with status ``pending`` and system-assigned
    timestamps.
    """
    return _service.create(payload)


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int) -> Task:
    """Retrieve a single task by its unique identifier."""
    try:
        return _service.get_by_id(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/{task_id}", response_model=Task)
async def update_task(task_id: int, payload: TaskUpdate) -> Task:
    """Partially update an existing task.

    Only the provided fields are modified.  Completed or cancelled
    tasks cannot have their status changed.
    """
    try:
        return _service.update(task_id, payload)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int) -> None:
    """Delete a task permanently."""
    try:
        _service.delete(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
