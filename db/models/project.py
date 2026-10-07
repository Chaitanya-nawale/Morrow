"""Project SQLModel representing research and engineering workspaces."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship

from db.models.base import TimestampModel, UUIDModel

if TYPE_CHECKING:
    from db.models.agent import AgentRun
    from db.models.document import Document
    from db.models.memory import Memory
    from db.models.task import Task
    from db.models.user import User


class Project(UUIDModel, TimestampModel, table=True):
    """Project domain entity encapsulating documents, memories, tasks, and agent runs."""

    __tablename__ = "projects"

    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Foreign key referencing the project owner",
    )
    name: str = Field(
        index=True,
        nullable=False,
        description="Project workspace name",
    )
    description: str | None = Field(
        default=None,
        nullable=True,
        description="Optional project description and scope summary",
    )
    settings: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Project-level configuration and environment settings",
    )

    # Relationships
    user: "User" = Relationship(back_populates="projects")
    documents: list["Document"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    memories: list["Memory"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    tasks: list["Task"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    agent_runs: list["AgentRun"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


__all__ = ["Project"]
