"""Task SQLModel representing long-running user-requested goals and research tasks."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship

from db.models.base import TimestampModel, UUIDModel
from db.models.enums import TaskStatus

if TYPE_CHECKING:
    from db.models.agent import AgentRun
    from db.models.approval import Approval
    from db.models.project import Project
    from db.models.user import User


class Task(UUIDModel, TimestampModel, table=True):
    """Task domain model for tracking long-horizon investigations and multi-step executions."""

    __tablename__ = "tasks"

    project_id: uuid.UUID = Field(
        foreign_key="projects.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Foreign key referencing the associated project",
    )
    user_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="users.id",
        index=True,
        nullable=True,
        ondelete="SET NULL",
        description="Optional foreign key referencing the requesting user",
    )
    title: str = Field(
        index=True,
        nullable=False,
        description="Task objective or concise goal title",
    )
    description: str | None = Field(
        default=None,
        nullable=True,
        description="Detailed task description or research inquiry",
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        index=True,
        nullable=False,
        description="Current lifecycle status of the task",
    )
    priority: int = Field(
        default=0,
        index=True,
        nullable=False,
        description="Execution priority order",
    )
    context_data: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Initial task parameters, input criteria, or reference artifacts",
    )
    completed_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Timestamp when the task reached a terminal status",
    )

    # Relationships
    project: "Project" = Relationship(back_populates="tasks")
    user: Optional["User"] = Relationship(back_populates="tasks")
    agent_runs: list["AgentRun"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    approvals: list["Approval"] = Relationship(
        back_populates="task",
    )


__all__ = ["Task"]
