# Safety Guide

## Core promise

The converter reads HEIC and HEIF source files and creates separate JPG files.

It does not contain a feature that deletes the original photos.

## Safe defaults

- Existing JPG files are renamed instead of overwritten.
- Output is written to a temporary file first.
- The temporary file is moved into its final name only after saving succeeds.
- One failed photo does not stop the remaining batch.
- Cancellation takes effect between files.
- Failures are written to a session log.

## Before converting important photos

1. Keep another copy of the original photos.
2. Start with a small test folder.
3. Use the default **Rename** mode.
4. Open several converted JPG files.
5. Check orientation, color, dimensions, and dates.
6. Compare discovered, completed, skipped, and failed totals.
7. Review failures before deleting photos from any other storage.

## Overwrite warning

Overwrite mode can replace an existing JPG.

It does not overwrite the HEIC source, but it can destroy a JPG you wanted to keep.

Use **Rename** unless replacement is intentional.

## Metadata limits

The converter attempts to preserve EXIF data and ICC color profiles when the decoding library provides them.

HEIC can contain more than one image or additional information such as depth data and edits. JPG cannot preserve every HEIC feature.

## When a conversion fails

- The source should remain untouched.
- The unfinished temporary file is removed when possible.
- A successful-looking final JPG should not remain.
- The error is written to the activity panel and session log.

## Unsigned executable

The generated Windows executable is intentionally unsigned.

Windows SmartScreen or antivirus software may warn about it. Build from trusted source and do not bypass warnings for an executable from an unknown source.

## Recovery

1. Stop the batch.
2. Preserve the original photos.
3. Preserve the session log.
4. Record the exact file that failed.
5. Reproduce the problem using a copied test photo.
6. Do not repeatedly overwrite the same output.
7. Record confirmed problems in `PROJECT_CONTINUITY.md`.
