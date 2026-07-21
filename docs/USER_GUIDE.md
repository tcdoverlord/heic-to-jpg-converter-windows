# User Guide

## The simple idea

The converter follows three steps:

```text
Input → Convert → Output
```

- **Input** is the HEIC or HEIF photo.
- **Convert** changes the image into JPG format.
- **Output** is the folder that receives the JPG copy.

The original photo stays where it is.

## Start the program

Double-click:

```text
RUN_FROM_SOURCE.bat
```

The script prepares the program and opens the window.

## Convert individual photos

1. Click **Add files**.
2. Choose one or more HEIC or HEIF photos.
3. Confirm the output folder.
4. Keep collision handling set to **Rename**.
5. Click **Convert to JPG**.
6. Wait for the summary.
7. Open a few JPG files and check them.

## Convert a folder

1. Click **Add folder**.
2. Choose the folder containing the photos.
3. Turn recursive scanning on when subfolders should also be searched.
4. Confirm the output folder.
5. Click **Convert to JPG**.

## Collision choices

### Rename

Safest default.

A numbered file is created when the JPG name already exists.

### Skip

The converter leaves the existing JPG alone and does not create another copy.

### Overwrite

The existing JPG is replaced.

Overwrite does not delete the HEIC source, but it can replace a JPG you wanted to keep. Use it only with copied test files or when replacement is deliberate.

## Cancel a batch

Use the cancellation control.

Cancellation takes effect between files. The current file is allowed to finish so it is less likely to be left incomplete.

## Check failures

Look at the activity summary and open the log folder.

A failed photo should not create a successful-looking final JPG. The original remains available for another attempt.

## Before deleting anything from an iPhone or USB drive

1. Confirm the expected number of JPG files exists.
2. Open several JPG files.
3. Check portrait and landscape orientation.
4. Check colors.
5. Check important dates or metadata.
6. Keep another copy of the originals.
