# File: /persistence/repositories.py
from config import DATABASE_TYPE, SupportedDatabase
from persistence.in_memory.in_memory_agent_repository import InMemoryAgentRepository
from persistence.in_memory.in_memory_model_repository import InMemoryModelRepository

class _RepositoryFactory:
    """A clean database factory using zero dynamic reflection libraries."""
    def __init__(self, db_type: SupportedDatabase):
        self.db_type = db_type
        self.entity = self._bootstrap_model()
        self.agent = self._bootstrap_agent()

    def _bootstrap_model(self):
        if self.db_type == SupportedDatabase.IN_MEMORY:
            return InMemoryModelRepository()
        raise NotImplementedError(f"Engine type '{self.db_type}' is not configured.")

    def _bootstrap_agent(self):
        if self.db_type == SupportedDatabase.IN_MEMORY:
            return InMemoryAgentRepository()
        raise NotImplementedError(f"Engine type '{self.db_type}' is not configured.")

# Expose only the initialized instance interface publicly
repositories = _RepositoryFactory(db_type=DATABASE_TYPE)
