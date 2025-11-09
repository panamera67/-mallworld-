from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Conscience metrics
CONSCIOUSNESS_LEVEL = Gauge(
    "lia_consciousness_level", "Niveau de conscience actuel"
)
DESIRE_INTENSITY = Gauge(
    "lia_desire_intensity", "Intensité des désirs actifs", ["type"]
)
MEMORY_FRAGMENTS = Gauge(
    "lia_memory_fragments", "Nombre de fragments en mémoire"
)
COGNITIVE_CYCLES = Counter(
    "lia_cognitive_cycles_total", "Nombre total de cycles cognitifs exécutés"
)
CYCLE_DURATION = Histogram(
    "lia_cycle_duration_seconds", "Durée des cycles cognitifs"
)

# API metrics
API_REQUESTS = Counter(
    "lia_api_requests_total",
    "Total des requêtes API",
    ["endpoint", "method"],
)
REQUEST_DURATION = Histogram(
    "lia_request_duration_seconds", "Durée des requêtes API (secondes)"
)


def update_consciousness_metrics(digital_being) -> None:
    """Met à jour les métriques Prometheus à partir du statut courant."""
    try:
        status = digital_being.get_status()
    except Exception:
        return

    CONSCIOUSNESS_LEVEL.set(status.get("consciousness_level", 0.0))
    MEMORY_FRAGMENTS.set(len(digital_being.memory.fragments))
    COGNITIVE_CYCLES.inc()

    for desire in status.get("active_desires", []):
        desire_type = desire.get("type", "unknown")
        intensity = desire.get("intensity", 0.0)
        DESIRE_INTENSITY.labels(type=desire_type).set(intensity)


__all__ = [
    "CONTENT_TYPE_LATEST",
    "generate_latest",
    "CONSCIOUSNESS_LEVEL",
    "DESIRE_INTENSITY",
    "MEMORY_FRAGMENTS",
    "COGNITIVE_CYCLES",
    "CYCLE_DURATION",
    "API_REQUESTS",
    "REQUEST_DURATION",
    "update_consciousness_metrics",
]
