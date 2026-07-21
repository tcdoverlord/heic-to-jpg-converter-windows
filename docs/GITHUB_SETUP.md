# GitHub Repository Setup

## Repository name

Recommended name:

```text
heic_to_jpg_convert_TCDOVERLORD
```

## Before the first commit

Place these documentation files inside the working project.

Make sure the project also contains:

```text
.gitignore
main.py
src
tests
scripts
requirements.txt
requirements-build.txt
RUN_FROM_SOURCE.bat
BUILD_UNSIGNED.bat
INSTALL_TO_REQUESTED_PATH.bat
```

Do not commit:

```text
.venv
__pycache__
.pytest_cache
build
dist
build_output
private photos
session logs
```

## Create the local repository

Open PowerShell inside the project folder:

```powershell
cd C:\DevTools\FullBuilds_Unsigned\heic_to_jpg_convert_TCDOVERLORD
git init
git branch -M main
git status
git add .
git status
git commit -m "feat: add working HEIC to JPG converter"
```

The second `git status` is important. Review the file list before committing.

## Create the GitHub repository

Create an empty GitHub repository named:

```text
heic_to_jpg_convert_TCDOVERLORD
```

When the local project already has documentation, do not ask GitHub to create another README, license, or `.gitignore`.

Copy the repository address from GitHub.

## Connect and push

Replace the example address with the address GitHub provides:

```powershell
git remote add origin <YOUR-GITHUB-REPOSITORY-ADDRESS>
git push -u origin main
```

## Verify

After pushing:

1. Open the repository page.
2. Confirm the README appears.
3. Confirm no private photos or logs were uploaded.
4. Confirm `.venv` and build folders are absent.
5. Open several documentation links.
6. Check the latest commit message.
7. Keep the working local folder and another backup.

## Safe update flow

```text
Build
Test
Document
git status
git add .
git status
git commit
git push
Verify
```
