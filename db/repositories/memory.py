"""Memory repository implementing CRUD, graph linking, archiving, and semantic search."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Literal, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from db.models.enums import MemoryLinkType, MemoryType
from db.models.memory import Memory, MemoryLink
from db.repositories.base import BaseRepository


class MemoryRepository(BaseRepository[Memory]):
    """Asynchronous repository for Memory entities, link relationships, and vector search."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Memory, session=session)

    async def create_memory(
        self,
        project_id: uuid.UUID,
        type: MemoryType,
        content: str,
        source: str,
        importance: float = 0.5,
        confidence: float = 1.0,
        embedding: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
        document_id: uuid.UUID | None = None,
    ) -> Memory:
        """Create and persist a new Memory record."""
        memory = Memory(
            project_id=project_id,
            document_id=document_id,
            type=type,
            content=content,
            source=source,
            importance=importance,
            confidence=confidence,
            embedding=embedding,
            metadata_=metadata or {},
        )
        return await self.create(memory)

    async def get_memory(
        self,
        memory_id: uuid.UUID,
        include_archived: bool = False,
        update_last_accessed: bool = False,
    ) -> Memory | None:
        """Retrieve a memory by ID with optional archival filtering and recency timestamp update."""
        stmt = select(Memory).where(col(Memory.id) == memory_id)
        if not include_archived:
            stmt = stmt.where(col(Memory.is_archived).is_(False))

        result = await self.session.execute(stmt)
        memory = result.scalar_one_or_none()

        if memory is not None and update_last_accessed:
            memory.last_accessed_at = datetime.now(UTC)
            await self.session.flush()

        return memory

    async def update_memory(
        self,
        memory_id: uuid.UUID,
        **updates: Any,
    ) -> Memory | None:
        """Update fields of an existing memory."""
        memory = await self.get_by_id(memory_id)
        if memory is None:
            return None

        for field, value in updates.items():
            if field == "metadata":
                memory.metadata_ = value
            elif hasattr(memory, field):
                setattr(memory, field, value)

        memory.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(memory)
        return memory

    async def archive_memory(self, memory_id: uuid.UUID) -> bool:
        """Soft-delete a memory by setting is_archived to True."""
        memory = await self.get_by_id(memory_id)
        if memory is None:
            return False

        memory.is_archived = True
        memory.updated_at = datetime.now(UTC)
        await self.session.flush()
        return True

    async def unarchive_memory(self, memory_id: uuid.UUID) -> bool:
        """Restore an archived memory by setting is_archived to False."""
        memory = await self.get_by_id(memory_id)
        if memory is None:
            return False

        memory.is_archived = False
        memory.updated_at = datetime.now(UTC)
        await self.session.flush()
        return True

    async def delete_memory(self, memory_id: uuid.UUID) -> bool:
        """Hard delete a memory from the database."""
        memory = await self.get_by_id(memory_id)
        if memory is None:
            return False

        await self.delete(memory)
        return True

    async def link_memories(
        self,
        source_memory_id: uuid.UUID,
        target_memory_id: uuid.UUID,
        link_type: MemoryLinkType,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryLink:
        """Create a directed evidence/consolidation link between two memories."""
        link = MemoryLink(
            source_memory_id=source_memory_id,
            target_memory_id=target_memory_id,
            link_type=link_type,
            weight=weight,
            metadata_=metadata or {},
        )
        self.session.add(link)
        await self.session.flush()
        await self.session.refresh(link)
        return link

    async def get_memory_links(
        self,
        memory_id: uuid.UUID,
        direction: Literal["outgoing", "incoming", "both"] = "both",
    ) -> Sequence[MemoryLink]:
        """Fetch links for a memory based on edge direction."""
        stmt = select(MemoryLink)
        if direction == "outgoing":
            stmt = stmt.where(col(MemoryLink.source_memory_id) == memory_id)
        elif direction == "incoming":
            stmt = stmt.where(col(MemoryLink.target_memory_id) == memory_id)
        else:
            stmt = stmt.where(
                (col(MemoryLink.source_memory_id) == memory_id)
                | (col(MemoryLink.target_memory_id) == memory_id)
            )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_memory_link(self, link_id: uuid.UUID) -> bool:
        """Remove a memory link by ID."""
        stmt = select(MemoryLink).where(col(MemoryLink.id) == link_id)
        result = await self.session.execute(stmt)
        link = result.scalar_one_or_none()
        if link is None:
            return False

        await self.session.delete(link)
        await self.session.flush()
        return True

    async def list_memories(
        self,
        project_id: uuid.UUID,
        memory_type: MemoryType | None = None,
        include_archived: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Memory]:
        """List project memories with type and archival filters."""
        stmt = select(Memory).where(col(Memory.project_id) == project_id)
        if not include_archived:
            stmt = stmt.where(col(Memory.is_archived).is_(False))
        if memory_type is not None:
            stmt = stmt.where(col(Memory.type) == memory_type)

        stmt = stmt.order_by(col(Memory.created_at).desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_similar(
        self,
        project_id: uuid.UUID,
        query_embedding: list[float],
        top_k: int = 10,
        memory_type: MemoryType | None = None,
        include_archived: bool = False,
    ) -> list[tuple[Memory, float]]:
        """Perform semantic similarity search using pgvector cosine distance.

        Returns pairs of (Memory, similarity_score) where similarity is in [-1, 1].
        """
        distance_col = (
            cast(Any, Memory.embedding).cosine_distance(query_embedding).label("distance")
        )
        stmt = (
            select(Memory, distance_col)
            .where(col(Memory.project_id) == project_id)
            .where(col(Memory.embedding).is_not(None))
        )

        if not include_archived:
            stmt = stmt.where(col(Memory.is_archived).is_(False))
        if memory_type is not None:
            stmt = stmt.where(col(Memory.type) == memory_type)

        stmt = stmt.order_by("distance").limit(top_k)
        result = await self.session.execute(stmt)
        rows = result.all()

        # Convert cosine distance to cosine similarity: similarity = 1 - distance
        return [(row[0], 1.0 - float(row[1])) for row in rows]


__all__ = ["MemoryRepository"]
