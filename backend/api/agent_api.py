from backend.api.base_api import BaseAPI
from backend.service.agent_service import agent_service
from persistence.entity.agent_entity import AgentEntity


class AgentAPI(BaseAPI[AgentEntity]):
    def register_extra(self) -> None:
        @self.router.get("/by-name/{name}")
        def get_by_name(name: str):
            return agent_service.get_by_name(name)


router = AgentAPI(agent_service).router
