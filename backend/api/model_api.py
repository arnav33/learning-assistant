from fastapi import APIRouter

from backend.service.model_service import model_service
from persistence.entity.model_entity import ModelEntity

router = APIRouter()

@router.get("/")
def get_model():
    return model_service.get_all()

@router.get("/{model_id}")
def get_model_by_id(model_id: str):
    return model_service.get_by_id(model_id)

@router.post("/")
def create_model(model: ModelEntity):
    return model_service.create(model)

@router.put("/{model_id}")
def update_model(model_id: str, model: ModelEntity):
    return model_service.update(model_id, model)

@router.delete("/{model_id}")
def delete_model(model_id: str):
    return model_service.delete(model_id)
