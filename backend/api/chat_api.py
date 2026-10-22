from pydantic import BaseModel

from backend.api.base_api import BaseAPI
from backend.service.chat_service import chat_service
from persistence.entity.chat_entity import ChatSessionEntity


class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None
    topic: str | None = None


class ChatAPI(BaseAPI[ChatSessionEntity]):
    def register_extra(self) -> None:
        @self.router.post("/chat")
        def chat(request: ChatRequest) -> ChatSessionEntity:
            return chat_service.send(request.query, request.session_id, request.topic)


router = ChatAPI(chat_service).router
