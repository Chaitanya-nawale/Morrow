"""Unit tests for SQLModel definitions, enums, and default factories."""

import uuid

from db.models.agent import AgentEvent, AgentRun, ToolCall
from db.models.approval import Approval
from db.models.document import Document
from db.models.enums import (
    AgentEventType,
    ApprovalStatus,
    MemoryLinkType,
    MemoryType,
    RiskLevel,
    RunStatus,
    TaskStatus,
)
from db.models.memory import Memory, MemoryLink
from db.models.project import Project
from db.models.task import Task
from db.models.user import User


def test_user_model_defaults() -> None:
    """Validate User model defaults including single-string persona."""
    user = User(username="chaituz", full_name="Chaitanya")
    assert isinstance(user.id, uuid.UUID)
    assert user.username == "chaituz"
    assert user.full_name == "Chaitanya"
    assert "research" in user.persona.lower()
    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None


def test_project_model_creation() -> None:
    """Validate Project model creation and settings JSON default."""
    user_id = uuid.uuid4()
    project = Project(user_id=user_id, name="Morrow-Thesis", description="Persistent Memory")
    assert project.user_id == user_id
    assert project.name == "Morrow-Thesis"
    assert project.settings == {}


def test_document_model_creation() -> None:
    """Validate Document model supporting URI, hash, and optional text content."""
    project_id = uuid.uuid4()
    doc = Document(
        project_id=project_id,
        uri="notes/thesis.md",
        title="Thesis Notes",
        content_hash="abc123sha256",
        content="# Thesis Architecture",
        size_bytes=1024,
    )
    assert doc.project_id == project_id
    assert doc.uri == "notes/thesis.md"
    assert doc.content == "# Thesis Architecture"
    assert doc.metadata_ == {}


def test_memory_model_and_link() -> None:
    """Validate Memory and MemoryLink model defaults and attributes."""
    project_id = uuid.uuid4()
    mem1 = Memory(
        project_id=project_id,
        type=MemoryType.DECISION,
        content="Selected XGBoost due to F1 performance.",
        source="experiment_42",
        importance=0.9,
        confidence=0.95,
        embedding=[0.1] * 1536,
    )
    assert mem1.type == MemoryType.DECISION
    assert mem1.is_archived is False
    assert mem1.embedding is not None and len(mem1.embedding) == 1536

    mem2 = Memory(
        project_id=project_id,
        type=MemoryType.EVIDENCE,
        content="Experiment 42 achieved F1 = 0.86.",
        source="run_logs",
    )

    link = MemoryLink(
        source_memory_id=mem1.id,
        target_memory_id=mem2.id,
        link_type=MemoryLinkType.SUPPORTS,
        weight=1.0,
    )
    assert link.link_type == MemoryLinkType.SUPPORTS
    assert link.source_memory_id == mem1.id
    assert link.target_memory_id == mem2.id


def test_task_model() -> None:
    """Validate Task model defaults."""
    project_id = uuid.uuid4()
    task = Task(project_id=project_id, title="Investigate performance degradation")
    assert task.status == TaskStatus.PENDING
    assert task.priority == 0
    assert task.completed_at is None


def test_agent_run_and_events() -> None:
    """Validate AgentRun with thread_id, messages list, and observable events."""
    project_id = uuid.uuid4()
    run = AgentRun(
        project_id=project_id,
        thread_id="thread_abc_123",
        agent_name="orchestrator",
        messages=[{"role": "user", "content": "Analyze experiment 42"}],
    )
    assert run.thread_id == "thread_abc_123"
    assert run.checkpoint_id is None
    assert run.status == RunStatus.PENDING
    assert len(run.messages) == 1

    event = AgentEvent(
        run_id=run.id,
        event_type=AgentEventType.RUN_STARTED,
        payload={"agent": "orchestrator"},
        sequence_number=1,
    )
    assert event.event_type == AgentEventType.RUN_STARTED
    assert event.sequence_number == 1

    tool_call = ToolCall(
        run_id=run.id,
        tool_name="search_memory",
        arguments={"query": "XGBoost experiment"},
        sandboxed=True,
    )
    assert tool_call.tool_name == "search_memory"
    assert tool_call.sandboxed is True


def test_approval_model() -> None:
    """Validate Approval checkpoint model."""
    run_id = uuid.uuid4()
    approval = Approval(
        run_id=run_id,
        action_type="file_modification",
        description="Update thesis/results.md with experiment 42 metrics",
        risk_level=RiskLevel.MEDIUM,
        payload={"target_file": "thesis/results.md", "diff": "+ F1: 0.86"},
        evidence_memory_ids=["mem-1", "mem-2"],
    )
    assert approval.status == ApprovalStatus.PENDING
    assert approval.risk_level == RiskLevel.MEDIUM
    assert len(approval.evidence_memory_ids) == 2
