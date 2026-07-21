# Testing Guide

## Automated tests

Run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Run-Tests.ps1
```

The unsigned build script runs the same tests before packaging.

## Current evidence

- Six automated foundation tests passed on July 20, 2026.
- The owner reports that the converter works locally.
- Exact Windows environment details have not yet been recorded.
- Clean second-machine compatibility has not yet been documented.

## Automated coverage

The tests check:

- HEIC and HEIF extensions are found without case sensitivity.
- Recursive scanning preserves relative folders.
- Several selected folders receive separate top-level output folders.
- Rename mode avoids existing JPG files.
- Skip mode returns no output target.
- Source bytes remain unchanged.
- The conversion pipeline creates a valid JPG.
- Invalid input returns a failure.
- A failed conversion does not leave a final JPG or temporary file.

The foundation conversion test uses a JPG payload with a `.heic` file name. This tests the safety and output pipeline without falsely claiming decoder coverage.

## Record a real Windows test

Create a dated file such as:

```text
docs\TEST_RESULTS_2026-07-20_WINDOWS.md
```

Record:

- Windows edition and build.
- Python version.
- Package versions.
- Whether the source launcher or executable was used.
- Number of input files.
- Approximate total size.
- Source of the photos.
- Quality and collision settings.
- Completed, skipped, and failed totals.
- Orientation result.
- Color result.
- Metadata result.
- Log path.
- Pass or fail.

## Recommended test cases

1. One portrait HEIC.
2. One landscape HEIC.
3. A file name containing spaces.
4. A file name containing non-English characters.
5. A folder containing subfolders.
6. An existing JPG in rename mode.
7. An existing JPG in skip mode.
8. Overwrite mode using copied test files.
9. A damaged photo.
10. Cancellation during a batch.
11. A batch of at least 100 copied photos.
12. A second Windows account or computer.

## Build verification

After `BUILD_UNSIGNED.bat` finishes:

1. Confirm the executable exists.
2. Confirm `SHA256SUMS.txt` exists.
3. Compare its checksum with `Get-FileHash`.
4. Run the executable.
5. Convert copied HEIC files.
6. Confirm logs open.
7. Record SmartScreen or antivirus behavior.
8. Repeat on another computer when available.
