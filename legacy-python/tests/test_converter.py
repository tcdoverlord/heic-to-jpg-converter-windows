from pathlib import Path

from PIL import Image

from heic_converter import converter
from heic_converter.models import (
    CollisionPolicy,
    ConversionOptions,
    ConversionStatus,
    DiscoveredFile,
)


def test_conversion_preserves_source_and_writes_jpeg(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "source.heic"
    # Pillow detects the image from its file signature, which lets this unit test
    # exercise conversion logic without requiring a real HEIC decoder.
    Image.new("RGB", (12, 8), (10, 20, 30)).save(source, format="JPEG")
    original = source.read_bytes()

    monkeypatch.setattr(converter, "register_heif_support", lambda: None)

    output_root = tmp_path / "output"
    result = converter.convert_one(
        DiscoveredFile(source=source, relative_output=Path("source.jpg")),
        ConversionOptions(
            output_root=output_root,
            quality=90,
            collision_policy=CollisionPolicy.RENAME,
            preserve_timestamps=False,
        ),
    )

    assert result.status is ConversionStatus.CONVERTED
    assert source.read_bytes() == original
    assert result.output == output_root / "source.jpg"

    with Image.open(result.output) as jpg:
        assert jpg.format == "JPEG"
        assert jpg.size == (12, 8)


def test_invalid_image_fails_without_partial_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "broken.heic"
    source.write_bytes(b"not-an-image")
    monkeypatch.setattr(converter, "register_heif_support", lambda: None)

    output_root = tmp_path / "output"
    result = converter.convert_one(
        DiscoveredFile(source=source, relative_output=Path("broken.jpg")),
        ConversionOptions(output_root=output_root),
    )

    assert result.status is ConversionStatus.FAILED
    assert not (output_root / "broken.jpg").exists()
    assert not list(output_root.glob("*.tmp"))
