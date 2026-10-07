"""Memory and MemoryLink SQLModels representing persistent agentic memory and evidence graphs."""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Column, Text, UniqueConstraint
from sqlmodel import Field, Relationship

from db.models.base import TimestampModel, UUIDModel
from db.models.enums import MemoryLinkType, MemoryType

if TYPE_CHECKING:
    from db.models.document import Document
    from db.models.project import Project


class Memory(UUIDModel, TimestampModel, table=True):
    """Core memory entity supporting semantic, episodic, procedural, decision, and evidence items."""

    __tablename__ = "memories"

    project_id: uuid.UUID = Field(
        foreign_key="projects.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Foreign key referencing the associated project workspace",
    )
    document_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="documents.id",
        index=True,
        nullable=True,
        ondelete="SET NULL",
        description="Optional foreign key linking memory to its source document",
    )
    type: MemoryType = Field(
        index=True,
        nullable=False,
        description="Classification category of the memory",
    )
    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Primary textual content or claim of the memory",
    )
    source: str = Field(
        index=True,
        nullable=False,
        description="Source identifier (commit hash, experiment ID, file URI, or user input)",
    )
    importance: float = Field(
        default=0.5,
        index=True,
        nullable=False,
        description="Calculated or assigned importance weight between 0.0 and 1.0",
    )
    confidence: float = Field(
        default=1.0,
        nullable=False,
        description="Reliability and evidence support confidence score between 0.0 and 1.0",
    )
    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(1536), nullable=True),
        description="Dense vector embedding (1536-dim standard) for semantic retrieval",
    )
    metadata_: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSON, nullable=False),
        description="Structured context such as decision rationale, metrics, tags, or experiment params",
    )
    is_archived: bool = Field(
        default=False,
        index=True,
        nullable=False,
        description="Soft-delete or archival flag for memory pruning",
    )
    last_accessed_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Timestamp of most recent retrieval for recency scoring",
    )

    # Relationships
    project: "Project" = Relationship(back_populates="memories")
    document: Optional["Document"] = Relationship(back_populates="memories")
    outgoing_links: list["MemoryLink"] = Relationship(
        back_populates="source_memory",
        sa_relationship_kwargs={
            "foreign_keys": "[MemoryLink.source_memory_id]",
            "cascade": "all, delete-orphan",
        },
    )
    incoming_links: list["MemoryLink"] = Relationship(
        back_populates="target_memory",
        sa_relationship_kwargs={
            "foreign_keys": "[MemoryLink.target_memory_id]",
            "cascade": "all, delete-orphan",
        },
    )


class MemoryLink(UUIDModel, table=True):
    """Directed relational link connecting two memories (evidence graph / consolidation links)."""

    __tablename__ = "memory_links"

    source_memory_id: uuid.UUID = Field(
        foreign_key="memories.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Origin memory of the relationship",
    )
    target_memory_id: uuid.UUID = Field(
        foreign_key="memories.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Destination memory of the relationship",
    )
    link_type: MemoryLinkType = Field(
        index=True,
        nullable=False,
        description="Relationship semantics (supports, derived_from, contradicts, consolidates, relates_to)",
    )
    weight: float = Field(
        default=1.0,
        nullable=False,
        description="Strength or relevance weight of the relationship",
    )
    metadata_: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSON, nullable=False),
        description="Arbitrary relation metadata or justification notes",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        description="Timestamp when the link was created",
    )

    # Relationships
    source_memory: "Memory" = Relationship(
        back_populates="outgoing_links",
        sa_relationship_kwargs={"foreign_keys": "[MemoryLink.source_memory_id]"},
    )
    target_memory: "Memory" = Relationship(
        back_populates="incoming_links",
        sa_relationship_kwargs={"foreign_keys": "[MemoryLink.target_memory_id]"},
    )

    __table_args__ = (
        UniqueConstraint(
            "source_memory_id",
            "target_memory_id",
            "link_type",
            name="uq_memory_links_source_target_type",
        ),
    )


__all__ = ["Memory", "MemoryLink"]
