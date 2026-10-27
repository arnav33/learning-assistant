from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException

from backend.service.base_service import BaseService
from graph.chat_orchestrator import orchestrate
from persistence.chat_repository import ChatRepository
from persistence.entity.chat_entity import ChatEntity, ChatSender, ChatSessionEntity
from persistence.repositories import repositories


class ChatService(BaseService[ChatSessionEntity]):
    """Business operations for chat sessions."""

    def __init__(self, repository: ChatRepository):
        super().__init__(repository)

    def send(self, query: str, session_id: Optional[str] = None, topic: Optional[str] = None) -> ChatSessionEntity:
        text = query.strip()
        if not text:
            raise HTTPException(status_code=400, detail="A query is required.")

        now = _now()
        if session_id:
            session = self.get_by_id(session_id)
            if session is None:
                raise HTTPException(status_code=404, detail="Chat session not found.")
        else:
            chosen = (topic or "").strip()
            if not chosen:
                raise HTTPException(status_code=400, detail="A topic is required.")
            session = ChatSessionEntity(
                id=str(uuid4()),
                name=_brief_name(text),
                topic=chosen,
                chats=[],
                created_by=None,
                created_time=now,
                last_modified_by=None,
                last_modified_time=now,
            )
            self.create(session)

        session.chats = [
            *session.chats,
            ChatEntity(id=str(uuid4()), chat_session_id=session.id, sender=ChatSender.HUMAN, message=text),
        ]
        session.last_modified_time = now
        self.update(session.id, session)

        compact, answer, references = _reply(text, session.topic)
        if len(session.chats) == 1 and (compact or answer):
            session.name = _brief_name(compact or answer)
        session.chats = [
            *session.chats,
            ChatEntity(
                id=str(uuid4()),
                chat_session_id=session.id,
                sender=ChatSender.AI,
                message=compact or answer or "The reply failed.",
                compact=compact,
                answer=answer,
                references=references,
            ),
        ]
        session.last_modified_time = _now()
        self.update(session.id, session)
        stored = self.get_by_id(session.id)
        return stored if stored is not None else session


def _reply(query: str, topic: str) -> tuple[str | None, str | None, list[str] | None]:
    return orchestrate(query, topic)


def _brief_name(text: str) -> str:
    compact = " ".join(text.split())
    if len(compact) <= 80:
        return compact
    return compact[:77].rstrip() + "..."


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


chat_service = ChatService(repositories.chat)
