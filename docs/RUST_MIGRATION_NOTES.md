# Rust migration notes

## Goal

Provide a native Rust Windows desktop app for converting HEIC and HEIF photos to JPG without requiring Python at runtime.

## Current layout

- `Cargo.toml` and `Cargo.lock`: Rust project configuration and locked dependencies.
- `src/`: Rust application source.
- `.github/workflows/build-rust-windows.yml`: Windows x64 build workflow.
- `legacy-python/`: preserved Python application, tests, and build scripts.
- `README.md`: primary project documentation.

## Implemented features

- File picker and drag-and-drop input.
- Up to 20 photos per batch.
- Destination-folder selection.
- Adjustable JPEG quality, default 95%.
- Background conversion and per-file status reporting.
- Local conversion without uploading photos.
- Original input files are preserved.
- Output-name collision handling.

## Local validation

- `cargo build --release` succeeded on Windows from the repository root.
- The resulting executable was produced at `target/release/tcd-heic-to-jpg.exe`.
- The application was previously launched from an extracted release ZIP.
- Conversion was previously tested with a HEIC image and produced a JPG.

## Remaining validation

- Run the GitHub Actions workflow after pushing the migration.
- Confirm the hosted Windows runner installs the required vcpkg `libheif` dependency and completes the release build.
- Test the packaged build from a clean folder with multiple HEIC/HEIF files, including filenames with spaces, duplicate output names, and unsupported or damaged inputs.
- Confirm the workflow artifact contains the expected executable and checksum.

HEIC decoder support depends on the linked libheif build and the codecs it provides. Keep backups of irreplaceable originals when testing.
