# Contributing

Thank you for helping improve the HEIC to JPG Converter.

This is currently a TCDOVERLORD personal learning project. Changes should be small, understandable, reversible, and supported by evidence.

## Before changing code

1. Read `README.md`.
2. Read `PROJECT_CONTINUITY.md`.
3. Read `docs/SAFETY.md`.
4. Create a branch.
5. Preserve the current working state.

## Development rules

- Do not delete or modify source photos.
- Do not change the default collision policy away from **Rename** without owner approval.
- Do not hide conversion failures.
- Do not claim tests that were not performed.
- Do not assign or change version numbers.
- Prefer a focused change over a rewrite.
- Update documentation when behavior changes.

## Run the tests

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Run-Tests.ps1
```

## Pull requests

A pull request should explain:

- What problem is being solved.
- Why the change is needed.
- Which files changed.
- How the change was tested.
- What remains unverified.
- How to recover if the change fails.

Use the repository pull request template.
