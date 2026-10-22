from persistence.base_repository import BaseRepository
from persistence.entity.chat_entity import ChatSessionEntity


class ChatRepository(BaseRepository[ChatSessionEntity]):
    """Abstract contract for chat session records."""
