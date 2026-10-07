"""Domain enumerations for Morrow database models and agent runtimes."""

from enum import StrEnum


class MemoryType(StrEnum):
    """Classification of persistent memories in Morrow."""

    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    DECISION = "decision"
    EVIDENCE = "evidence"


class MemoryLinkType(StrEnum):
    """Types of relational links connecting memories."""

    SUPPORTS = "supports"
    DERIVED_FROM = "derived_from"
    CONTRADICTS = "contradicts"
    CONSOLIDATES = "consolidates"
    RELATES_TO = "relates_to"


class TaskStatus(StrEnum):
    """Lifecycle status of long-horizon tasks."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunStatus(StrEnum):
    """Execution status for agent runs and subagent handoffs."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED_APPROVAL = "paused_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentEventType(StrEnum):
    """Structured observable lifecycle events emitted during agent runs."""

    RUN_STARTED = "RunStarted"
    AGENT_STARTED = "AgentStarted"
    AGENT_COMPLETED = "AgentCompleted"
    MEMORY_SEARCH_STARTED = "MemorySearchStarted"
    MEMORY_RETRIEVED = "MemoryRetrieved"
    TOOL_CALL_STARTED = "ToolCallStarted"
    TOOL_CALL_COMPLETED = "ToolCallCompleted"
    AGENT_HANDOFF = "AgentHandoff"
    APPROVAL_REQUESTED = "ApprovalRequested"
    APPROVAL_GRANTED = "ApprovalGranted"
    APPROVAL_REJECTED = "ApprovalRejected"
    WORKFLOW_CHECKPOINTED = "WorkflowCheckpointed"
    WORKFLOW_RESUMED = "WorkflowResumed"
    RUN_COMPLETED = "RunCompleted"
    RUN_FAILED = "RunFailed"


class RiskLevel(StrEnum):
    """Risk tier for proposed agent operations requiring human approval."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(StrEnum):
    """Resolution state for human-in-the-loop approval requests."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


__all__ = [
    "AgentEventType",
    "ApprovalStatus",
    "MemoryLinkType",
    "MemoryType",
    "RiskLevel",
    "RunStatus",
    "TaskStatus",
]
