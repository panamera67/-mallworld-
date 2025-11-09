"""
DesireEngine - Génération et gestion des désirs cognitifs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


class Desire:
    """Représentation d'un désir cognitif."""

    def __init__(self, desire_type: str, intensity: float, target: Optional[Any] = None):
        self.type = desire_type
        self.intensity = max(0.0, min(1.0, intensity))
        self.target = target
        self.created = datetime.utcnow()
        self.last_satisfied: Optional[datetime] = None
        self.urgency = 0.5

    def decay(self, decay_rate: float = 0.1) -> None:
        self.intensity *= max(0.0, 1.0 - decay_rate)

    def boost(self, boost_amount: float) -> None:
        self.intensity = max(0.0, min(1.0, self.intensity + boost_amount))


class DesireEngine:
    """Moteur de motivation basé sur l'état interne et l'environnement."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_desires: List[Desire] = []

    async def generate_desires(
        self, internal_state: Dict[str, Any], world_update: Dict[str, Any]
    ) -> List[Desire]:
        for desire in self.active_desires:
            desire.decay(decay_rate=self.config.get("desire_decay_rate", 0.05))

        self.active_desires = [d for d in self.active_desires if d.intensity > 0.1]

        new_desires: List[Desire] = []

        curiosity = internal_state.get("curiosity", 0.5)
        if curiosity > 0.6:
            new_desires.append(
                Desire(
                    "knowledge_seeking",
                    intensity=curiosity * 0.8,
                    target={"domain": internal_state.get("attention_focus", "global")},
                )
            )

        complexity_gap = world_update.get("complexity_gap", 0.0)
        if complexity_gap > 0.7:
            new_desires.append(
                Desire(
                    "understanding_seeking",
                    intensity=complexity_gap,
                    target={"gap_type": world_update.get("gap_domain", "unknown")},
                )
            )

        energy_level = internal_state.get("energy_level", 0.5)
        if energy_level > 0.8:
            new_desires.append(
                Desire(
                    "creative_expression",
                    intensity=energy_level * 0.6,
                    target={"medium": "synthetic_expression"},
                )
            )

        self.active_desires.extend(new_desires)
        return self.active_desires

    def get_active_desires(self) -> List[Dict[str, Any]]:
        desires: List[Dict[str, Any]] = []
        for desire in self.active_desires:
            desires.append(
                {
                    "type": desire.type,
                    "intensity": desire.intensity,
                    "target": desire.target,
                    "urgency": desire.urgency,
                }
            )
        return desires

    async def satisfy_desire(self, desire_type: str, satisfaction_level: float) -> None:
        for desire in self.active_desires:
            if desire.type == desire_type:
                desire.intensity *= max(0.0, 1.0 - satisfaction_level)
                desire.last_satisfied = datetime.utcnow()


__all__ = ["Desire", "DesireEngine"]
