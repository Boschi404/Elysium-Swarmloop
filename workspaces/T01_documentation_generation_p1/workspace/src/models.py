"""Data models for the Task Manager API."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Enumeration of possible task statuses."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskBase(BaseModel):
    """Base task schema shared across create/read/update operations."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=2000, description="Detailed task description")
    priority: int = Field(default=1, ge=1, le=5, description="Priority level (1=lowest, 5=highest)")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for partial task update. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    priority: int | None = Field(None, ge=1, le=5)
    status: TaskStatus | None = None


class Task(TaskBase):
    """Full task model with system-managed fields."""

    id: int = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of creation")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last update")

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Wrapper for paginated task list responses."""

    items: list[Task]
    total: int
    page: int
    page_size: int
