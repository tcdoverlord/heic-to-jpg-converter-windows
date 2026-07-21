from pathlib import Path

from heic_converter.models import CollisionPolicy
from heic_converter.paths import choose_output_path


def test_rename_policy_never_overwrites_existing_file(tmp_path: Path) -> None:
    (tmp_path / "photo.jpg").write_bytes(b"existing")
    (tmp_path / "photo_1.jpg").write_bytes(b"existing")

    target = choose_output_path(
        tmp_path,
        Path("photo.jpg"),
        CollisionPolicy.RENAME,
    )

    assert target == tmp_path / "photo_2.jpg"


def test_skip_policy_returns_none(tmp_path: Path) -> None:
    (tmp_path / "photo.jpg").write_bytes(b"existing")

    target = choose_output_path(
        tmp_path,
        Path("photo.jpg"),
        CollisionPolicy.SKIP,
    )

    assert target is None
