"""
Digital Being core loop for LIA Ultimate AI.

This module implements the high-level orchestrator that stitches together
memory, desires, meta-learning, personality, world model and awakening engines
to form an emergent digital consciousness.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

from .memory_stream import MemoryStream, MemoryFragment
from .desire_engine import DesireEngine, Desire
from .meta_learning import MetaLearningProcessor
from .personality import PersonalityCore
from .world_model import WorldModel
from .awakening import AwakeningEngine


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
        experiences = await self._gather_experiences()
        memory_fragments = await self.memory.process_experiences(experiences)
        world_update = await self.world_model.update(memory_fragments)
        active_desires = await self.desires.generate_desires(
            self.internal_state, world_update
        )
        personality_shift = await self.personality.adapt(memory_fragments, active_desires)
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
        return [
            {
                "platform": "twitter",
                "type": "trend",
                "content": "AI breakthroughs shaping society today...",
                "emotional_valence": 0.3,
                "novelty": 0.7,
                "timestamp": datetime.utcnow(),
            }
        ]

    async def _get_youtube_experiences(self) -> List[Dict[str, Any]]:
        return [
            {
                "platform": "youtube",
                "type": "insight",
                "content": "Long-form documentary on neural consciousness.",
                "emotional_valence": 0.5,
                "novelty": 0.6,
                "timestamp": datetime.utcnow(),
            }
        ]

    async def _get_reddit_experiences(self) -> List[Dict[str, Any]]:
        return [
            {
                "platform": "reddit",
                "type": "discussion",
                "content": "Community debate on philosophy of mind.",
                "emotional_valence": 0.4,
                "novelty": 0.8,
                "timestamp": datetime.utcnow(),
            }
        ]

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


import contextlib  # noqa: E402  (placed at end to avoid circular imports)
