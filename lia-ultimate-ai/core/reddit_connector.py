import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncpraw

from storage.mongodb_manager import init_mongo_manager


@dataclass
class RedditConfig:
    client_id: str
    client_secret: str
    user_agent: str = "LIA-Ultimate-AI-Enterprise/1.0"
    update_interval: int = 1800  # seconds
    subreddits: Optional[List[str]] = None


class RedditConnector:
    def __init__(self, config: RedditConfig):
        self.config = config
        self.reddit = asyncpraw.Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent=config.user_agent,
        )
        self.logger = logging.getLogger("Reddit-Connector")
        self.posts_collected = 0

    async def initialize(self) -> bool:
        """Test de connexion à l'API Reddit."""
        try:
            subreddit = await self.reddit.subreddit("all")
            async for _ in subreddit.hot(limit=1):
                break
            self.logger.info("✅ Connecteur Reddit initialisé")
            return True
        except Exception as exc:
            self.logger.error("❌ Erreur connexion Reddit: %s", exc)
            return False

    async def fetch_trending_posts(
        self, subreddits: Optional[List[str]] = None, limit_per_sub: int = 20
    ) -> List[Dict]:
        """Récupération des posts tendances."""
        subreddits = subreddits or self.config.subreddits or [
            "artificial",
            "MachineLearning",
            "technology",
            "programming",
        ]

        collected: List[Dict] = []
        try:
            async with self.reddit:
                for subreddit_name in subreddits:
                    try:
                        subreddit = await self.reddit.subreddit(subreddit_name)
                        async for post in subreddit.hot(limit=limit_per_sub):
                            post_data = await self._process_post_data(post)
                            collected.append(post_data)
                            self.posts_collected += 1
                    except Exception as exc:
                        self.logger.error(
                            "❌ Erreur récupération subreddit %s: %s", subreddit_name, exc
                        )
                        continue

            self.logger.info("📝 %s posts Reddit collectés", len(collected))
            return collected
        except Exception as exc:
            self.logger.error("❌ Erreur récupération Reddit: %s", exc)
            return []

    async def _process_post_data(self, post) -> Dict:
        """Transformation des données post."""
        return {
            "post_id": post.id,
            "title": post.title,
            "content": post.selftext,
            "subreddit": str(post.subreddit),
            "author": str(post.author) if post.author else None,
            "score": post.score,
            "upvote_ratio": post.upvote_ratio,
            "num_comments": post.num_comments,
            "created_utc": datetime.utcfromtimestamp(post.created_utc).isoformat(),
            "url": post.url,
            "permalink": post.permalink,
            "collected_at": datetime.utcnow().isoformat(),
            "platform": "reddit",
        }

    async def start_monitoring(self):
        """Démarrage de la surveillance continue."""
        self.logger.info("🔍 Démarrage surveillance Reddit...")
        while True:
            try:
                posts = await self.fetch_trending_posts()
                if posts:
                    mongo_manager = init_mongo_manager()
                    for post in posts:
                        await mongo_manager.store_reddit_post(post)
                await asyncio.sleep(self.config.update_interval)
            except asyncio.CancelledError:
                self.logger.info("🛑 Surveillance Reddit interrompue")
                raise
            except Exception as exc:
                self.logger.error("❌ Erreur monitoring Reddit: %s", exc)
                await asyncio.sleep(300)

    async def close(self):
        """Fermeture propre du connecteur."""
        await self.reddit.close()
        self.logger.info("🔌 Connecteur Reddit arrêté")

    async def get_hot_posts(
        self, subreddits: List[str], limit_per_sub: int = 3
    ) -> List[Dict]:
        """Retourne les posts populaires simplifiés."""
        return await self.fetch_trending_posts(subreddits=subreddits, limit_per_sub=limit_per_sub)
