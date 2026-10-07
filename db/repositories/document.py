"""Document repository for ingested research papers, code files, and notes."""

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from db.models.document import Document
from db.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Asynchronous repository for Document entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Document, session=session)

    async def create_document(
        self,
        project_id: uuid.UUID,
        uri: str,
        title: str,
        content_hash: str,
        content: str | None = None,
        mime_type: str = "text/plain",
        size_bytes: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        """Create and store a newly ingested document record."""
        document = Document(
            project_id=project_id,
            uri=uri,
            title=title,
            content_hash=content_hash,
            content=content,
            mime_type=mime_type,
            size_bytes=size_bytes,
            metadata_=metadata or {},
        )
        return await self.create(document)

    async def get_by_hash(self, project_id: uuid.UUID, content_hash: str) -> Document | None:
        """Find a document in a project by its SHA-256 hash (deduplication/drift check)."""
        stmt = select(Document).where(
            col(Document.project_id) == project_id,
            col(Document.content_hash) == content_hash,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_uri(self, project_id: uuid.UUID, uri: str) -> Document | None:
        """Find a document in a project by its source URI."""
        stmt = select(Document).where(
            col(Document.project_id) == project_id,
            col(Document.uri) == uri,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Document]:
        """List documents belonging to a project."""
        stmt = (
            select(Document)
            .where(col(Document.project_id) == project_id)
            .order_by(col(Document.created_at).desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


__all__ = ["DocumentRepository"]
