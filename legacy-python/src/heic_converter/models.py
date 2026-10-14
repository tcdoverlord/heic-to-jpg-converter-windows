from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class CollisionPolicy(str, Enum):
    """What to do when a target JPG already exists."""

    RENAME = "rename"
    SKIP = "skip"
    OVERWRITE = "overwrite"


class ConversionStatus(str, Enum):
    CONVERTED = "converted"
    SKIPPED = "skipped"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class DiscoveredFile:
    source: Path
    relative_output: Path


@dataclass(frozen=True, slots=True)
class ConversionOptions:
    output_root: Path
    quality: int = 95
    collision_policy: CollisionPolicy = CollisionPolicy.RENAME
    preserve_timestamps: bool = True


@dataclass(frozen=True, slots=True)
class ConversionResult:
    source: Path
    status: ConversionStatus
    output: Path | None = None
    message: str = ""
