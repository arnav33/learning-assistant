import sqlite3
from typing import List, Optional

from persistence.base_repository import BaseRepository
from persistence.entity.agent_entity import AgentEntity


class InMemoryAgentRepository(BaseRepository[AgentEntity]):
    """In-memory SQLite store for agent records."""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_table()
        self.create(AgentEntity(
            id="c3e1a9b4-7d26-4f58-8a10-2e6b9d4c7f81",
            name="local14",
            description="local14",
            model_id="8f603127-6459-4e34-b1f8-18b28672d77f",
            active=True,
            created_by=None,
            created_time="2026-10-20T18:23:53.715Z",
            last_modified_by=None,
            last_modified_time="2026-10-20T18:23:53.715Z",
        ))

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                model_id TEXT NOT NULL,
                active INTEGER NOT NULL,
                created_by TEXT,
                created_time TEXT NOT NULL,
                last_modified_by TEXT,
                last_modified_time TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def create(self, entity: AgentEntity) -> str:
        self.cursor.execute("""
            INSERT INTO agent (
                id, name, description, model_id, active,
                created_by, created_time, last_modified_by, last_modified_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entity.id,
            entity.name,
            entity.description,
            entity.model_id,
            1 if entity.active else 0,
            entity.created_by,
            entity.created_time,
            entity.last_modified_by,
            entity.last_modified_time
        ))
        self.conn.commit()
        return entity.id

    def get_all(self) -> List[AgentEntity]:
        self.cursor.execute("SELECT * FROM agent")
        rows = self.cursor.fetchall()
        return [AgentEntity.from_db_row(row) for row in rows]

    def get_by_id(self, agent_id: str) -> Optional[AgentEntity]:
        self.cursor.execute("SELECT * FROM agent WHERE id = ?", (agent_id,))
        row = self.cursor.fetchone()
        return AgentEntity.from_db_row(row) if row else None

    def update(self, agent_id: str, entity: AgentEntity) -> bool:
        self.cursor.execute("""
            UPDATE agent
            SET name = ?, description = ?, model_id = ?, active = ?,
                last_modified_by = ?, last_modified_time = ?
            WHERE id = ?
        """, (
            entity.name,
            entity.description,
            entity.model_id,
            1 if entity.active else 0,
            entity.last_modified_by,
            entity.last_modified_time,
            agent_id
        ))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, agent_id: str) -> bool:
        self.cursor.execute("DELETE FROM agent WHERE id = ?", (agent_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
