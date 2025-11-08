import asyncio
import logging
from datetime import datetime
from typing import Dict

import googleapiclient.discovery


class YouTubeConnector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=api_key
        )
        self.logger = logging.getLogger(__name__)

    async def monitor_trending(self):
        """Surveillance des vidéos tendances"""
        while True:
            try:
                request = self.youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    chart="mostPopular",
                    regionCode="FR",
                    maxResults=50,
                )
                response = request.execute()

                for item in response.get("items", []):
                    video_data = self._process_video(item)
                    await self._store_video_data(video_data)

                self.logger.info(
                    f"📹 {len(response.get('items', []))} vidéos YouTube collectées"
                )
                await asyncio.sleep(3600)

            except Exception as e:
                self.logger.error(f"Erreur YouTube: {e}")
                await asyncio.sleep(300)

    def _process_video(self, item: Dict) -> Dict:
        """Traitement des données vidéo"""
        return {
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "channel_id": item["snippet"]["channelId"],
            "published_at": item["snippet"]["publishedAt"],
            "statistics": item.get("statistics", {}),
            "tags": item["snippet"].get("tags", []),
            "category_id": item["snippet"]["categoryId"],
            "collected_at": datetime.utcnow().isoformat(),
            "platform": "youtube",
        }

    async def _store_video_data(self, video_data: Dict):
        """Placeholder de stockage (à relier au pipeline)"""
        self.logger.debug(f"Video collectée: {video_data['video_id']}")
