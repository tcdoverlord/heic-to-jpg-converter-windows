from __future__ import annotations

import argparse
from pathlib import Path

from .converter import convert_batch
from .models import CollisionPolicy, ConversionOptions, ConversionStatus
from .scanner import discover_files


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="HEIC to JPG Converter",
        description="Convert HEIC and HEIF images to JPG without deleting originals.",
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="HEIC files or folders")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path.cwd() / "JPG Converted",
        help="Output folder",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=95,
        help="JPEG quality from 1 to 100 (default: 95)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan inside subfolders",
    )
    parser.add_argument(
        "--collision",
        choices=[policy.value for policy in CollisionPolicy],
        default=CollisionPolicy.RENAME.value,
        help="How to handle an existing JPG (default: rename)",
    )
    parser.add_argument(
        "--no-preserve-timestamps",
        action="store_true",
        help="Do not copy source file timestamps to the JPG",
    )
    return parser


def run_cli(arguments: list[str]) -> int:
    args = _parser().parse_args(arguments)
    items = discover_files(args.inputs, recursive=args.recursive)

    if not items:
        print("No HEIC or HEIF files were found.")
        return 1

    options = ConversionOptions(
        output_root=args.output.resolve(),
        quality=args.quality,
        collision_policy=CollisionPolicy(args.collision),
        preserve_timestamps=not args.no_preserve_timestamps,
    )

    def report(index: int, total: int, result) -> None:
        label = result.status.value.upper()
        destination = f" -> {result.output}" if result.output else ""
        print(f"[{index}/{total}] {label}: {result.source}{destination}")
        if result.message and result.status is ConversionStatus.FAILED:
            print(f"    {result.message}")

    results = convert_batch(items, options, progress_callback=report)
    failures = sum(result.status is ConversionStatus.FAILED for result in results)
    converted = sum(result.status is ConversionStatus.CONVERTED for result in results)
    skipped = sum(result.status is ConversionStatus.SKIPPED for result in results)

    print(f"Finished: {converted} converted, {skipped} skipped, {failures} failed.")
    return 1 if failures else 0
