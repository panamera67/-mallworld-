"""
MemoryStream - Flux de mémoire continue avec associations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId


class MemoryFragment:
    """Fragment individuel de mémoire."""

    def __init__(self, experience: Dict[str, Any], importance: float = 0.5):
        self.id = ObjectId()
        self.content = experience.get("content", "")
        self.type = experience.get("type", "unknown")
        self.timestamp = experience.get("timestamp", datetime.utcnow())
        self.importance = importance
        self.emotional_valence = experience.get("emotional_valence", 0.0)
        self.associations: List[Dict[str, Any]] = []
        self.retrieval_strength = 1.0
        self.last_accessed = datetime.utcnow()

    def add_association(self, other_fragment: MemoryFragment, strength: float) -> None:
        self.associations.append(
            {
                "target_id": other_fragment.id,
                "strength": strength,
                "created": datetime.utcnow(),
            }
        )


class MemoryStream:
    """Flux de mémoire continu avec réseau associatif."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fragments: Dict[ObjectId, MemoryFragment] = {}
        self.timeline: List[ObjectId] = []
        self.importance_threshold = config.get("importance_threshold", 0.3)
        self.association_threshold = config.get("association_threshold", 0.6)

    async def process_experiences(
        self, experiences: List[Dict[str, Any]]
    ) -> List[MemoryFragment]:
        new_fragments: List[MemoryFragment] = []
        for experience in experiences:
            importance = self._calculate_importance(experience)
            if importance < self.importance_threshold:
                continue

            fragment = MemoryFragment(experience, importance)
            self.fragments[fragment.id] = fragment
            self.timeline.append(fragment.id)
            new_fragments.append(fragment)

            await self._create_associations(fragment)
            self._clean_old_memories()
        return new_fragments

    def _calculate_importance(self, experience: Dict[str, Any]) -> float:
        novelty = experience.get("novelty", 0.5)
        emotional_intensity = abs(experience.get("emotional_valence", 0.0))
        surprise = 1.0 - self._predictability_score(experience)
        base = 0.5
        importance = (base + novelty + emotional_intensity + surprise) / 4
        return max(0.0, min(1.0, importance))

    def _predictability_score(self, experience: Dict[str, Any]) -> float:
        return 0.5

    async def _create_associations(self, new_fragment: MemoryFragment) -> None:
        for fragment_id, existing in list(self.fragments.items()):
            if fragment_id == new_fragment.id:
                continue
            strength = self._calculate_association_strength(new_fragment, existing)
            if strength > self.association_threshold:
                new_fragment.add_association(existing, strength)
                existing.add_association(new_fragment, strength)

    def _calculate_association_strength(
        self, frag1: MemoryFragment, frag2: MemoryFragment
    ) -> float:
        semantic_similarity = self._semantic_similarity(frag1.content, frag2.content)
        time_diff = abs((frag1.timestamp - frag2.timestamp).total_seconds())
        temporal_proximity = 1.0 / (1.0 + time_diff / 3600.0)
        emotional_similarity = 1.0 - abs(
            frag1.emotional_valence - frag2.emotional_valence
        )
        return max(
            0.0,
            min(
                1.0,
                (semantic_similarity + temporal_proximity + emotional_similarity) / 3,
            ),
        )

    def _semantic_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union else 0.0

    async def retrieve_associated(
        self, fragment_id: ObjectId, max_results: int = 5
    ) -> List[MemoryFragment]:
        fragment = self.fragments.get(fragment_id)
        if not fragment:
            return []
        fragment.last_accessed = datetime.utcnow()
        fragment.retrieval_strength += 0.1
        associations = sorted(
            fragment.associations, key=lambda a: a["strength"], reverse=True
        )[:max_results]
        return [
            self.fragments[a["target_id"]]
            for a in associations
            if a["target_id"] in self.fragments
        ]

    def _clean_old_memories(self) -> None:
        max_memories = self.config.get("max_memories", 10000)
        if len(self.fragments) <= max_memories:
            return
        excess = len(self.fragments) - max_memories
        ordered = sorted(
            self.fragments.values(),
            key=lambda frag: (frag.importance, frag.last_accessed),
        )
        for fragment in ordered[:excess]:
            self.fragments.pop(fragment.id, None)
            self.timeline = [fid for fid in self.timeline if fid != fragment.id]

    async def store_insight(self, expression: str, insight: Dict[str, Any]) -> None:
        insight_experience = {
            "type": "reflective_insight",
            "content": expression,
            "emotional_valence": 0.8,
            "novelty": 0.9,
            "timestamp": datetime.utcnow(),
        }
        fragment = MemoryFragment(insight_experience, importance=0.9)
        self.fragments[fragment.id] = fragment
        self.timeline.append(fragment.id)

    async def persist_state(self) -> None:
        """Persist state to external storage (placeholder)."""
        pass


__all__ = ["MemoryStream", "MemoryFragment"]
