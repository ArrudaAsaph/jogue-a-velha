"""
MongoDB connection manager
"""
from pymongo import MongoClient
from django.conf import settings


class MongoDB:
    """Singleton para gerenciar conexão com MongoDB"""
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            mongo_settings = settings.MONGODB_SETTINGS
            self._client = MongoClient(
                host=mongo_settings['HOST'],
                port=mongo_settings['PORT']
            )
            self._db = self._client[mongo_settings['DB_NAME']]

    @property
    def db(self):
        """Retorna o database"""
        return self._db

    @property
    def rooms(self):
        """Retorna a collection de salas"""
        return self._db.rooms


# Instância global
mongodb = MongoDB()
