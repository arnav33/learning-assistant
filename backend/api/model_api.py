from backend.api.base_api import BaseAPI
from backend.service.model_service import model_service
from persistence.entity.model_entity import ModelEntity


class ModelAPI(BaseAPI[ModelEntity]):
    def register_extra(self) -> None:
        @self.router.get("/by-name/{name}")
        def get_by_name(name: str):
            return model_service.get_by_name(name)


router = ModelAPI(model_service).router
