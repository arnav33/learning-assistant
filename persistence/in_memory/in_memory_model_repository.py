# File: /persistence/in_memory/in_memory_model_repository.py
import sqlite3
from typing import List, Optional
from persistence.model_repository import ModelRepository
from persistence.entity.model_entity import ModelEntity

class InMemoryModelRepository(ModelRepository):
    """In-memory SQLite engine implementation satisfying the ModelRepository contract."""

    def __init__(self):
        # check_same_thread=False permits FastAPI async worker pools to run cross-thread queries safely
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_table()
        self.create(ModelEntity(
            id="8f603127-6459-4e34-b1f8-18b28672d77f",
            model="qwen2.5-14b",
            model_provider="ollama",
            thinking_budget=0,
            active=True,
            created_by=None,
            created_time="2026-10-20T18:23:53.715Z",
            last_modified_by=None,
            last_modified_time="2026-10-20T18:23:53.715Z",
        ))

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS model (
                id TEXT PRIMARY KEY,
                model TEXT NOT NULL,
                model_provider TEXT NOT NULL,
                thinking_budget INTEGER NOT NULL,
                active INTEGER NOT NULL,
                created_by TEXT,
                created_time TEXT NOT NULL,
                last_modified_by TEXT,
                last_modified_time TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def create(self, entity: ModelEntity) -> str:
        self.cursor.execute("""
            INSERT INTO model (
                id, model, model_provider, thinking_budget, active, 
                created_by, created_time, last_modified_by, last_modified_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entity.id,
            entity.model,
            entity.model_provider,
            entity.thinking_budget,
            1 if entity.active else 0,  # Map boolean to integer natively
            entity.created_by,
            entity.created_time,
            entity.last_modified_by,
            entity.last_modified_time
        ))
        self.conn.commit()
        return entity.id

    def get_all(self) -> List[ModelEntity]:
        self.cursor.execute("SELECT * FROM model")
        rows = self.cursor.fetchall()
        # Clean tuple mapping happens directly inside your entity module
        return [ModelEntity.from_db_row(row) for row in rows]

    def get_by_id(self, model_id: str) -> Optional[ModelEntity]:
        self.cursor.execute("SELECT * FROM model WHERE id = ?", (model_id,))
        row = self.cursor.fetchone()
        return ModelEntity.from_db_row(row) if row else None

    def update(self, model_id: str, entity: ModelEntity) -> bool:
        self.cursor.execute("""
            UPDATE model 
            SET model = ?, model_provider = ?, thinking_budget = ?, active = ?, 
                last_modified_by = ?, last_modified_time = ?
            WHERE id = ?
        """, (
            entity.model,
            entity.model_provider,
            entity.thinking_budget,
            1 if entity.active else 0,
            entity.last_modified_by,
            entity.last_modified_time,
            model_id
        ))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, model_id: str) -> bool:
        self.cursor.execute("DELETE FROM model WHERE id = ?", (model_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
