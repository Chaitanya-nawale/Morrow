"""Integration tests for MemoryRepository, linking, pgvector search, and workflow state."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.enums import (
    AgentEventType,
    ApprovalStatus,
    MemoryLinkType,
    MemoryType,
    RiskLevel,
    RunStatus,
)
from db.repositories.agent import AgentRunRepository
from db.repositories.approval import ApprovalRepository
from db.repositories.document import DocumentRepository
from db.repositories.memory import MemoryRepository
from db.repositories.project import ProjectRepository
from db.repositories.task import TaskRepository
from db.repositories.user import UserRepository


@pytest.mark.asyncio
async def test_user_and_project_repository(db_session: AsyncSession) -> None:
    """Test user creation with persona and project workspace binding."""
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)

    user = await user_repo.get_or_create(
        username=f"researcher_{uuid.uuid4().hex[:6]}",
        full_name="Alice Researcher",
        persona="Act as a meticulous ML engineer.",
    )
    assert user.id is not None
    assert user.persona == "Act as a meticulous ML engineer."

    project = await project_repo.create_project(
        user_id=user.id,
        name="Long-Horizon Agent Memory",
        description="Testing persistent memory architectures",
    )
    assert project.id is not None
    assert project.user_id == user.id

    fetched = await project_repo.get_by_name(user.id, "Long-Horizon Agent Memory")
    assert fetched is not None
    assert fetched.id == project.id


@pytest.mark.asyncio
async def test_memory_crud_and_archival(db_session: AsyncSession) -> None:
    """Deliverable: create, retrieve, update, delete/archive memory."""
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)
    doc_repo = DocumentRepository(db_session)
    mem_repo = MemoryRepository(db_session)

    user = await user_repo.get_or_create(username=f"user_{uuid.uuid4().hex[:6]}")
    project = await project_repo.create_project(user_id=user.id, name="Project Alpha")

    # Ingest source document
    doc = await doc_repo.create_document(
        project_id=project.id,
        uri="experiments/exp42.md",
        title="Experiment 42 Documentation",
        content_hash="hash42abc",
        content="Experiment 42 details and benchmark metrics.",
    )

    # 1. Create memory
    memory = await mem_repo.create_memory(
        project_id=project.id,
        document_id=doc.id,
        type=MemoryType.DECISION,
        content="XGBoost was chosen over Random Forest due to latency constraints.",
        source="experiment_42",
        importance=0.85,
        confidence=0.95,
        metadata={"metric": "f1", "value": 0.86},
    )
    assert memory.id is not None
    assert memory.is_archived is False
    assert memory.document_id == doc.id

    # 2. Retrieve memory
    retrieved = await mem_repo.get_memory(memory.id, update_last_accessed=True)
    assert retrieved is not None
    assert retrieved.content == memory.content
    assert retrieved.last_accessed_at is not None

    # 3. Update memory
    updated = await mem_repo.update_memory(
        memory.id,
        importance=0.95,
        metadata={"metric": "f1", "value": 0.88, "status": "verified"},
    )
    assert updated is not None
    assert updated.importance == 0.95
    assert updated.metadata_["status"] == "verified"

    # 4. Archive memory (soft-delete)
    archived_success = await mem_repo.archive_memory(memory.id)
    assert archived_success is True

    # Check that normal retrieval excludes archived
    assert await mem_repo.get_memory(memory.id, include_archived=False) is None
    # Check that retrieval with include_archived returns it
    archived_mem = await mem_repo.get_memory(memory.id, include_archived=True)
    assert archived_mem is not None
    assert archived_mem.is_archived is True

    # 5. Unarchive memory
    unarchive_success = await mem_repo.unarchive_memory(memory.id)
    assert unarchive_success is True
    assert await mem_repo.get_memory(memory.id, include_archived=False) is not None

    # 6. Hard delete memory
    deleted = await mem_repo.delete_memory(memory.id)
    assert deleted is True
    assert await mem_repo.get_memory(memory.id, include_archived=True) is None


@pytest.mark.asyncio
async def test_memory_linking(db_session: AsyncSession) -> None:
    """Deliverable: link memories and retrieve relationship graphs."""
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)
    mem_repo = MemoryRepository(db_session)

    user = await user_repo.get_or_create(username=f"user_{uuid.uuid4().hex[:6]}")
    project = await project_repo.create_project(user_id=user.id, name="Project Graph")

    # Create source evidence and consolidated decision memories
    evidence_mem = await mem_repo.create_memory(
        project_id=project.id,
        type=MemoryType.EVIDENCE,
        content="Benchmark run 42 reached 0.86 F1.",
        source="benchmark_run_42",
    )
    decision_mem = await mem_repo.create_memory(
        project_id=project.id,
        type=MemoryType.DECISION,
        content="XGBoost was deployed in production.",
        source="architecture_review",
    )

    # Link: evidence SUPPORTS decision
    link = await mem_repo.link_memories(
        source_memory_id=evidence_mem.id,
        target_memory_id=decision_mem.id,
        link_type=MemoryLinkType.SUPPORTS,
        weight=0.9,
        metadata={"rationale": "Direct benchmark proof"},
    )
    assert link.id is not None
    assert link.link_type == MemoryLinkType.SUPPORTS

    # Query outgoing links from evidence
    outgoing = await mem_repo.get_memory_links(evidence_mem.id, direction="outgoing")
    assert len(outgoing) == 1
    assert outgoing[0].target_memory_id == decision_mem.id

    # Query incoming links to decision
    incoming = await mem_repo.get_memory_links(decision_mem.id, direction="incoming")
    assert len(incoming) == 1
    assert incoming[0].source_memory_id == evidence_mem.id

    # Delete link
    assert await mem_repo.delete_memory_link(link.id) is True
    assert len(await mem_repo.get_memory_links(evidence_mem.id)) == 0


@pytest.mark.asyncio
async def test_pgvector_similarity_search(db_session: AsyncSession) -> None:
    """Test semantic similarity retrieval using pgvector cosine distance."""
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)
    mem_repo = MemoryRepository(db_session)

    user = await user_repo.get_or_create(username=f"user_{uuid.uuid4().hex[:6]}")
    project = await project_repo.create_project(user_id=user.id, name="Vector Project")

    # Create synthetic vectors of dimension 1536
    # Vector A: highly aligned with [1, 0, 0, ...]
    vec_a = [0.0] * 1536
    vec_a[0] = 1.0

    # Vector B: orthogonal / distant from [1, 0, 0, ...]
    vec_b = [0.0] * 1536
    vec_b[1] = 1.0

    mem_a = await mem_repo.create_memory(
        project_id=project.id,
        type=MemoryType.SEMANTIC,
        content="Gradient boosted decision trees explanation.",
        source="ml_handbook",
        embedding=vec_a,
    )
    mem_b = await mem_repo.create_memory(
        project_id=project.id,
        type=MemoryType.SEMANTIC,
        content="Convolutional neural network pooling layers.",
        source="cv_paper",
        embedding=vec_b,
    )

    # Query with vector close to A
    query_vec = [0.0] * 1536
    query_vec[0] = 0.99
    query_vec[1] = 0.01

    results = await mem_repo.search_similar(
        project_id=project.id,
        query_embedding=query_vec,
        top_k=2,
    )
    assert len(results) == 2
    # mem_a should rank first with high cosine similarity
    top_memory, top_similarity = results[0]
    assert top_memory.id == mem_a.id
    assert top_similarity > 0.9  # Nearly 1.0 cosine similarity

    second_memory, second_similarity = results[1]
    assert second_memory.id == mem_b.id
    assert top_similarity > second_similarity


@pytest.mark.asyncio
async def test_agent_run_and_approval_workflow(db_session: AsyncSession) -> None:
    """Test AgentRun, messages array, monotonic events, tool calls, and approvals."""
    user_repo = UserRepository(db_session)
    project_repo = ProjectRepository(db_session)
    task_repo = TaskRepository(db_session)
    agent_repo = AgentRunRepository(db_session)
    approval_repo = ApprovalRepository(db_session)

    user = await user_repo.get_or_create(username=f"user_{uuid.uuid4().hex[:6]}")
    project = await project_repo.create_project(user_id=user.id, name="Agent Workflow")
    task = await task_repo.create_task(project_id=project.id, title="Refactor Experiment Pipeline")

    # Create run with LangGraph thread_id
    run = await agent_repo.create_run(
        project_id=project.id,
        thread_id="thread_langgraph_42",
        agent_name="orchestrator",
        task_id=task.id,
        messages=[{"role": "user", "content": "Please inspect experiments."}],
    )
    assert run.status == RunStatus.RUNNING
    assert len(run.messages) == 1

    # Add message
    await agent_repo.add_message(run.id, {"role": "assistant", "content": "Inspecting repository..."})
    refetched_run = await agent_repo.get_by_id(run.id)
    assert refetched_run is not None
    assert len(refetched_run.messages) == 2

    # Add observable events with monotonic sequence numbers
    e1 = await agent_repo.add_event(run.id, AgentEventType.RUN_STARTED, {"start": True})
    e2 = await agent_repo.add_event(run.id, AgentEventType.MEMORY_SEARCH_STARTED, {"query": "exp"})
    assert e1.sequence_number == 1
    assert e2.sequence_number == 2

    events = await agent_repo.get_events(run.id)
    assert len(events) == 2
    assert events[0].event_type == AgentEventType.RUN_STARTED

    # Add sandboxed tool call
    tool_call = await agent_repo.add_tool_call(
        run_id=run.id,
        tool_name="git_diff",
        arguments={"path": "thesis/results.md"},
        result={"diff": "+ XGBoost: 0.86"},
        duration_ms=45.2,
        sandboxed=True,
    )
    assert tool_call.sandboxed is True
    tool_calls = await agent_repo.get_tool_calls(run.id)
    assert len(tool_calls) == 1

    # Human-in-the-loop approval checkpoint
    approval = await approval_repo.create_approval(
        run_id=run.id,
        task_id=task.id,
        action_type="file_modification",
        description="Write experiment 42 results to thesis/results.md",
        payload={"file": "thesis/results.md", "diff": "+ XGBoost: 0.86"},
        risk_level=RiskLevel.MEDIUM,
    )
    assert approval.status == ApprovalStatus.PENDING

    pending = await approval_repo.list_pending()
    assert any(a.id == approval.id for a in pending)

    # Resolve approval
    resolved = await approval_repo.resolve_approval(
        approval.id,
        status=ApprovalStatus.APPROVED,
        reviewer_notes="Results verified against logs.",
    )
    assert resolved is not None
    assert resolved.status == ApprovalStatus.APPROVED
    assert resolved.resolved_at is not None

    # Complete run
    completed_run = await agent_repo.update_status(
        run.id,
        status=RunStatus.COMPLETED,
        output_result={"status": "completed_successfully"},
        total_tokens=450,
        checkpoint_id="chk_step_final",
    )
    assert completed_run is not None
    assert completed_run.status == RunStatus.COMPLETED
    assert completed_run.completed_at is not None
    assert completed_run.checkpoint_id == "chk_step_final"
