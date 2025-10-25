from pymongo import MongoClient
from backend.config import get_settings


class Database:
    client = None
    db = None

    @staticmethod
    def connect():
        settings = get_settings()
        Database.client = MongoClient(settings.mongodb_uri)
        Database.db = Database.client[settings.database_name]

    @staticmethod
    def disconnect():
        if Database.client:
            Database.client.close()

    @staticmethod
    def get_db():
        return Database.db
