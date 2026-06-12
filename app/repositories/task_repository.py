from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskUpdate


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Task]:
        result = await self.session.execute(select(Task))
        return result.scalars().all()

    async def get_by_id(self, task_id: str) -> Optional[Task]:
        result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def create(self, title: str, description: str = "") -> Task:
        task = Task(title=title, description=description)

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def update(self, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        task = await self.get_by_id(task_id)
        if not task:
            return None

        data = task_update.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete(self, task_id: str) -> bool:
        result = await self.session.execute(
            delete(Task).where(Task.id == task_id)
        )

        await self.session.commit()
        return result.rowcount > 0