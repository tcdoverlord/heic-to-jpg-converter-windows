# Angel Project Information

| Field | Value |
|---|---|
| Project | HEIC to JPG Converter by TCDOVERLORD |
| Owner | TCDOVERLORD |
| Version | Not assigned by owner |
| Six-Color phase | Orange — Local Working Build |
| Current state | Owner reports the converter works locally |
| Primary platform | Windows 10 and Windows 11 |
| Primary language | Python |
| Interface | Tkinter desktop interface |
| Image engine | Pillow and pillow-heif |
| Build system | PowerShell and PyInstaller |
| Release signing | Unsigned |
| Requested path | `C:\DevTools\FullBuilds_Unsigned\heic_to_jpg_convert_TCDOVERLORD` |
| Last reviewed | 2026-07-20 |

## Purpose

Convert iPhone HEIC and HEIF photos into JPG copies on a local Windows computer.

The project is designed to preserve original photos, handle batches safely, provide clear failures, and support repeatable local builds.

## Current evidence

- The owner reports that the converter works locally.
- Six automated foundation tests previously passed.
- Source launch, test, and unsigned build scripts are present.
- Clean-machine testing has not been documented.
- A signed release has not been created.

## Read first

1. `README.md`
2. `PROJECT_CONTINUITY.md`
3. `docs/USER_GUIDE.md`
4. `docs/SAFETY.md`
5. `docs/TESTING.md`
6. `docs/ARCHITECTURE.md`

## Stable areas to protect

- Never delete or modify source photos.
- Keep **Rename** as the default collision policy.
- Keep temporary-file output before final placement.
- Continue the batch after an individual file failure.
- Keep conversion work outside the main interface thread.
- Preserve previous working builds.
- Do not claim compatibility tests that were not performed.
- Do not assign a version number without owner approval.
