from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .models import DiscoveredFile

HEIC_EXTENSIONS = {".heic", ".heif"}


def is_heic_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in HEIC_EXTENSIONS


def discover_files(
    inputs: Iterable[Path],
    *,
    recursive: bool,
) -> list[DiscoveredFile]:
    """Resolve files and folders into a stable, de-duplicated work list.

    For a single folder, its internal folder structure is preserved.
    For multiple inputs, each folder gets its own top-level folder in output.
    Directly selected files are placed at the output root.
    """
    normalized = [Path(item).expanduser() for item in inputs]
    multiple_inputs = len(normalized) > 1
    discovered: list[DiscoveredFile] = []
    seen: set[Path] = set()

    for item in normalized:
        if item.is_file():
            if is_heic_file(item):
                resolved = item.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    discovered.append(
                        DiscoveredFile(
                            source=resolved,
                            relative_output=Path(item.stem + ".jpg"),
                        )
                    )
            continue

        if not item.is_dir():
            continue

        iterator = item.rglob("*") if recursive else item.glob("*")
        prefix = Path(item.name) if multiple_inputs else Path()

        for candidate in iterator:
            if not is_heic_file(candidate):
                continue

            resolved = candidate.resolve()
            if resolved in seen:
                continue

            seen.add(resolved)
            relative = candidate.relative_to(item).with_suffix(".jpg")
            discovered.append(
                DiscoveredFile(
                    source=resolved,
                    relative_output=prefix / relative,
                )
            )

    return sorted(discovered, key=lambda entry: str(entry.source).casefold())
