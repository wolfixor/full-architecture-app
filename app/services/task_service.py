"""Task service for business logic."""

import uuid
from typing import List, Optional
from datetime import datetime
from ..models.task import TaskInDB, TaskStatus, TaskUpdate


class TaskRepository:
    """In-memory task repository."""
    
    def __init__(self):
        self._tasks = {}
    
    def get_all(self) -> List[TaskInDB]:
        """Get all tasks."""
        return list(self._tasks.values())
    
    def get_by_id(self, task_id: str) -> Optional[TaskInDB]:
        """Get task by ID."""
        return self._tasks.get(task_id)
    
    def create(self, task: TaskInDB) -> TaskInDB:
        """Create a new task."""
        self._tasks[task.id] = task
        return task
    
    def update(self, task_id: str, task_update: TaskUpdate) -> Optional[TaskInDB]:
        """Update a task."""
        if task_id not in self._tasks:
            return None
        
        task = self._tasks[task_id]
        
        # Update fields if provided
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        # Always update timestamp
        task.updated_at = datetime.utcnow()
        
        self._tasks[task_id] = task
        return task
    
    def delete(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False


class TaskService:
    """Task business logic service."""
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository
    
    def get_tasks(self) -> List[TaskInDB]:
        """Get all tasks."""
        return self.repository.get_all()
    
    def get_task(self, task_id: str) -> Optional[TaskInDB]:
        """Get task by ID."""
        return self.repository.get_by_id(task_id)
    
    def create_task(self, title: str, description: str = "") -> TaskInDB:
        """Create a new task."""
        task = TaskInDB(
            title=title,
            description=description
        )
        return self.repository.create(task)
    
    def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[TaskInDB]:
        """Update a task."""
        return self.repository.update(task_id, task_update)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        return self.repository.delete(task_id)


# Create default instance
task_repository = TaskRepository()
task_service = TaskService(task_repository)