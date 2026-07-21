from __future__ import annotations

from pathlib import Path

from .models import CollisionPolicy


def choose_output_path(
    output_root: Path,
    relative_output: Path,
    policy: CollisionPolicy,
) -> Path | None:
    """Return a safe target path, or None when collision policy says skip."""
    candidate = output_root / relative_output
    candidate = candidate.with_suffix(".jpg")

    if not candidate.exists():
        return candidate

    if policy is CollisionPolicy.SKIP:
        return None

    if policy is CollisionPolicy.OVERWRITE:
        return candidate

    index = 1
    while True:
        renamed = candidate.with_name(f"{candidate.stem}_{index}{candidate.suffix}")
        if not renamed.exists():
            return renamed
        index += 1
