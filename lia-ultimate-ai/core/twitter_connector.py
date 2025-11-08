import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

import tweepy


@dataclass
class TwitterConfig:
    bearer_token: str
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str
    max_requests_per_15min: int = 300


class TwitterAPIConnector:
    def __init__(self, config: TwitterConfig):
        self.config = config
        self.client = None
        self.stream = None
        self.logger = logging.getLogger("Twitter-Connector")
        self.tweets_collected = 0
        self.initialize_client()

    def initialize_client(self):
        """Initialisation du client Twitter"""
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
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation client Twitter: {e}")

    async def initialize(self):
        """Test de connexion à l'API Twitter"""
        try:
            if self.client:
                me = self.client.get_me()
                self.logger.info(f"✅ Connecté à Twitter: @{me.data.username}")
                return True
        except Exception as e:
            self.logger.error(f"❌ Erreur connexion Twitter: {e}")
        return False

    async def start_stream(self):
        """Démarrage du stream temps réel"""
        self.logger.info("🔌 Démarrage du stream Twitter...")

        class TweetStream(tweepy.StreamingClient):
            def __init__(self, bearer_token, processor):
                super().__init__(bearer_token)
                self.processor = processor

            def on_tweet(self, tweet):
                asyncio.create_task(self.processor.process_tweet(tweet))

            def on_errors(self, errors):
                self.processor.logger.error(f"Erreurs stream: {errors}")

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

        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage stream: {e}")

    async def process_tweet(self, tweet):
        """Traitement d'un tweet reçu"""
        try:
            processed_tweet = {
                "tweet_id": str(tweet.id),
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat()
                if tweet.created_at
                else None,
                "author_id": tweet.author_id,
                "metrics": {
                    "retweets": tweet.public_metrics.get("retweet_count", 0),
                    "likes": tweet.public_metrics.get("like_count", 0),
                    "replies": tweet.public_metrics.get("reply_count", 0),
                },
                "collected_at": datetime.utcnow().isoformat(),
                "platform": "twitter",
            }

            self.tweets_collected += 1
            self.logger.info(f"📥 Tweet #{self.tweets_collected}: {tweet.text[:50]}...")

            await self._save_tweet_local(processed_tweet)

        except Exception as e:
            self.logger.error(f"❌ Erreur traitement tweet: {e}")

    async def _save_tweet_local(self, tweet_data: Dict):
        """Sauvegarde locale des tweets (temporaire)"""
        try:
            with open("data/tweets_collected.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(tweet_data, ensure_ascii=False) + "\n")
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde locale: {e}")

    async def close(self):
        """Fermeture propre des connexions"""
        if self.stream:
            self.stream.disconnect()
        self.logger.info("🔌 Connexions Twitter fermées")
