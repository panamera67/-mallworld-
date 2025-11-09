import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import googleapiclient.discovery

from storage.mongodb_manager import init_mongo_manager


@dataclass
class YouTubeConfig:
    api_key: str
    max_results: int = 50
    update_interval: int = 3600  # seconds


class YouTubeConnector:
    def __init__(self, config: YouTubeConfig):
        self.config = config
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=config.api_key
        )
        self.logger = logging.getLogger("YouTube-Connector")
        self.videos_collected = 0

    async def initialize(self) -> bool:
        """Test de connexion à l'API YouTube."""
        try:
            request = self.youtube.videos().list(
                part="snippet", chart="mostPopular", regionCode="FR", maxResults=1
            )
            request.execute()
            self.logger.info("✅ Connecteur YouTube initialisé")
            return True
        except Exception as exc:
            self.logger.error("❌ Erreur connexion YouTube: %s", exc)
            return False

    async def fetch_trending_videos(self) -> List[Dict]:
        """Récupération des vidéos tendances."""
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                chart="mostPopular",
                regionCode="FR",
                maxResults=self.config.max_results,
            )
            response = request.execute()

            videos: List[Dict] = []
            for item in response.get("items", []):
                video_data = self._process_video_data(item)
                videos.append(video_data)
                self.videos_collected += 1

            self.logger.info("📹 %s vidéos YouTube collectées", len(videos))
            return videos

        except Exception as exc:
            self.logger.error("❌ Erreur récupération YouTube: %s", exc)
            return []

    def _process_video_data(self, item: Dict) -> Dict:
        """Transformation des données vidéo."""
        snippet = item.get("snippet", {})
        content_details = item.get("contentDetails", {})

        return {
            "video_id": item.get("id"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel_id": snippet.get("channelId"),
            "channel_title": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "statistics": item.get("statistics", {}),
            "tags": snippet.get("tags", []),
            "category_id": snippet.get("categoryId"),
            "duration": content_details.get("duration", ""),
            "collected_at": datetime.utcnow().isoformat(),
            "platform": "youtube",
        }

    async def start_monitoring(self):
        """Démarrage de la surveillance continue."""
        self.logger.info("🔍 Démarrage surveillance YouTube...")
        while True:
            try:
                videos = await self.fetch_trending_videos()

                if videos:
                    mongo_manager = init_mongo_manager()
                    for video in videos:
                        await mongo_manager.store_youtube_video(video)

                await asyncio.sleep(self.config.update_interval)

            except asyncio.CancelledError:
                self.logger.info("🛑 Surveillance YouTube interrompue")
                raise
            except Exception as exc:
                self.logger.error("❌ Erreur monitoring YouTube: %s", exc)
                await asyncio.sleep(300)

    async def close(self):
        """Fermeture propre (placeholder)."""
        self.logger.info("🔌 Connecteur YouTube arrêté")
