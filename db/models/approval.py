"""Approval SQLModel representing human-in-the-loop approval checkpoints."""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship

from db.models.base import UUIDModel
from db.models.enums import ApprovalStatus, RiskLevel

if TYPE_CHECKING:
    from db.models.agent import AgentRun
    from db.models.task import Task


class Approval(UUIDModel, table=True):
    """Human-in-the-loop approval record for sensitive agent operations."""

    __tablename__ = "approvals"

    run_id: uuid.UUID = Field(
        foreign_key="agent_runs.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Foreign key referencing the agent run requesting approval",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="tasks.id",
        index=True,
        nullable=True,
        ondelete="SET NULL",
        description="Optional foreign key referencing the associated task",
    )
    action_type: str = Field(
        index=True,
        nullable=False,
        description="Category of sensitive action (file_modification, git_commit, command_execution)",
    )
    description: str = Field(
        nullable=False,
        description="Human-readable explanation of why this action is proposed",
    )
    risk_level: RiskLevel = Field(
        default=RiskLevel.MEDIUM,
        index=True,
        nullable=False,
        description="Assigned risk tier of the action",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Structured action payload (e.g. proposed file diff, command string, target path)",
    )
    evidence_memory_ids: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
        description="List of memory UUIDs supporting and justifying this requested action",
    )
    status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        index=True,
        nullable=False,
        description="Current state of human review (pending, approved, rejected, timeout)",
    )
    reviewer_notes: str | None = Field(
        default=None,
        nullable=True,
        description="Optional feedback or rejection justification from the reviewer",
    )
    requested_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        description="Timestamp when the approval was requested",
    )
    resolved_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Timestamp when the human approved or rejected the request",
    )

    # Relationships
    run: "AgentRun" = Relationship(back_populates="approvals")
    task: Optional["Task"] = Relationship(back_populates="approvals")


__all__ = ["Approval"]
