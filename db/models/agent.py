"""AgentRun, AgentEvent, and ToolCall SQLModels for runtime execution and observation."""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship

from db.models.base import TimestampModel, UUIDModel
from db.models.enums import AgentEventType, RunStatus

if TYPE_CHECKING:
    from db.models.approval import Approval
    from db.models.project import Project
    from db.models.task import Task


class AgentRun(UUIDModel, TimestampModel, table=True):
    """Execution instance of an agent or workflow, bridged with LangGraph's checkpointer."""

    __tablename__ = "agent_runs"

    thread_id: str = Field(
        index=True,
        nullable=False,
        description="LangGraph conversation/thread identifier for durable checkpointing",
    )
    checkpoint_id: str | None = Field(
        default=None,
        index=True,
        nullable=True,
        description="Current LangGraph state checkpoint identifier",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="tasks.id",
        index=True,
        nullable=True,
        ondelete="SET NULL",
        description="Optional foreign key referencing the associated task",
    )
    project_id: uuid.UUID = Field(
        foreign_key="projects.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Foreign key referencing the associated project",
    )
    parent_run_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="agent_runs.id",
        index=True,
        nullable=True,
        ondelete="SET NULL",
        description="Optional parent run ID for hierarchical orchestration and agent handoffs",
    )
    agent_name: str = Field(
        index=True,
        nullable=False,
        description="Identifier of the executing agent (orchestrator, research, code, analysis, critic)",
    )
    status: RunStatus = Field(
        default=RunStatus.PENDING,
        index=True,
        nullable=False,
        description="Current execution lifecycle status",
    )
    messages: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
        description="Sequential chat messages array for UI rendering and prompt inspection",
    )
    input_state: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Initial state dictionary passed into the agent run",
    )
    output_result: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Final returned output state or structured conclusion",
    )
    model_name: str | None = Field(
        default=None,
        nullable=True,
        description="LLM model identifier used for this run",
    )
    prompt_tokens: int | None = Field(
        default=None,
        nullable=True,
        description="Total input tokens consumed",
    )
    completion_tokens: int | None = Field(
        default=None,
        nullable=True,
        description="Total output tokens generated",
    )
    total_tokens: int | None = Field(
        default=None,
        nullable=True,
        description="Aggregate token consumption",
    )
    total_cost_usd: float | None = Field(
        default=None,
        nullable=True,
        description="Estimated execution cost in USD",
    )
    error_message: str | None = Field(
        default=None,
        nullable=True,
        description="Diagnostic error string if the run failed",
    )
    started_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Execution initiation timestamp",
    )
    completed_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Execution termination timestamp",
    )

    # Relationships
    project: "Project" = Relationship(back_populates="agent_runs")
    task: Optional["Task"] = Relationship(back_populates="agent_runs")
    parent_run: Optional["AgentRun"] = Relationship(
        back_populates="child_runs",
        sa_relationship_kwargs={"remote_side": "AgentRun.id"},
    )
    child_runs: list["AgentRun"] = Relationship(
        back_populates="parent_run",
    )
    events: list["AgentEvent"] = Relationship(
        back_populates="run",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    tool_calls: list["ToolCall"] = Relationship(
        back_populates="run",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    approvals: list["Approval"] = Relationship(
        back_populates="run",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class AgentEvent(UUIDModel, table=True):
    """Structured observable lifecycle event recorded during agent execution."""

    __tablename__ = "agent_events"

    run_id: uuid.UUID = Field(
        foreign_key="agent_runs.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Foreign key referencing the parent agent run",
    )
    event_type: AgentEventType = Field(
        index=True,
        nullable=False,
        description="Standardized event category enum",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Structured event payload (scores, retrieved IDs, handoff reasons, etc.)",
    )
    sequence_number: int = Field(
        default=0,
        index=True,
        nullable=False,
        description="Strict monotonic sequence counter within the agent run",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        description="UTC timestamp when the event occurred",
    )

    # Relationships
    run: "AgentRun" = Relationship(back_populates="events")


class ToolCall(UUIDModel, table=True):
    """Detailed record of an individual tool invocation by an agent."""

    __tablename__ = "tool_calls"

    run_id: uuid.UUID = Field(
        foreign_key="agent_runs.id",
        index=True,
        nullable=False,
        ondelete="CASCADE",
        description="Foreign key referencing the associated agent run",
    )
    tool_name: str = Field(
        index=True,
        nullable=False,
        description="Name of the invoked tool (e.g. search_memory, git_diff, python_sandbox)",
    )
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Tool input arguments dictionary",
    )
    result: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Structured output returned by the tool",
    )
    error: str | None = Field(
        default=None,
        nullable=True,
        description="Captured tool execution error if failed",
    )
    duration_ms: float | None = Field(
        default=None,
        nullable=True,
        description="Execution wall-clock duration in milliseconds",
    )
    sandboxed: bool = Field(
        default=True,
        nullable=False,
        description="Flag indicating whether tool executed inside the isolated sandbox",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        description="Invocation start timestamp",
    )

    # Relationships
    run: "AgentRun" = Relationship(back_populates="tool_calls")


__all__ = ["AgentEvent", "AgentRun", "ToolCall"]
