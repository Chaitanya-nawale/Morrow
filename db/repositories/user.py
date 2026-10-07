"""User repository for managing workspace users and agent personas."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from db.models.user import User
from db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Asynchronous repository for User entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=User, session=session)

    async def get_by_username(self, username: str) -> User | None:
        """Fetch user by unique username."""
        stmt = select(User).where(col(User.username) == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        username: str = "default",
        full_name: str = "Default User",
        persona: str = "Rigorous, evidence-oriented research and engineering assistant.",
    ) -> User:
        """Get existing user or create a new user profile."""
        user = await self.get_by_username(username)
        if user is not None:
            return user

        user = User(
            username=username,
            full_name=full_name,
            persona=persona,
        )
        return await self.create(user)

    async def update_persona(self, username: str, persona: str) -> User | None:
        """Update persona and system instructions for a user."""
        user = await self.get_by_username(username)
        if user is None:
            return None

        user.persona = persona
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list_active_users(self) -> Sequence[User]:
        """List all active workspace users."""
        stmt = select(User).where(col(User.is_active).is_(True))
        result = await self.session.execute(stmt)
        return result.scalars().all()


__all__ = ["UserRepository"]
