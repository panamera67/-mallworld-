import logging
import os
from datetime import datetime
from typing import Dict, Optional

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import ConnectionFailure


class MongoDBManager:
    def __init__(self, connection_string: str, db_name: str = "lia_ai"):
        self.connection_string = connection_string
        self.db_name = db_name
        self.client: Optional[MongoClient] = None
        self.db = None
        self.logger = logging.getLogger("MongoDB-Manager")
        self.connect()
        self.setup_indexes()

    def connect(self):
        """Connexion à MongoDB avec gestion d'erreur."""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
            )
            self.db = self.client[self.db_name]
            self.client.admin.command("ping")
            self.logger.info("✅ MongoDB connecté avec succès")
        except ConnectionFailure as exc:
            self.logger.error("❌ Erreur connexion MongoDB: %s", exc)
            raise

    def setup_indexes(self):
        """Configuration des index optimisés."""
        if not self.db:
            return
        try:
            self.db.tweets.create_index([("created_at", DESCENDING)])
            self.db.tweets.create_index([("author_id", ASCENDING)])
            self.db.tweets.create_index([("platform", ASCENDING)])

            self.db.youtube_videos.create_index([("published_at", DESCENDING)])
            self.db.youtube_videos.create_index([("channel_id", ASCENDING)])

            self.db.reddit_posts.create_index([("created_utc", DESCENDING)])
            self.db.reddit_posts.create_index([("subreddit", ASCENDING)])

            self.db.system_metrics.create_index([("timestamp", DESCENDING)])

            self.logger.info("✅ Index MongoDB configurés")
        except Exception as exc:
            self.logger.error("❌ Erreur configuration indexes: %s", exc)

    async def is_healthy(self) -> bool:
        """Vérification approfondie de la santé."""
        try:
            if not self.client:
                return False
            self.client.admin.command("ping")

            expected_collections = {"tweets", "youtube_videos", "reddit_posts"}
            existing = set(self.db.list_collection_names())
            for missing in expected_collections - existing:
                self.logger.warning("⚠️ Collection manquante: %s", missing)

            return True
        except Exception as exc:
            self.logger.error("❌ Santé MongoDB: %s", exc)
            return False

    async def store_tweet(self, tweet_data: Dict) -> bool:
        """Stockage d'un tweet avec validation."""
        try:
            if not self.db:
                return False
            required_fields = ["tweet_id", "text", "created_at"]
            for field in required_fields:
                if field not in tweet_data:
                    self.logger.warning("⚠️ Champ manquant dans tweet: %s", field)
                    return False

            result = self.db.tweets.insert_one(tweet_data)
            self.logger.debug("💾 Tweet stocké: %s", result.inserted_id)
            return True
        except Exception as exc:
            self.logger.error("❌ Erreur stockage tweet: %s", exc)
            return False

    async def store_youtube_video(self, video_data: Dict) -> bool:
        """Stockage d'une vidéo YouTube."""
        try:
            if not self.db:
                return False
            result = self.db.youtube_videos.insert_one(video_data)
            self.logger.debug("💾 Vidéo YouTube stockée: %s", result.inserted_id)
            return True
        except Exception as exc:
            self.logger.error("❌ Erreur stockage YouTube: %s", exc)
            return False

    async def store_reddit_post(self, post_data: Dict) -> bool:
        """Stockage d'un post Reddit."""
        try:
            if not self.db:
                return False
            result = self.db.reddit_posts.insert_one(post_data)
            self.logger.debug("💾 Post Reddit stocké: %s", result.inserted_id)
            return True
        except Exception as exc:
            self.logger.error("❌ Erreur stockage Reddit: %s", exc)
            return False

    async def get_system_metrics(self) -> Dict:
        """Récupération des métriques système."""
        try:
            if not self.db:
                return {}
            tweet_count = self.db.tweets.count_documents({})
            youtube_count = self.db.youtube_videos.count_documents({})
            reddit_count = self.db.reddit_posts.count_documents({})

            latest_tweet = self.db.tweets.find_one({}, sort=[("collected_at", DESCENDING)])

            return {
                "tweets_collected": tweet_count,
                "youtube_videos": youtube_count,
                "reddit_posts": reddit_count,
                "last_update": latest_tweet.get("collected_at") if latest_tweet else None,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as exc:
            self.logger.error("❌ Erreur récupération métriques: %s", exc)
            return {}

    async def close(self):
        """Fermeture propre."""
        if self.client:
            self.client.close()
            self.logger.info("🔌 Connexion MongoDB fermée")


mongo_manager: Optional[MongoDBManager] = None


def init_mongo_manager(connection_string: Optional[str] = None, db_name: str = "lia_ai") -> MongoDBManager:
    """Initialise (ou retourne) l'instance globale de MongoDBManager."""
    global mongo_manager
    if mongo_manager is None:
        conn = connection_string or os.getenv("MONGODB_URI", "mongodb://localhost:27017/lia_ai")
        mongo_manager = MongoDBManager(conn, db_name=db_name)
    return mongo_manager
