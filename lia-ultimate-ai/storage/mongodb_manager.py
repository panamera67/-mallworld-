import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class MongoDBManager:
    def __init__(self, connection_string: str, db_name: str = "lia_ai"):
        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None
        self.logger = logging.getLogger("MongoDB-Manager")
        self.connect()

    def connect(self):
        """Connexion à MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            self.logger.info("✅ Connecté à MongoDB")
        except ConnectionFailure as e:
            self.logger.error(f"❌ Erreur connexion MongoDB: {e}")

    async def is_healthy(self) -> bool:
        """Vérification de la santé de la base"""
        try:
            if self.client:
                self.client.admin.command("ping")
                return True
        except Exception:
            pass
        return False

    async def store_tweet(self, tweet_data: dict) -> bool:
        """Stockage d'un tweet"""
        try:
            if self.db:
                result = self.db.tweets.insert_one(tweet_data)
                self.logger.debug(f"💾 Tweet stocké: {result.inserted_id}")
                return True
        except Exception as e:
            self.logger.error(f"❌ Erreur stockage tweet: {e}")
        return False

    async def close(self):
        """Fermeture de la connexion"""
        if self.client:
            self.client.close()
            self.logger.info("🔌 Connexion MongoDB fermée")
