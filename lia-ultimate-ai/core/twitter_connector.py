import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

import tweepy


@dataclass
class TwitterConfig:
    bearer_token: str
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str
    max_requests_per_15min: int = 300

    @classmethod
    def from_env(cls) -> "TwitterConfig":
        """Construit la configuration à partir des variables d'environnement."""
        required = {
            "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN"),
            "TWITTER_CONSUMER_KEY": os.getenv("TWITTER_CONSUMER_KEY"),
            "TWITTER_CONSUMER_SECRET": os.getenv("TWITTER_CONSUMER_SECRET"),
            "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
            "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise EnvironmentError(
                f"Variables d'environnement Twitter manquantes: {', '.join(missing)}"
            )
        return cls(
            bearer_token=required["TWITTER_BEARER_TOKEN"],
            consumer_key=required["TWITTER_CONSUMER_KEY"],
            consumer_secret=required["TWITTER_CONSUMER_SECRET"],
            access_token=required["TWITTER_ACCESS_TOKEN"],
            access_token_secret=required["TWITTER_ACCESS_TOKEN_SECRET"],
        )


class TwitterAPIConnector:
    def __init__(self, config: Optional[TwitterConfig] = None):
        self.config = config or TwitterConfig.from_env()
        self.client: Optional[tweepy.Client] = None
        self.stream: Optional[tweepy.StreamingClient] = None
        self.logger = logging.getLogger("Twitter-Connector")
        self.tweets_collected = 0
        self._initialize_client()

    @classmethod
    def from_env(cls) -> "TwitterAPIConnector":
        return cls(TwitterConfig.from_env())

    def _initialize_client(self):
        """Initialisation du client Twitter."""
        try:
            self.client = tweepy.Client(
                bearer_token=self.config.bearer_token,
                consumer_key=self.config.consumer_key,
                consumer_secret=self.config.consumer_secret,
                access_token=self.config.access_token,
                access_token_secret=self.config.access_token_secret,
                wait_on_rate_limit=True,
            )
            self.logger.info("✅ Client Twitter initialisé")
        except Exception as exc:
            self.logger.error("❌ Erreur initialisation client Twitter: %s", exc)
            self.client = None

    async def initialize(self) -> bool:
        """Test de connexion à l'API Twitter."""
        if not self.client:
            self.logger.error("Client Twitter non initialisé")
            return False
        try:
            me = self.client.get_me()
            if me and me.data:
                self.logger.info("✅ Connecté à Twitter: @%s", me.data.username)
                return True
        except Exception as exc:
            self.logger.error("❌ Erreur connexion Twitter: %s", exc)
        return False

    async def start_stream(self):
        """Démarrage du stream temps réel."""
        if not self.client:
            raise RuntimeError("Client Twitter non initialisé")

        self.logger.info("🔌 Démarrage du stream Twitter...")

        class TweetStream(tweepy.StreamingClient):
            def __init__(self, bearer_token, processor):
                super().__init__(bearer_token, wait_on_rate_limit=True)
                self.processor = processor

            def on_tweet(self, tweet):
                asyncio.create_task(self.processor.process_tweet(tweet))

            def on_errors(self, errors):
                self.processor.logger.error("Erreurs stream: %s", errors)

        try:
            self.stream = TweetStream(self.config.bearer_token, self)

            rules = [
                "IA OR intelligence artificielle OR AI -is:retweet",
                "technologie OR tech OR innovation -is:retweet",
                "philosophie OR pensée OR réflexion -is:retweet",
            ]

            existing_rules = self.stream.get_rules()
            if existing_rules.data:
                rule_ids = [rule.id for rule in existing_rules.data]
                self.stream.delete_rules(rule_ids)

            for rule in rules:
                self.stream.add_rules(tweepy.StreamRule(rule))

            self.stream.filter(
                tweet_fields=[
                    "author_id",
                    "created_at",
                    "public_metrics",
                    "context_annotations",
                ],
                expansions=["author_id"],
                user_fields=["username", "name"],
            )

        except Exception as exc:
            self.logger.error("❌ Erreur démarrage stream: %s", exc)

    async def process_tweet(self, tweet):
        """Traitement d'un tweet reçu."""
        try:
            processed_tweet = {
                "tweet_id": str(tweet.id),
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat()
                if getattr(tweet, "created_at", None)
                else None,
                "author_id": getattr(tweet, "author_id", None),
                "metrics": {
                    "retweets": tweet.public_metrics.get("retweet_count", 0),
                    "likes": tweet.public_metrics.get("like_count", 0),
                    "replies": tweet.public_metrics.get("reply_count", 0),
                }
                if getattr(tweet, "public_metrics", None)
                else {},
                "collected_at": datetime.utcnow().isoformat(),
                "platform": "twitter",
            }

            self.tweets_collected += 1
            self.logger.info("📥 Tweet #%s reçu", self.tweets_collected)

            await self._save_tweet_local(processed_tweet)

        except Exception as exc:
            self.logger.error("❌ Erreur traitement tweet: %s", exc)

    async def _save_tweet_local(self, tweet_data: Dict):
        """Sauvegarde locale des tweets (temporaire)."""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/tweets_collected.jsonl", "a", encoding="utf-8") as handle:
                handle.write(json.dumps(tweet_data, ensure_ascii=False) + "\n")
        except Exception as exc:
            self.logger.error("❌ Erreur sauvegarde locale: %s", exc)

    async def close(self):
        """Fermeture propre des connexions."""
        if self.stream:
            self.stream.disconnect()
        self.logger.info("🔌 Connexions Twitter fermées")
