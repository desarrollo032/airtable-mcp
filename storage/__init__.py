"""
Storage factory for MCP server
"""
from config import settings
from storage.redis_storage import RedisStorage
from storage.mongo_storage import MongoStorage
from storage.memory_storage import MemoryStorage


def get_storage():
    """Fábrica para obtener el sistema de almacenamiento configurado"""
    if settings.STORAGE_BACKEND == "redis":
        return RedisStorage()
    elif settings.STORAGE_BACKEND == "mongo":
        return MongoStorage()
    else:  # memory (default)
        return MemoryStorage()
