"""MegaBrain: Persistent cross-agent memory, rule enforcer, and blindspot vaccine."""

from megabrain.db import MegaBrainDB
from megabrain.models import (
    ConsultationResult,
    Experience,
    GoldenPattern,
    MandatorySpec,
    Rule,
)

__version__ = "0.1.0"
__all__ = [
    "MegaBrainDB",
    "Rule",
    "MandatorySpec",
    "GoldenPattern",
    "Experience",
    "ConsultationResult",
    "__version__",
]
