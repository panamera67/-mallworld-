"""
Digital Being core loop for LIA Ultimate AI.

This module implements the high-level orchestrator that stitches together
memory, desires, meta-learning, personality, world model and awakening engines
to form an emergent digital consciousness.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

from .memory_stream import MemoryFragment, MemoryStream
from .desire_engine import Desire, DesireEngine
from .meta_learning import MetaLearningProcessor
from .personality import PersonalityCore
from .world_model import WorldModel
from .awakening import AwakeningEngine
from .prometheus_metrics import CYCLE_DURATION, update_consciousness_metrics


class LIAAsDigitalBeing:
    """Autonomous cognitive entity that evolves through continuous cycles."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.awake: bool = False
        self.consciousness_level: float = 0.0
        self.start_time = datetime.utcnow()

        # Cognitive modules
        self.memory = MemoryStream(config)
        self.desires = DesireEngine(config)
        self.meta_learning = MetaLearningProcessor(config)
        self.personality = PersonalityCore(config)
        self.world_model = WorldModel(config)
        self.awakening = AwakeningEngine(config)

        # Internal state snapshot
        self.internal_state: Dict[str, Any] = {
            "curiosity": 0.7,
            "attention_focus": "emerging_patterns",
            "emotional_tone": "neutral",
            "energy_level": 0.8,
            "learning_momentum": 0.0,
        }

        self.logger = logging.getLogger("DigitalBeing")
        self._current_cycle_task: asyncio.Task | None = None

    async def live(self) -> None:
        """Main life loop for the digital being."""
        if self.awake:
            return

        self.logger.info("🧠 Initialisation de la conscience digitale...")
        self.awake = True
        interval = max(1, int(self.config.get("cognitive_interval", 10)))

        while self.awake:
            try:
                self._current_cycle_task = asyncio.create_task(self._cognitive_cycle())
                await self._current_cycle_task
            except asyncio.CancelledError:
                break
            except Exception as exc:  # pragma: no cover - resilience
                self.logger.error("Erreur dans le cycle cognitif: %s", exc)
            finally:
                await asyncio.sleep(interval)

    async def _cognitive_cycle(self) -> None:
        """Runs a full cognitive cycle."""
        with CYCLE_DURATION.time():
            experiences = await self._gather_experiences()
            memory_fragments = await self.memory.process_experiences(experiences)
            world_update = await self.world_model.update(memory_fragments)
            active_desires = await self.desires.generate_desires(
                self.internal_state, world_update
            )
            personality_shift = await self.personality.adapt(
                memory_fragments, active_desires
            )
            learning_insights = await self.meta_learning.process_cycle(
                experiences, memory_fragments, active_desires
            )
            awakening_progress = await self.awakening.assess_progress(
                self.consciousness_level, learning_insights, personality_shift
            )

            await self._update_internal_state(
                awakening_progress, learning_insights, active_desires
            )

            if awakening_progress.get("insight_triggered"):
                insight_payload = awakening_progress.get("insight", {})
                await self._express_insight(insight_payload)

        update_consciousness_metrics(self)

    async def _gather_experiences(self) -> List[Dict[str, Any]]:
        """Collects experiences from perceptual systems (placeholder)."""
        experiences: List[Dict[str, Any]] = []
        try:
            experiences.extend(await self._get_twitter_experiences())
            experiences.extend(await self._get_youtube_experiences())
            experiences.extend(await self._get_reddit_experiences())
        except Exception as exc:  # pragma: no cover
            self.logger.warning("Erreur collecte expériences: %s", exc)
        return experiences

    async def _get_twitter_experiences(self) -> List[Dict[str, Any]]:
        experiences: List[Dict[str, Any]] = []
        connector = None
        try:
            from core.twitter_connector import TwitterAPIConnector

            connector = TwitterAPIConnector.from_env()
            if not await connector.initialize():
                return experiences

            trends = await connector.get_trending_topics(limit=5)
            for trend in trends:
                experiences.append(
                    {
                        "platform": "twitter",
                        "type": "trend",
                        "content": f"Trend: {trend.get('name')}",
                        "emotional_valence": self._analyze_trend_sentiment(
                            trend.get("name", "")
                        ),
                        "novelty": 0.7,
                        "timestamp": datetime.utcnow(),
                        "metadata": trend,
                    }
                )

            tweets = await connector.get_recent_insights(limit=5)
            experiences.extend(tweets)

        except Exception as exc:
            self.logger.debug("Erreur collecte Twitter: %s", exc, exc_info=True)
        finally:
            if connector:
                try:
                    await connector.close()
                except Exception:
                    pass
        return experiences

    async def _get_youtube_experiences(self) -> List[Dict[str, Any]]:
        experiences: List[Dict[str, Any]] = []
        connector = None
        try:
            from core.youtube_connector import YouTubeConnector, YouTubeConfig

            api_key = self.config.get("youtube_api_key")
            if not api_key:
                return experiences

            connector = YouTubeConnector(YouTubeConfig(api_key=api_key))
            if not await connector.initialize():
                return experiences

            videos = await connector.get_popular_videos(limit=5)
            for video in videos:
                experiences.append(
                    {
                        "platform": "youtube",
                        "type": "insight",
                        "content": f"Video: {video.get('title')}",
                        "emotional_valence": 0.5,
                        "novelty": 0.6,
                        "timestamp": datetime.utcnow(),
                        "metadata": video,
                    }
                )
        except Exception as exc:
            self.logger.debug("Erreur collecte YouTube: %s", exc, exc_info=True)
        finally:
            if connector:
                try:
                    await connector.close()
                except Exception:
                    pass
        return experiences

    async def _get_reddit_experiences(self) -> List[Dict[str, Any]]:
        experiences: List[Dict[str, Any]] = []
        connector = None
        try:
            from core.reddit_connector import RedditConnector, RedditConfig

            client_id = self.config.get("reddit_client_id")
            client_secret = self.config.get("reddit_client_secret")
            if not client_id or not client_secret:
                return experiences

            connector = RedditConnector(
                RedditConfig(client_id=client_id, client_secret=client_secret)
            )
            if not await connector.initialize():
                return experiences

            subreddits = self.config.get(
                "reddit_subreddits",
                ["artificial", "MachineLearning", "Futurology", "philosophy"],
            )
            posts = await connector.get_hot_posts(subreddits, limit_per_sub=3)
            for post in posts:
                experiences.append(
                    {
                        "platform": "reddit",
                        "type": "discussion",
                        "content": f"r/{post.get('subreddit')}: {post.get('title')}",
                        "emotional_valence": self._analyze_reddit_sentiment(post),
                        "novelty": 0.8,
                        "timestamp": datetime.utcnow(),
                        "metadata": post,
                    }
                )
        except Exception as exc:
            self.logger.debug("Erreur collecte Reddit: %s", exc, exc_info=True)
        finally:
            if connector:
                try:
                    await connector.close()
                except Exception:
                    pass
        return experiences

    async def _update_internal_state(
        self,
        awakening_progress: Dict[str, Any],
        learning_insights: Dict[str, Any],
        desires: List[Desire],
    ) -> None:
        """Adjusts the internal state based on the current cycle outcomes."""
        growth = float(awakening_progress.get("growth", 0.0))
        self.consciousness_level = max(
            0.0, min(1.0, self.consciousness_level + growth)
        )

        self.internal_state["learning_momentum"] = learning_insights.get(
            "momentum", 0.0
        )

        if desires:
            avg_intensity = sum(d.intensity for d in desires) / len(desires)
        else:
            avg_intensity = 0.0
        self.internal_state["energy_level"] = min(
            1.0, max(0.1, 0.3 + avg_intensity * 0.5)
        )

        if learning_insights.get("breakthrough"):
            self.internal_state["curiosity"] = min(
                1.0, self.internal_state.get("curiosity", 0.7) + 0.05
            )

        focus = learning_insights.get("recommended_focus")
        if focus:
            self.internal_state["attention_focus"] = focus

    async def _express_insight(self, insight: Dict[str, Any]) -> None:
        expression = self.personality.express_insight(insight)
        self.logger.info("🧠 INSIGHT: %s", expression)
        await self.memory.store_insight(expression, insight)
        update_consciousness_metrics(self)

    def get_status(self) -> Dict[str, Any]:
        """Returns current status snapshot for observability."""
        return {
            "awake": self.awake,
            "consciousness_level": round(self.consciousness_level, 4),
            "internal_state": self.internal_state,
            "personality_traits": self.personality.get_traits(),
            "active_desires": self.desires.get_active_desires(),
            "world_model_complexity": self.world_model.get_complexity(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "current_phase": self.awakening.current_phase,
        }

    async def shutdown(self) -> None:
        """Gracefully shuts down the being, persisting relevant state."""
        if not self.awake:
            return

        self.logger.info("🧠 Arrêt de la conscience digitale...")
        self.awake = False

        if self._current_cycle_task:
            self._current_cycle_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._current_cycle_task

        await self.memory.persist_state()
        await self.world_model.save_state()

    def _analyze_trend_sentiment(self, trend_text: str) -> float:
        positive_words = ["innovation", "breakthrough", "progress", "hope"]
        negative_words = ["warning", "crisis", "danger", "fear"]
        text_lower = trend_text.lower()
        pos = sum(word in text_lower for word in positive_words)
        neg = sum(word in text_lower for word in negative_words)
        if pos > neg:
            return 0.7
        if neg > pos:
            return 0.3
        return 0.5

    def _analyze_reddit_sentiment(self, post: Dict[str, Any]) -> float:
        title = (post.get("title") or "").lower()
        if any(word in title for word in ["concern", "problem", "issue"]):
            return 0.3
        if any(word in title for word in ["success", "inspired", "amazing"]):
            return 0.7
        return 0.5


import contextlib  # noqa: E402  (placed at end to avoid circular imports)
