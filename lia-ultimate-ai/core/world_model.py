"""
WorldModel - Représentation interne du monde.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class WorldModel:
    """Modèle interne du monde avec croyances dynamiques."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.beliefs: Dict[str, Dict[str, Any]] = {}
        self.expectations: Dict[str, Any] = {}
        self.complexity = 0.0

    async def update(self, memories: List[Any]) -> Dict[str, Any]:
        for fragment in memories:
            concept = fragment.type
            confidence = min(1.0, fragment.importance)
            belief = self.beliefs.setdefault(
                concept,
                {
                    "confidence": 0.5,
                    "sources": [],
                    "first_observed": datetime.utcnow(),
                },
            )
            belief["confidence"] = (belief["confidence"] + confidence) / 2
            belief["last_updated"] = datetime.utcnow()
            belief["sources"].append(fragment.id)

        self.complexity = min(1.0, len(self.beliefs) / 100.0)
        return {
            "complexity_gap": max(0.0, 1.0 - self.complexity),
            "gap_domain": "emerging_patterns",
        }

    def get_complexity(self) -> float:
        return self.complexity

    async def save_state(self) -> None:
        """Persistance du modèle (placeholder)."""
        pass


__all__ = ["WorldModel"]
