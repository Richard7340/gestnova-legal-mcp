"""Multi-tenant knowledge store backed by PostgreSQL."""
import json
import os
import uuid
from datetime import datetime
from typing import Any, Optional

from gestnova_legal.types import (
    ConsultaContent,
    JurisprudenciaContent,
    NormaContent,
)

CONTENT_VALIDATORS = {
    "consulta": ConsultaContent,
    "norma": NormaContent,
    "jurisprudencia": JurisprudenciaContent,
}


def _get_dsn() -> str:
    return os.environ.get(
        "LEGAL_DATABASE_URL",
        os.environ.get("DATABASE_URL", "postgresql://localhost:5432/gestnova"),
    )


class KnowledgeStore:
    def __init__(self, pool=None):
        self._pool = pool

    async def _get_pool(self):
        if self._pool is None:
            import asyncpg
            self._pool = await asyncpg.create_pool(_get_dsn(), min_size=1, max_size=5)
        return self._pool

    async def save(
        self,
        workspace_id: str,
        content_type: str,
        jurisdiction: str,
        sector: str | None,
        content: dict[str, Any],
    ) -> str:
        validator = CONTENT_VALIDATORS.get(content_type)
        if validator:
            validator(**content)
        entry_id = str(uuid.uuid4())
        pool = await self._get_pool()
        await pool.execute(
            """
            INSERT INTO legal_knowledge (id, "workspaceId", type, jurisdiction, sector, content, "createdAt", "updatedAt")
            VALUES ($1, $2::uuid, $3, $4, $5, $6::jsonb, NOW(), NOW())
            """,
            entry_id, workspace_id, content_type, jurisdiction, sector,
            json.dumps(content, default=str),
        )
        return entry_id

    async def search(
        self,
        workspace_id: str,
        query: str,
        jurisdiction: str | None = None,
        content_type: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        pool = await self._get_pool()
        sql = """
            SELECT id, type, jurisdiction, sector, content, "createdAt",
                   ts_rank(search_vector, plainto_tsquery('spanish', $2)) AS rank
            FROM legal_knowledge
            WHERE "workspaceId" = $1::uuid
              AND search_vector @@ plainto_tsquery('spanish', $2)
        """
        params: list[Any] = [workspace_id, query]
        idx = 3
        if jurisdiction:
            sql += f" AND jurisdiction = ${idx}"
            params.append(jurisdiction)
            idx += 1
        if content_type:
            sql += f" AND type = ${idx}"
            params.append(content_type)
            idx += 1
        sql += f" ORDER BY rank DESC LIMIT ${idx}"
        params.append(limit)
        rows = await pool.fetch(sql, *params)
        return [
            {
                "id": str(r["id"]),
                "type": r["type"],
                "jurisdiction": r["jurisdiction"],
                "sector": r["sector"],
                "content": json.loads(r["content"]) if isinstance(r["content"], str) else r["content"],
                "created_at": r["createdAt"].isoformat(),
                "rank": float(r["rank"]),
            }
            for r in rows
        ]

    async def get_by_workspace(
        self,
        workspace_id: str,
        content_type: str | None = None,
        jurisdiction: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        pool = await self._get_pool()
        sql = 'SELECT id, type, jurisdiction, sector, content, "createdAt" FROM legal_knowledge WHERE "workspaceId" = $1::uuid'
        params: list[Any] = [workspace_id]
        idx = 2
        if content_type:
            sql += f" AND type = ${idx}"
            params.append(content_type)
            idx += 1
        if jurisdiction:
            sql += f" AND jurisdiction = ${idx}"
            params.append(jurisdiction)
            idx += 1
        sql += f' ORDER BY "createdAt" DESC LIMIT ${idx}'
        params.append(limit)
        rows = await pool.fetch(sql, *params)
        return [
            {
                "id": str(r["id"]),
                "type": r["type"],
                "jurisdiction": r["jurisdiction"],
                "sector": r["sector"],
                "content": json.loads(r["content"]) if isinstance(r["content"], str) else r["content"],
                "created_at": r["createdAt"].isoformat(),
            }
            for r in rows
        ]

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
