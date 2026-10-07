"""Agent repository for managing agent runs, lifecycle events, and tool calls."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from db.models.agent import AgentEvent, AgentRun, ToolCall
from db.models.enums import AgentEventType, RunStatus
from db.repositories.base import BaseRepository


class AgentRunRepository(BaseRepository[AgentRun]):
    """Asynchronous repository for AgentRun records, event logs, and tool executions."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=AgentRun, session=session)

    async def create_run(
        self,
        project_id: uuid.UUID,
        thread_id: str,
        agent_name: str,
        task_id: uuid.UUID | None = None,
        parent_run_id: uuid.UUID | None = None,
        input_state: dict[str, Any] | None = None,
        messages: list[dict[str, Any]] | None = None,
        model_name: str | None = None,
        checkpoint_id: str | None = None,
    ) -> AgentRun:
        """Create and start a new agent run."""
        run = AgentRun(
            project_id=project_id,
            thread_id=thread_id,
            agent_name=agent_name,
            task_id=task_id,
            parent_run_id=parent_run_id,
            input_state=input_state or {},
            messages=messages or [],
            model_name=model_name,
            checkpoint_id=checkpoint_id,
            status=RunStatus.RUNNING,
            started_at=datetime.now(UTC),
        )
        return await self.create(run)

    async def get_by_thread_id(self, thread_id: str) -> Sequence[AgentRun]:
        """Fetch all agent runs sharing a LangGraph thread ID."""
        stmt = (
            select(AgentRun)
            .where(col(AgentRun.thread_id) == thread_id)
            .order_by(col(AgentRun.created_at).asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status(
        self,
        run_id: uuid.UUID,
        status: RunStatus,
        output_result: dict[str, Any] | None = None,
        error_message: str | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        total_tokens: int | None = None,
        total_cost_usd: float | None = None,
        checkpoint_id: str | None = None,
    ) -> AgentRun | None:
        """Update run status, token metrics, and completion state."""
        run = await self.get_by_id(run_id)
        if run is None:
            return None

        run.status = status
        run.updated_at = datetime.now(UTC)

        if checkpoint_id is not None:
            run.checkpoint_id = checkpoint_id
        if output_result is not None:
            run.output_result = output_result
        if error_message is not None:
            run.error_message = error_message
        if prompt_tokens is not None:
            run.prompt_tokens = prompt_tokens
        if completion_tokens is not None:
            run.completion_tokens = completion_tokens
        if total_tokens is not None:
            run.total_tokens = total_tokens
        if total_cost_usd is not None:
            run.total_cost_usd = total_cost_usd

        if status in (RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED):
            run.completed_at = datetime.now(UTC)

        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def add_message(self, run_id: uuid.UUID, message: dict[str, Any]) -> AgentRun | None:
        """Append a conversational message to the agent run message history."""
        run = await self.get_by_id(run_id)
        if run is None:
            return None

        updated_messages = list(run.messages)
        updated_messages.append(message)
        run.messages = updated_messages
        run.updated_at = datetime.now(UTC)

        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def add_event(
        self,
        run_id: uuid.UUID,
        event_type: AgentEventType,
        payload: dict[str, Any] | None = None,
    ) -> AgentEvent:
        """Emit and record a structured observable agent lifecycle event."""
        stmt = (
            select(col(AgentEvent.sequence_number))
            .where(col(AgentEvent.run_id) == run_id)
            .order_by(col(AgentEvent.sequence_number).desc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        latest_seq = res.scalar_one_or_none()
        next_seq = (latest_seq + 1) if latest_seq is not None else 1

        event = AgentEvent(
            run_id=run_id,
            event_type=event_type,
            payload=payload or {},
            sequence_number=next_seq,
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_events(self, run_id: uuid.UUID) -> Sequence[AgentEvent]:
        """Fetch all events for an agent run in sequential order."""
        stmt = (
            select(AgentEvent)
            .where(col(AgentEvent.run_id) == run_id)
            .order_by(col(AgentEvent.sequence_number).asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_tool_call(
        self,
        run_id: uuid.UUID,
        tool_name: str,
        arguments: dict[str, Any],
        result: dict[str, Any] | None = None,
        error: str | None = None,
        duration_ms: float | None = None,
        sandboxed: bool = True,
    ) -> ToolCall:
        """Record an individual tool call executed by the agent."""
        tool_call = ToolCall(
            run_id=run_id,
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            error=error,
            duration_ms=duration_ms,
            sandboxed=sandboxed,
        )
        self.session.add(tool_call)
        await self.session.flush()
        await self.session.refresh(tool_call)
        return tool_call

    async def get_tool_calls(self, run_id: uuid.UUID) -> Sequence[ToolCall]:
        """Fetch all tool calls executed within an agent run."""
        stmt = (
            select(ToolCall)
            .where(col(ToolCall.run_id) == run_id)
            .order_by(col(ToolCall.created_at).asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


__all__ = ["AgentRunRepository"]
