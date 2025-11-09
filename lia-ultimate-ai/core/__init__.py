"""Core package exposing the cognitive components for LIA."""

from .digital_being import LIAAsDigitalBeing  # noqa: F401
from .memory_stream import MemoryStream  # noqa: F401
from .desire_engine import DesireEngine  # noqa: F401
from .meta_learning import MetaLearningProcessor  # noqa: F401
from .personality import PersonalityCore  # noqa: F401
from .world_model import WorldModel  # noqa: F401
from .awakening import AwakeningEngine  # noqa: F401

__all__ = [
    "LIAAsDigitalBeing",
    "MemoryStream",
    "DesireEngine",
    "MetaLearningProcessor",
    "PersonalityCore",
    "WorldModel",
    "AwakeningEngine",
]
