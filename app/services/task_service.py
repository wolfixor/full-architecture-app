"""Task service for business logic."""

from typing import List, Optional
from ..schemas.task import (
    TaskUpdate
)
from ..repositories.task_repository import TaskRepository
from ..repositories.cache_repository import CacheRepository
from ..models.task import Task


class TaskService:
    """Task business logic service."""
    
    async def get_tasks(self, repository: TaskRepository) -> List[Task]:
        """Get all tasks with caching."""
        cache_repo = CacheRepository(repository)
        return await cache_repo.get_all()
    
    async def get_task(self, repository: TaskRepository, task_id: str) -> Optional[Task]:
        """Get task by ID with caching."""
        cache_repo = CacheRepository(repository)
        return await cache_repo.get_by_id(task_id)
    
    async def create_task(self, repository: TaskRepository, title: str, description: str = "") -> Task:
        """Create a new task with cache invalidation."""
        cache_repo = CacheRepository(repository)
        return await cache_repo.create(title, description)
    
    async def update_task(self, repository: TaskRepository, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Update a task with cache invalidation."""
        cache_repo = CacheRepository(repository)
        return await cache_repo.update(task_id, task_update)
    
    async def delete_task(self, repository: TaskRepository, task_id: str) -> bool:
        """Delete a task with cache invalidation."""
        cache_repo = CacheRepository(repository)
        return await cache_repo.delete(task_id)


# Create default instance
task_service = TaskService()
