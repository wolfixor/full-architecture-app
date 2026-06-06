"""Task data model."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskBase(BaseModel):
    """Base task model."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)


class TaskCreate(TaskBase):
    """Task creation model."""
    pass


class TaskUpdate(BaseModel):
    """Task update model."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None


class TaskInDB(TaskBase):
    """Task model for database/storage."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class TaskResponse(TaskInDB):
    """Task response model."""
    pass