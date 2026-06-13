from dataclasses import dataclass
from enum import StrEnum


class IndexabilityStatus(StrEnum):
    DRAFT = "draft"
    NOINDEX = "noindex"
    INDEXABLE = "indexable"


@dataclass(frozen=True)
class IndexabilityDecision:
    allowed: bool
    reason: str
