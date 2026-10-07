"""Approval repository for human-in-the-loop review operations."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from db.models.approval import Approval
from db.models.enums import ApprovalStatus, RiskLevel
from db.repositories.base import BaseRepository


class ApprovalRepository(BaseRepository[Approval]):
    """Asynchronous repository for human-in-the-loop approval checkpoints."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Approval, session=session)

    async def create_approval(
        self,
        run_id: uuid.UUID,
        action_type: str,
        description: str,
        payload: dict[str, Any],
        evidence_memory_ids: list[str] | None = None,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        task_id: uuid.UUID | None = None,
    ) -> Approval:
        """Create and queue a new approval request."""
        approval = Approval(
            run_id=run_id,
            task_id=task_id,
            action_type=action_type,
            description=description,
            risk_level=risk_level,
            payload=payload,
            evidence_memory_ids=evidence_memory_ids or [],
            status=ApprovalStatus.PENDING,
        )
        return await self.create(approval)

    async def list_pending(self, limit: int = 50) -> Sequence[Approval]:
        """Fetch pending approval requests awaiting human review."""
        stmt = (
            select(Approval)
            .where(col(Approval.status) == ApprovalStatus.PENDING)
            .order_by(col(Approval.requested_at).asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def resolve_approval(
        self,
        approval_id: uuid.UUID,
        status: ApprovalStatus,
        reviewer_notes: str | None = None,
    ) -> Approval | None:
        """Approve or reject a pending approval request."""
        approval = await self.get_by_id(approval_id)
        if approval is None:
            return None

        approval.status = status
        approval.reviewer_notes = reviewer_notes
        approval.resolved_at = datetime.now(UTC)

        await self.session.flush()
        await self.session.refresh(approval)
        return approval

    async def get_by_run(self, run_id: uuid.UUID) -> Sequence[Approval]:
        """Fetch all approvals associated with a specific agent run."""
        stmt = (
            select(Approval)
            .where(col(Approval.run_id) == run_id)
            .order_by(col(Approval.requested_at).desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


__all__ = ["ApprovalRepository"]
