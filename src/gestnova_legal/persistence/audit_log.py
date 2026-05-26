"""Audit log for legal consultations — compliance trail."""
import json
import os
import uuid
from typing import Any, Optional


def _get_dsn() -> str:
    return os.environ.get(
        "LEGAL_DATABASE_URL",
        os.environ.get("DATABASE_URL", "postgresql://localhost:5432/gestnova"),
    )


class AuditLog:
    def __init__(self, pool=None):
        self._pool = pool

    async def _get_pool(self):
        if self._pool is None:
            import asyncpg
            self._pool = await asyncpg.create_pool(_get_dsn(), min_size=1, max_size=3)
        return self._pool

    async def log(
        self,
        workspace_id: str,
        tool_name: str,
        input_args: dict[str, Any],
        output_summary: dict[str, Any] | None = None,
        confianza: str | None = None,
    ) -> str:
        entry_id = str(uuid.uuid4())
        pool = await self._get_pool()
        await pool.execute(
            """
            INSERT INTO legal_audit_log (id, "workspaceId", "toolName", "inputArgs", "outputSummary", confianza, "createdAt")
            VALUES ($1, $2::uuid, $3, $4::jsonb, $5::jsonb, $6, NOW())
            """,
            entry_id, workspace_id, tool_name,
            json.dumps(input_args, default=str),
            json.dumps(output_summary, default=str) if output_summary else None,
            confianza,
        )
        return entry_id

    async def get_recent(self, workspace_id: str, limit: int = 20) -> list[dict[str, Any]]:
        pool = await self._get_pool()
        rows = await pool.fetch(
            """
            SELECT id, "toolName", "inputArgs", "outputSummary", confianza, "createdAt"
            FROM legal_audit_log WHERE "workspaceId" = $1::uuid
            ORDER BY "createdAt" DESC LIMIT $2
            """,
            workspace_id, limit,
        )
        return [
            {
                "id": str(r["id"]),
                "tool_name": r["toolName"],
                "input_args": json.loads(r["inputArgs"]) if isinstance(r["inputArgs"], str) else r["inputArgs"],
                "confianza": r["confianza"],
                "created_at": r["createdAt"].isoformat(),
            }
            for r in rows
        ]

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
