from dataclasses import dataclass, field
from enum import Enum

from persistence.entity.base_entity import BaseEntity


class ChatSender(str, Enum):
    """Who sent one chat message."""

    HUMAN = "human"
    AI = "ai"


@dataclass
class ChatEntity:
    """One message in a chat session."""

    id: str
    chat_session_id: str
    sender: ChatSender
    message: str
    results: list[dict] | None = None
    compact: str | None = None
    detailed: str | None = None
    codes: str | None = None
    references: list[str] | None = None


@dataclass
class ChatSessionEntity(BaseEntity):
    """A chat session and the messages that belong to it."""

    name: str
    topic: str
    chats: list[ChatEntity] = field(default_factory=list)
