from fastapi import APIRouter
from persistence.entity.model_entity import ModelEntity
from persistence.repositories import repositories

router = APIRouter()

@router.get("/")
def get_model():
    return [model.to_dict() for model in repositories.models.get_all()]

@router.get("/{model_id}")
def get_model_by_id(model_id: str):
    model = repositories.models.get_by_id(model_id)
    return model.to_dict() if model else None

@router.post("/")
def create_model(model: ModelEntity):
    return repositories.models.create(model)

@router.put("/{model_id}")
def update_model(model_id: str, model: ModelEntity):
    return repositories.models.update(model_id, model)

@router.delete("/{model_id}")
def delete_model(model_id: str):
    return repositories.models.delete(model_id)