# Test Results — 2026-07-20

## Environment

- Operating system: Linux creation workspace
- Python: 3.13.5
- Test runner: pytest available in the workspace
- Real `pillow-heif` decoder: not installed in the workspace
- Windows executable build: not attempted

## Command

```text
python -m pytest -q
```

## Result

```text
6 passed in 0.17s
```

## Verified

- Recursive and case-insensitive HEIC/HEIF discovery.
- Output folder preservation for one or several source folders.
- Safe collision renaming.
- Skip collision behavior.
- Source bytes remain unchanged during conversion.
- A valid JPEG is produced by the conversion pipeline.
- Invalid image input reports failure.
- Failed conversion leaves no final JPG or temporary output.

## Not verified

- Decoding a real iPhone HEIC file.
- Metadata behavior from a real iPhone HEIC file.
- Windows Tkinter behavior.
- Windows PyInstaller packaging.
- Clean-machine operation.
- Large batches.
- Digital signing.

The image conversion unit test uses a JPEG payload with a `.heic` filename so the conversion and safety pipeline can be tested without falsely claiming HEIC decoder coverage.
