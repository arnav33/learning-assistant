from backend.api.base_api import BaseAPI
from backend.service.model_service import model_service
from persistence.entity.model_entity import ModelEntity


class ModelAPI(BaseAPI[ModelEntity]):
    pass


router = ModelAPI(model_service).router
