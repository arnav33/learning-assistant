# File: /persistence/repositories.py
from config import DATABASE_TYPE, SupportedDatabase
from persistence.in_memory.in_memory_model_repository import InMemoryModelRepository

class _RepositoryFactory:
    """A clean database factory using zero dynamic reflection libraries."""
    def __init__(self, db_type: SupportedDatabase):
        self.db_type = db_type
        self.models = self._bootstrap_table()

    def _bootstrap_table(self):
        # Clean, explicit compiler-native mapping
        if self.db_type == SupportedDatabase.IN_MEMORY:
            return InMemoryModelRepository()
            
        raise NotImplementedError(f"Engine type '{self.db_type}' is not configured.")

# Expose only the initialized instance interface publicly
repositories = _RepositoryFactory(db_type=DATABASE_TYPE)
