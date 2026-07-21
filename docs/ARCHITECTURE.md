# Architecture

## Goal

Keep the project small enough to understand while separating parts that change for different reasons.

## Main modules

### `main.py`

Starts the project and adds the `src` folder to the Python path.

### `app.py`

Chooses graphical or command-line operation and starts logging.

### `gui.py`

Owns the Windows interface, selections, progress, cancellation, and worker thread.

It does not directly contain the complete conversion engine.

### `cli.py`

Reads command-line options and prints terminal results.

It uses the same scanner and converter as the graphical interface.

### `scanner.py`

Finds HEIC and HEIF files, removes duplicates, and calculates relative paths.

### `converter.py`

Registers HEIC decoding, corrects orientation, creates a JPG-compatible RGB image, attempts to preserve supported metadata, writes through a temporary file, and reports the result.

### `paths.py`

Handles rename, skip, and overwrite behavior.

### `models.py`

Contains shared enums and data structures.

### `logging_setup.py`

Creates a separate session log in the user's local application-data folder.

## Execution flow

```text
User chooses input
        |
        v
Scanner finds HEIC and HEIF files
        |
        v
Collision policy chooses output names
        |
        v
pillow-heif enables HEIC decoding
        |
        v
Pillow opens and rotates the image correctly
        |
        v
The image is converted to JPG-compatible RGB
        |
        v
A temporary JPG is written
        |
        v
The temporary file becomes the final JPG
        |
        v
The result is shown and logged
```

## Protected design decisions

- Original photos are never deleted.
- Rename is the default collision policy.
- Conversion runs outside the main interface thread.
- One failed file does not stop the full batch.
- Builds are created on Windows.
- A previous unsigned build is preserved before replacement.
- Version numbers remain under owner control.

## Future improvements

Possible later improvements include:

- A fixed `IN` and `OUT` folder mode.
- Drag-and-drop support.
- Thumbnail previews.
- Better metadata verification.
- Clean-machine build automation.
- Optional digital signing.

These should be added as modules or focused changes rather than through a full rewrite.
