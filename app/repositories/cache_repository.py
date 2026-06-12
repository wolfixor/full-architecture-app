"""Cache repository for Redis caching."""

import json
from typing import List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime
import logging

from .task_repository import TaskRepository
from ..models.task import Task
from ..schemas.task import TaskUpdate
from ..core.redis import redis_client
from ..core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheRepository(Generic[T]):
    """Cache repository that wraps another repository with Redis caching."""
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository
        self.cache_prefix = "task:"
        self.cache_ttl = settings.REDIS_CACHE_TTL
    
    def _get_cache_key(self, key: str) -> str:
        """Get cache key with prefix."""
        return f"{self.cache_prefix}{key}"
    
    def _serialize(self, obj: T) -> str:
        """Serialize object to JSON."""
        if isinstance(obj, Task):
            return json.dumps({
                "id": str(obj.id),
                "title": obj.title,
                "description": obj.description,
                "status": obj.status,
                "created_at": obj.created_at.isoformat() if obj.created_at else None,
                "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
            })
        elif isinstance(obj, list):
            return json.dumps([self._serialize(item) for item in obj])
        return json.dumps(obj)
    
    def _deserialize_task(self, data: str) -> Task:
        """Deserialize JSON to Task."""
        obj = json.loads(data)
        task = Task(
            id=obj["id"],
            title=obj["title"],
            description=obj["description"],
            status=obj["status"]
        )
        task.created_at = datetime.fromisoformat(obj["created_at"]) if obj["created_at"] else None
        task.updated_at = datetime.fromisoformat(obj["updated_at"]) if obj["updated_at"] else None
        return task
    
    async def _get_from_cache(self, key: str) -> Optional[T]:
        """Get value from cache."""
        try:
            client = await redis_client.get_client()
            cached = await client.get(self._get_cache_key(key))
            if cached:
                logger.info(f"CACHE HIT for key: {key}")
                return self._deserialize_task(cached)
            logger.info(f"CACHE MISS for key: {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache read error for key {key}: {e}")
            return None
    
    async def _set_to_cache(self, key: str, value: T):
        """Set value to cache."""
        try:
            client = await redis_client.get_client()
            await client.setex(
                self._get_cache_key(key),
                self.cache_ttl,
                self._serialize(value)
            )
            logger.info(f"CACHE SET for key: {key}")
        except Exception as e:
            logger.warning(f"Cache write error for key {key}: {e}")
    
    async def _delete_from_cache(self, key: str):
        """Delete value from cache."""
        try:
            client = await redis_client.get_client()
            await client.delete(self._get_cache_key(key))
            logger.info(f"CACHE DELETED for key: {key}")
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
    
    async def _invalidate_task_cache(self, task_id: str):
        """Invalidate task cache."""
        await self._delete_from_cache(task_id)
        # Also invalidate all tasks list
        await self._delete_from_cache("all")
    
    # TaskRepository methods with caching
    async def get_all(self) -> List[Task]:
        """Get all tasks with caching."""
        cache_key = "all"
        try:
            # Try to get from cache first
            client = await redis_client.get_client()
            cached = await client.get(self._get_cache_key(cache_key))
            if cached:
                tasks_data = json.loads(cached)
                tasks = [self._deserialize_task(task_str) for task_str in tasks_data]
                logger.info("CACHE HIT for all tasks")
                return tasks
            else:
                logger.info("CACHE MISS for all tasks")
        except Exception as e:
            logger.warning(f"Cache read error for all tasks: {e}")
        
        # Get from database
        logger.info("Reading tasks from DATABASE")
        tasks = await self.repository.get_all()
        
        # Cache the result
        try:
            client = await redis_client.get_client()
            tasks_serialized = [self._serialize(task) for task in tasks]
            await client.setex(
                self._get_cache_key(cache_key),
                self.cache_ttl,
                json.dumps(tasks_serialized)
            )
            logger.info("CACHED all tasks")
        except Exception as e:
            logger.warning(f"Cache write error for all tasks: {e}")
        
        return tasks
    
    async def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID with caching."""
        # Try cache first
        cached_task = await self._get_from_cache(task_id)
        if cached_task:
            logger.info(f"Returning task {task_id} from CACHE")
            return cached_task
        
        # Get from database
        logger.info(f"Reading task {task_id} from DATABASE")
        task = await self.repository.get_by_id(task_id)
        
        # Cache the result
        if task:
            await self._set_to_cache(task_id, task)
            logger.info(f"Cached task {task_id} for future requests")
        
        return task
    
    async def create(self, title: str, description: str = "") -> Task:
        """Create a new task and invalidate cache."""
        task = await self.repository.create(title, description)
        
        # Invalidate cache for all tasks list
        await self._delete_from_cache("all")
        
        return task
    
    async def update(self, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Update a task and invalidate its cache."""
        task = await self.repository.update(task_id, task_update)
        
        if task:
            # Update cache with new task data
            await self._set_to_cache(task_id, task)
            # Also invalidate all tasks list
            await self._delete_from_cache("all")
        
        return task
    
    async def delete(self, task_id: str) -> bool:
        """Delete a task and invalidate its cache."""
        result = await self.repository.delete(task_id)
        
        if result:
            # Invalidate cache
            await self._invalidate_task_cache(task_id)
        
        return result