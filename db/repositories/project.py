"""Project repository for research workspace operations."""

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from db.models.project import Project
from db.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Asynchronous repository for Project workspaces."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Project, session=session)

    async def create_project(
        self,
        user_id: uuid.UUID,
        name: str,
        description: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Project:
        """Create and persist a new workspace project."""
        project = Project(
            user_id=user_id,
            name=name,
            description=description,
            settings=settings or {},
        )
        return await self.create(project)

    async def get_by_name(self, user_id: uuid.UUID, name: str) -> Project | None:
        """Fetch project by owner user ID and workspace name."""
        stmt = select(Project).where(
            col(Project.user_id) == user_id,
            col(Project.name) == name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> Sequence[Project]:
        """List all projects belonging to a user."""
        stmt = (
            select(Project)
            .where(col(Project.user_id) == user_id)
            .order_by(col(Project.created_at).desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


__all__ = ["ProjectRepository"]
