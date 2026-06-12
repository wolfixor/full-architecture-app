"""Task management endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)
from ...services.task_service import task_service
from ...repositories.database import get_session
from ...repositories.task_repository import TaskRepository
import logging


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(session: AsyncSession = Depends(get_session)):
    """Get all tasks."""
    repository = TaskRepository(session)
    tasks = await task_service.get_tasks(repository)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, session: AsyncSession = Depends(get_session)):
    """Get task by ID."""
    repository = TaskRepository(session)
    task = await task_service.get_task(repository, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_create: TaskCreate, session: AsyncSession = Depends(get_session)):
    """Create a new task."""
    repository = TaskRepository(session)
    
    logger.info("Creating task ghasem=%s", task_create)
    logger.info("repository=%s", repository)
    
    return await task_service.create_task(
        repository,
        title=task_create.title,
        description=task_create.description
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskUpdate, session: AsyncSession = Depends(get_session)):
    """Update a task."""
    repository = TaskRepository(session)
    task = await task_service.update_task(repository, task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, session: AsyncSession = Depends(get_session)):
    """Delete a task."""
    repository = TaskRepository(session)
    if not await task_service.delete_task(repository, task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
