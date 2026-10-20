from typing import Generic, Type, TypeVar, get_args, get_origin

from fastapi import APIRouter

from backend.service.base_service import BaseService
from persistence.entity.base_entity import BaseEntity

EntityT = TypeVar("EntityT", bound=BaseEntity)


class BaseAPI(Generic[EntityT]):
    """CRUD routes shared by every entity API."""

    def __init__(self, service: BaseService[EntityT]):
        self.service = service
        self.router = APIRouter()
        self._register(self._entity_type())
        self.register_extra()

    def register_extra(self) -> None:
        """Domain routes that are not shared CRUD."""

    def _entity_type(self) -> Type[EntityT]:
        for base in getattr(type(self), "__orig_bases__", ()):
            if get_origin(base) is BaseAPI:
                entity_type = get_args(base)[0]
                if isinstance(entity_type, type):
                    return entity_type
        raise TypeError(f"{type(self).__name__} must extend BaseAPI[SomeEntity]")

    def _register(self, entity_type: Type[EntityT]) -> None:
        service = self.service

        @self.router.get("/")
        def get_all():
            return service.get_all()

        @self.router.get("/{entity_id}")
        def get_by_id(entity_id: str):
            return service.get_by_id(entity_id)

        @self.router.post("/")
        def create(entity: entity_type):
            return service.create(entity)

        @self.router.put("/{entity_id}")
        def update(entity_id: str, entity: entity_type):
            return service.update(entity_id, entity)

        @self.router.delete("/{entity_id}")
        def delete(entity_id: str):
            return service.delete(entity_id)
