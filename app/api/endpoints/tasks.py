"""Task management endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from ...models.task import TaskCreate, TaskUpdate, TaskResponse
from ...services.task_service import task_service


router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def get_tasks():
    """Get all tasks."""
    return task_service.get_tasks()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task by ID."""
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_create: TaskCreate):
    """Create a new task."""
    return task_service.create_task(
        title=task_create.title,
        description=task_create.description
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task."""
    task = task_service.update_task(task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Delete a task."""
    if not task_service.delete_task(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )