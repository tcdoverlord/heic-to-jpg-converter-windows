from pathlib import Path

from heic_converter.scanner import discover_files


def test_discover_files_is_case_insensitive_and_recursive(tmp_path: Path) -> None:
    nested = tmp_path / "album" / "day1"
    nested.mkdir(parents=True)
    (nested / "one.HEIC").write_bytes(b"test")
    (nested / "two.heif").write_bytes(b"test")
    (nested / "ignore.jpg").write_bytes(b"test")

    items = discover_files([tmp_path / "album"], recursive=True)

    assert [item.source.name for item in items] == ["one.HEIC", "two.heif"]
    assert [item.relative_output.as_posix() for item in items] == [
        "day1/one.jpg",
        "day1/two.jpg",
    ]


def test_multiple_folders_keep_separate_top_level_names(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    (first / "same.heic").write_bytes(b"1")
    (second / "same.heic").write_bytes(b"2")

    items = discover_files([first, second], recursive=True)

    assert [item.relative_output.as_posix() for item in items] == [
        "first/same.jpg",
        "second/same.jpg",
    ]
