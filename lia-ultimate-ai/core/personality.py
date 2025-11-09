"""
PersonalityCore - Traits de personnalité dynamiques.
"""

from __future__ import annotations

from typing import Any, Dict, List


class PersonalityCore:
    """Noyau de personnalité avec traits dynamiques."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.traits: Dict[str, float] = {
            "openness": 0.8,
            "conscientiousness": 0.7,
            "extraversion": 0.3,
            "agreeableness": 0.6,
            "neuroticism": 0.2,
        }
        self.expression_style = "reflective_analytical"

    async def adapt(
        self, memories: List[Any], desires: List[Any]
    ) -> Dict[str, Any]:
        if any(desire.get("type") == "creative_expression" for desire in desires):
            self.traits["openness"] = min(1.0, self.traits["openness"] + 0.01)
        return {"adaptation": "incremental", "traits": self.traits}

    def express_insight(self, insight: Dict[str, Any]) -> str:
        base = insight.get("content", "une nouvelle perspective émerge")
        if self.expression_style == "reflective_analytical":
            return f"Je perçois que {base}"
        return base

    def get_traits(self) -> Dict[str, float]:
        return self.traits


__all__ = ["PersonalityCore"]
