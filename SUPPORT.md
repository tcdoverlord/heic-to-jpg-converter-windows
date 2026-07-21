# Support

## Start here

1. Open `README.md`.
2. Read `docs/USER_GUIDE.md`.
3. Read `docs/SAFETY.md`.
4. Check the session log.

Logs are normally stored here:

```text
%LOCALAPPDATA%\TCDOVERLORD\HEIC_to_JPG_Converter\logs
```

## Common problems

### The run script says Python is missing

Install Python 3.10 or newer. Then run `RUN_FROM_SOURCE.bat` again.

### The first start takes a while

The first start creates `.venv` and installs required packages. Later starts reuse that environment.

### A photo failed

The original photo should remain unchanged. Check the session log, copy the failing photo to a test folder, and retry without overwrite mode.

### A JPG already exists

Use the default **Rename** mode. The converter creates a new numbered JPG instead of replacing the existing file.

### Windows warns about the executable

The build is unsigned. Only run an executable that you built yourself or received from a source you trust.

## Asking for help

Include:

- Windows version.
- Whether you used the source launcher or executable.
- The action you selected.
- The exact error message.
- The session log with private information removed.
- Whether the problem happens with one file or every file.
