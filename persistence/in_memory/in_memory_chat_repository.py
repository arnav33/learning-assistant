import json
import sqlite3
from typing import List, Optional

from persistence.chat_repository import ChatRepository
from persistence.entity.chat_entity import ChatEntity, ChatSender, ChatSessionEntity


class InMemoryChatRepository(ChatRepository):
    """In-memory SQLite store for chat sessions and their messages."""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_session (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                topic TEXT NOT NULL,
                created_by TEXT,
                created_time TEXT NOT NULL,
                last_modified_by TEXT,
                last_modified_time TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat (
                id TEXT PRIMARY KEY,
                chat_session_id TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                results TEXT,
                compact TEXT,
                answer TEXT,
                "references" TEXT,
                FOREIGN KEY (chat_session_id) REFERENCES chat_session(id)
            )
        """)
        self.conn.commit()

    def create(self, entity: ChatSessionEntity) -> str:
        self.cursor.execute("""
            INSERT INTO chat_session (
                id, name, topic, created_by, created_time, last_modified_by, last_modified_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entity.id,
            entity.name,
            entity.topic,
            entity.created_by,
            entity.created_time,
            entity.last_modified_by,
            entity.last_modified_time,
        ))
        self._insert_chats(entity)
        self.conn.commit()
        return entity.id

    def get_all(self) -> List[ChatSessionEntity]:
        self.cursor.execute("SELECT * FROM chat_session")
        rows = self.cursor.fetchall()
        return [self._to_session(row) for row in rows]

    def get_by_id(self, entity_id: str) -> Optional[ChatSessionEntity]:
        self.cursor.execute("SELECT * FROM chat_session WHERE id = ?", (entity_id,))
        row = self.cursor.fetchone()
        return self._to_session(row) if row else None

    def update(self, entity_id: str, entity: ChatSessionEntity) -> bool:
        self.cursor.execute("SELECT topic FROM chat_session WHERE id = ?", (entity_id,))
        stored = self.cursor.fetchone()
        if stored is None:
            return False
        self.cursor.execute("""
            UPDATE chat_session
            SET name = ?, topic = ?, last_modified_by = ?, last_modified_time = ?
            WHERE id = ?
        """, (
            entity.name,
            stored["topic"],
            entity.last_modified_by,
            entity.last_modified_time,
            entity_id,
        ))
        changed = self.cursor.rowcount > 0
        if changed:
            self.cursor.execute("DELETE FROM chat WHERE chat_session_id = ?", (entity_id,))
            self._insert_chats(entity)
        self.conn.commit()
        return changed

    def delete(self, entity_id: str) -> bool:
        self.cursor.execute("DELETE FROM chat WHERE chat_session_id = ?", (entity_id,))
        self.cursor.execute("DELETE FROM chat_session WHERE id = ?", (entity_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def _insert_chats(self, entity: ChatSessionEntity) -> None:
        for chat in entity.chats:
            sender = chat.sender.value if isinstance(chat.sender, ChatSender) else chat.sender
            self.cursor.execute("""
                INSERT INTO chat (id, chat_session_id, sender, message, results, compact, answer, "references")
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chat.id,
                entity.id,
                sender,
                chat.message,
                json.dumps(chat.results) if chat.results is not None else None,
                chat.compact,
                chat.answer,
                json.dumps(chat.references) if chat.references is not None else None,
            ))

    def _to_session(self, row: sqlite3.Row) -> ChatSessionEntity:
        self.cursor.execute(
            "SELECT * FROM chat WHERE chat_session_id = ? ORDER BY rowid",
            (row["id"],),
        )
        chats = [self._to_chat(chat_row) for chat_row in self.cursor.fetchall()]
        return ChatSessionEntity(
            id=row["id"],
            name=row["name"],
            topic=row["topic"],
            chats=chats,
            created_by=row["created_by"],
            created_time=row["created_time"],
            last_modified_by=row["last_modified_by"],
            last_modified_time=row["last_modified_time"],
        )

    def _to_chat(self, row: sqlite3.Row) -> ChatEntity:
        stored = row["results"]
        references = row["references"]
        return ChatEntity(
            id=row["id"],
            chat_session_id=row["chat_session_id"],
            sender=ChatSender(row["sender"]),
            message=row["message"],
            results=json.loads(stored) if stored else None,
            compact=row["compact"],
            answer=row["answer"],
            references=json.loads(references) if references else None,
        )
