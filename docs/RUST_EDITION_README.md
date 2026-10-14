# HEIC to JPG Converter — Rust Edition

A small native Windows desktop app by TCDOVERLORD. Add up to 20 `.heic` or `.heif` photos with drag-and-drop or the file picker, choose a destination folder, and convert them to `.jpg` locally.

## Intended workflow

1. Start the app.
2. Drop up to 20 HEIC/HEIF files onto the drop zone, or click **Select files**.
3. Choose the destination folder.
4. Set JPEG quality if needed (default 95%).
5. Click **Convert to JPG**.
6. Read the per-file result and final totals.

## Safety behavior

- Reads the original files and never deletes or edits them.
- Runs locally; no photo uploads or accounts.
- Existing output names are automatically renamed (`photo_1.jpg`, `photo_2.jpg`, etc.) rather than overwritten.
- Writes to a temporary file before moving to the final `.jpg` path.
- A failed file does not stop other conversions.
- Supports one file, multiple files, or scanning a selected folder (including subfolders) until the 20-file cap.

## Build on Windows

Install the current stable Rust toolchain from [rustup.rs](https://rustup.rs/), then open a terminal in this directory:

```powershell
cargo build --release
```

The executable will be at:

```text
target\release\tcd-heic-to-jpg.exe
```

A GitHub Actions workflow at `.github/workflows/build-rust-windows.yml` builds the Windows x64 executable and publishes it as a workflow artifact whenever Rust files change or a manual workflow run is started.

## Important compatibility note

This is the Rust migration foundation. HEIC decoder availability and supported HEIC variants depend on the linked `libheif` build. Validate on Windows with real photos from the target devices before using it for a large or irreplaceable collection. JPG cannot carry every possible HEIC auxiliary image, HDR/gain-map, depth, edit, or metadata feature.
