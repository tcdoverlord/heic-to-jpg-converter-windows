<p align="center">
  <img src="images/heic-to-jpeg-hero.jpg" alt="HEIC to JPG Converter" width="100%">
</p>

# HEIC to JPG Converter by TCDOVERLORD

A local Windows desktop app for converting HEIC and HEIF photos to JPG.

## Features

- Drag and drop photos or use the file picker.
- Select up to 20 photos per batch.
- Choose a destination folder.
- Adjust JPEG quality (default 95%).
- Review per-file conversion results.
- Original photos are left unchanged.
- Existing output files are not intentionally overwritten.
- Conversion runs locally without photo uploads or accounts.

## Build on Windows

Install the stable Rust toolchain and vcpkg, then install libheif for the x64 static triplet:

```powershell
vcpkg install libheif:x64-windows-static-md
$env:VCPKG_ROOT = "C:\DevTools\vcpkg"
cargo build --release
```

The executable is created at `target\release\tcd-heic-to-jpg.exe`.

## Download

After a successful GitHub Actions run, download the Windows x64 artifact from the workflow run in the repository Actions tab. The executable is unsigned, so Windows may display a SmartScreen warning.

## Legacy Python edition

The original Python application, tests, and build scripts are preserved in [`legacy-python`](legacy-python/README.md).

## Documentation

- [Rust edition build notes](docs/RUST_EDITION_README.md)
- [Rust migration notes](docs/RUST_MIGRATION_NOTES.md)
- [Safety guide](docs/SAFETY.md)
- [Testing guide](docs/TESTING.md)
- [Project continuity](PROJECT_CONTINUITY.md)

## License

See [LICENSE](LICENSE).
