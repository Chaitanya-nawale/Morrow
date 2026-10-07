"""Task repository for long-horizon task coordination."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from db.models.enums import TaskStatus
from db.models.task import Task
from db.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Asynchronous repository for Task entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Task, session=session)

    async def create_task(
        self,
        project_id: uuid.UUID,
        title: str,
        description: str | None = None,
        user_id: uuid.UUID | None = None,
        priority: int = 0,
        context_data: dict[str, Any] | None = None,
    ) -> Task:
        """Create and persist a new task."""
        task = Task(
            project_id=project_id,
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            context_data=context_data or {},
        )
        return await self.create(task)

    async def update_status(self, task_id: uuid.UUID, status: TaskStatus) -> Task | None:
        """Update task status with automatic completion timestamp if terminal."""
        task = await self.get_by_id(task_id)
        if task is None:
            return None

        task.status = status
        task.updated_at = datetime.now(UTC)
        if status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            task.completed_at = datetime.now(UTC)

        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def list_by_project(
        self,
        project_id: uuid.UUID,
        status: TaskStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Task]:
        """List tasks for a project with optional status filtering."""
        stmt = select(Task).where(col(Task.project_id) == project_id)
        if status is not None:
            stmt = stmt.where(col(Task.status) == status)

        stmt = (
            stmt.order_by(col(Task.priority).desc(), col(Task.created_at).desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


__all__ = ["TaskRepository"]
