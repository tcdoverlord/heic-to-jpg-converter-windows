# Project Continuity

## Why this project exists

iPhones commonly save photos as HEIC. JPG is easier to use with older software, websites, printers, televisions, and mixed Windows workflows.

This project provides a local converter so private photos do not need to be uploaded to an online conversion service.

## Current engineering state

| Field | State |
|---|---|
| Owner | TCDOVERLORD |
| Version | Not assigned |
| Six-Color phase | Orange — Local Working Build |
| Local operation | Owner reports working |
| Automated foundation tests | 6 passed on 2026-07-20 |
| Real local HEIC use | Confirmed generally by owner |
| Exact Windows test record | Not yet documented |
| Clean second-machine test | Not documented |
| Executable signing | Not performed |
| Public release status | Not yet approved |

## Why the project is Orange

Orange asks whether the core system works honestly on the development computer.

The owner has confirmed that the converter works. This supports moving the project from Red foundation work into Orange local working status.

The next phase, Yellow, requires compatibility evidence outside the original working environment. That evidence has not yet been recorded.

## Completed work

- Modular Python project structure.
- Tkinter desktop interface.
- Individual file selection.
- Folder selection.
- Recursive scanning.
- Relative folder preservation.
- HEIC and HEIF discovery.
- JPG conversion.
- Rename, skip, and overwrite collision policies.
- Safe rename default.
- EXIF orientation correction.
- EXIF and ICC preservation attempts.
- Temporary-file output before final placement.
- Original-file timestamp preservation.
- Per-file failure handling.
- Progress and cancellation.
- User-local session logs.
- Command-line mode.
- Automated foundation tests.
- Source run script.
- Safe requested-path installer.
- Unsigned PyInstaller build script.
- Previous-build preservation.
- SHA-256 checksum generation.
- Repository documentation.

## Stable behavior to protect

The following behavior should not be removed during future changes:

1. Original HEIC and HEIF files remain untouched.
2. Existing JPG files are renamed by default instead of overwritten.
3. Failed conversions do not leave a successful-looking final JPG.
4. One failed file does not stop the complete batch.
5. The interface remains responsive during conversion.
6. Previous working builds are preserved before replacement.
7. Test and documentation claims remain evidence-based.

## Known limits and unknowns

- The exact Windows computer and test conditions have not been recorded.
- Clean-machine operation has not been verified.
- Very large batches have not been stress-tested.
- Some HEIC metadata or auxiliary images may not transfer to JPG.
- Windows SmartScreen may warn because the executable is unsigned.
- Dependency compatibility should be checked before future upgrades.
- The complete owner-approved TPLL legal text is still required before public distribution.

## Smallest responsible next steps

1. Record the working Windows environment in a dated test report.
2. Test five to ten copied iPhone HEIC photos with different orientations.
3. Test duplicate JPG names using the default rename mode.
4. Test one damaged or unsupported file.
5. Run the automated test script.
6. Build the unsigned executable.
7. Test the executable on a second Windows account or computer.
8. Update the test record and changelog.
9. Let the owner decide when to assign a version and release tag.

## Recovery guidance

- Keep original photos backed up outside the repository.
- Commit the current working state before changing code.
- Create a branch for behavior changes.
- Keep previous unsigned builds under `build_output\previous`.
- Do not replace the only working executable without preserving it.
- Use the logs and a copied test photo when reproducing failures.

## Suggested first repository commit

```text
feat: add working HEIC to JPG converter
```

## Files to read after a long pause

1. `README.md`
2. `ANGEL_PROJECT_INFO.md`
3. `PROJECT_CONTINUITY.md`
4. `CHANGELOG.md`
5. `docs/SAFETY.md`
6. `docs/TESTING.md`
7. `docs/ARCHITECTURE.md`
