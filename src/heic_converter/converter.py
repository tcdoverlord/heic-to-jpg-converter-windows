from __future__ import annotations

import logging
import os
import uuid
from collections.abc import Callable, Iterable
from pathlib import Path
from threading import Event

from PIL import Image, ImageOps

from .models import (
    CollisionPolicy,
    ConversionOptions,
    ConversionResult,
    ConversionStatus,
    DiscoveredFile,
)
from .paths import choose_output_path

LOGGER = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, ConversionResult], None]


class MissingDependencyError(RuntimeError):
    """Raised when HEIC decoding support is not installed."""


def register_heif_support() -> None:
    """Register pillow-heif as a Pillow image loader."""
    try:
        from pillow_heif import register_heif_opener
    except ImportError as exc:
        raise MissingDependencyError(
            "pillow-heif is not installed. Run scripts\\Setup-Environment.ps1."
        ) from exc

    register_heif_opener()


def validate_quality(quality: int) -> int:
    if not 1 <= quality <= 100:
        raise ValueError("JPEG quality must be between 1 and 100.")
    return quality


def _flatten_for_jpeg(image: Image.Image) -> Image.Image:
    """Convert a Pillow image to a JPEG-compatible image.

    Transparent pixels are composited over white instead of becoming black.
    """
    if image.mode in {"RGBA", "LA"} or (
        image.mode == "P" and "transparency" in image.info
    ):
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background

    if image.mode == "RGB":
        return image.copy()

    return image.convert("RGB")


def convert_one(
    item: DiscoveredFile,
    options: ConversionOptions,
) -> ConversionResult:
    """Convert one HEIC/HEIF file while preserving the source."""
    validate_quality(options.quality)

    target = choose_output_path(
        options.output_root,
        item.relative_output,
        options.collision_policy,
    )
    if target is None:
        return ConversionResult(
            source=item.source,
            status=ConversionStatus.SKIPPED,
            message="Target already exists.",
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")

    try:
        register_heif_support()

        with Image.open(item.source) as opened:
            opened.load()
            oriented = ImageOps.exif_transpose(opened)
            converted = _flatten_for_jpeg(oriented)

            save_options: dict[str, object] = {
                "format": "JPEG",
                "quality": options.quality,
                "optimize": True,
            }

            exif = oriented.getexif()
            if exif:
                save_options["exif"] = exif.tobytes()

            icc_profile = oriented.info.get("icc_profile")
            if icc_profile:
                save_options["icc_profile"] = icc_profile

            converted.save(temporary, **save_options)

        # os.replace keeps the final path from containing a partially written JPG.
        os.replace(temporary, target)

        timestamp_warning = ""
        if options.preserve_timestamps:
            try:
                source_stat = item.source.stat()
                os.utime(
                    target,
                    ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns),
                )
            except OSError as exc:
                timestamp_warning = f" JPG created, but timestamps were not preserved: {exc}"
                LOGGER.warning(
                    "Converted %s but could not preserve timestamps on %s: %s",
                    item.source,
                    target,
                    exc,
                )

        LOGGER.info("Converted %s -> %s", item.source, target)
        return ConversionResult(
            source=item.source,
            status=ConversionStatus.CONVERTED,
            output=target,
            message="Converted successfully." + timestamp_warning,
        )

    except Exception as exc:
        LOGGER.exception("Failed to convert %s", item.source)
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            LOGGER.warning("Could not remove temporary file %s", temporary)

        return ConversionResult(
            source=item.source,
            status=ConversionStatus.FAILED,
            output=None,
            message=str(exc),
        )


def convert_batch(
    items: Iterable[DiscoveredFile],
    options: ConversionOptions,
    *,
    cancel_event: Event | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[ConversionResult]:
    work = list(items)
    total = len(work)
    results: list[ConversionResult] = []

    for index, item in enumerate(work, start=1):
        if cancel_event is not None and cancel_event.is_set():
            result = ConversionResult(
                source=item.source,
                status=ConversionStatus.CANCELLED,
                message="Batch cancelled before this file started.",
            )
            results.append(result)
            if progress_callback:
                progress_callback(index, total, result)
            break

        result = convert_one(item, options)
        results.append(result)

        if progress_callback:
            progress_callback(index, total, result)

    return results
