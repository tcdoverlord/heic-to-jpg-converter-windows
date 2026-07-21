#requires -Version 5.1
<#
Creates the first GitHub repository for the working HEIC to JPG converter.

Safety rules:
- Verifies the active GitHub account is TCDOVERLORD before git init.
- Verifies the exact project folder before git init.
- Stops if the folder is nested inside another Git repository.
- Uses repository-local Git identity settings.
- Blocks common private photos, videos, logs, build output, and secrets.
- Creates a public repository for discoverability and SEO.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectPath = "C:\DevTools\FullBuilds_Unsigned\heic_to_jpg_convert_TCDOVERLORD"
$GitHubOwner = "tcdoverlord"

# The local folder keeps its current name.
# The public GitHub repository uses a clearer search-friendly name.
$RepositoryName = "heic-to-jpg-converter-windows"
$RepositoryFullName = "$GitHubOwner/$RepositoryName"

$Description = "Offline Windows HEIC and HEIF to JPG converter for iPhone photos with batch conversion, safe file naming, metadata preservation, logs, and unsigned local builds."

$Topics = @(
    "heic",
    "heif",
    "jpg",
    "jpeg",
    "converter",
    "windows",
    "iphone",
    "iphone-photos",
    "batch-conversion",
    "image-converter",
    "photo-converter",
    "python",
    "pillow",
    "tkinter",
    "offline",
    "privacy"
)

function Write-Section {
    param([Parameter(Mandatory = $true)][string]$Text)

    Write-Host ""
    Write-Host ("=" * 72) -ForegroundColor DarkCyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ("=" * 72) -ForegroundColor DarkCyan
}

function Stop-Safely {
    param([Parameter(Mandatory = $true)][string]$Message)

    Write-Host ""
    Write-Host "STOPPED SAFELY" -ForegroundColor Red
    Write-Host $Message -ForegroundColor Yellow
    exit 1
}

function Assert-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Stop-Safely "Required command '$Name' was not found. Install it, reopen PowerShell, and run this script again."
    }
}

function Get-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $FullPath = [System.IO.Path]::GetFullPath($Path)
    $TrimCharacters = [char[]]@(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    return $FullPath.TrimEnd($TrimCharacters)
}

Write-Section "1. VERIFY THE EXACT PROJECT FOLDER"

if (-not (Test-Path -LiteralPath $ProjectPath -PathType Container)) {
    Stop-Safely "The project folder does not exist: $ProjectPath"
}

$ExpectedPath = Get-NormalizedPath -Path $ProjectPath
$ResolvedPath = Get-NormalizedPath -Path (Resolve-Path -LiteralPath $ProjectPath).Path

if (-not [string]::Equals(
    $ExpectedPath,
    $ResolvedPath,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    Stop-Safely "The resolved folder does not match the expected project folder."
}

Set-Location -LiteralPath $ResolvedPath

if (-not (Test-Path -LiteralPath ".\README.md" -PathType Leaf)) {
    Stop-Safely "README.md is missing. Add the repository documentation before publishing."
}

if (-not (Test-Path -LiteralPath ".\.gitignore" -PathType Leaf)) {
    Stop-Safely ".gitignore is missing. Publishing without it could expose build files or private data."
}

Write-Host "Confirmed project folder:" -ForegroundColor Green
Write-Host $ResolvedPath

Write-Section "2. VERIFY GIT AND GITHUB CLI"

Assert-Command -Name "git"
Assert-Command -Name "gh"

Write-Host "Git:"
& git --version
if ($LASTEXITCODE -ne 0) {
    Stop-Safely "Git did not run correctly."
}

Write-Host "GitHub CLI:"
& gh --version
if ($LASTEXITCODE -ne 0) {
    Stop-Safely "GitHub CLI did not run correctly."
}

Write-Section "3. CHOOSE AND VERIFY THE TCDOVERLORD GITHUB ACCOUNT"

& gh auth switch --hostname github.com --user $GitHubOwner 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "TCDOVERLORD is not currently available in GitHub CLI." -ForegroundColor Yellow
    Write-Host "A browser login will open. Sign in as TCDOVERLORD." -ForegroundColor Yellow

    & gh auth login --hostname github.com --git-protocol https --web
    if ($LASTEXITCODE -ne 0) {
        Stop-Safely "GitHub login did not complete."
    }

    & gh auth switch --hostname github.com --user $GitHubOwner
    if ($LASTEXITCODE -ne 0) {
        Stop-Safely "GitHub CLI could not switch to TCDOVERLORD."
    }
}

$ActiveLogin = ((@(& gh api user --jq ".login")) -join "").Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($ActiveLogin)) {
    Stop-Safely "The active GitHub account could not be verified."
}

if (-not [string]::Equals(
    $ActiveLogin,
    $GitHubOwner,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    Stop-Safely "Wrong GitHub account is active. Expected TCDOVERLORD but found $ActiveLogin."
}

$GitHubId = ((@(& gh api user --jq ".id")) -join "").Trim()
if ($LASTEXITCODE -ne 0 -or $GitHubId -notmatch "^\d+$") {
    Stop-Safely "The numeric GitHub account ID could not be read."
}

$CommitEmail = "$GitHubId+$GitHubOwner@users.noreply.github.com"

Write-Host "Verified active GitHub account: $ActiveLogin" -ForegroundColor Green
Write-Host "Private commit email: $CommitEmail"

Write-Section "4. MAKE SURE GIT INIT BELONGS TO THIS PROJECT ONLY"

$ExistingRootOutput = @(& git rev-parse --show-toplevel 2>$null)
$ExistingRootExitCode = $LASTEXITCODE

if ($ExistingRootExitCode -eq 0) {
    $ExistingRoot = Get-NormalizedPath -Path (($ExistingRootOutput -join "").Trim())

    if (-not [string]::Equals(
        $ExistingRoot,
        $ResolvedPath,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        Stop-Safely "This folder is currently inside another Git repository: $ExistingRoot"
    }

    Write-Host "This exact project folder is already initialized as a Git repository." -ForegroundColor Green
}
else {
    Write-Host "Initializing Git only inside this exact folder:"
    Write-Host $ResolvedPath -ForegroundColor White

    & git init -b main
    if ($LASTEXITCODE -ne 0) {
        # Fallback for an older Git version that does not support init -b.
        & git init
        if ($LASTEXITCODE -ne 0) {
            Stop-Safely "git init failed."
        }

        & git branch -M main
        if ($LASTEXITCODE -ne 0) {
            Stop-Safely "The main branch could not be created."
        }
    }
}

$VerifiedRootOutput = @(& git rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0) {
    Stop-Safely "Git repository verification failed after initialization."
}

$VerifiedRoot = Get-NormalizedPath -Path (($VerifiedRootOutput -join "").Trim())

if (-not [string]::Equals(
    $VerifiedRoot,
    $ResolvedPath,
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    Stop-Safely "Git root mismatch. Expected $ResolvedPath but found $VerifiedRoot."
}

& git branch -M main
if ($LASTEXITCODE -ne 0) {
    Stop-Safely "The branch could not be named main."
}

# Use local settings so another repository on this computer is not changed.
& git config --local user.name $GitHubOwner
if ($LASTEXITCODE -ne 0) {
    Stop-Safely "The local Git user name could not be configured."
}

& git config --local user.email $CommitEmail
if ($LASTEXITCODE -ne 0) {
    Stop-Safely "The local Git commit email could not be configured."
}

Write-Host "Verified Git root: $VerifiedRoot" -ForegroundColor Green
Write-Host "Local Git author: $(& git config --local user.name)"
Write-Host "Local Git email:  $(& git config --local user.email)"

Write-Section "5. STAGE AND INSPECT THE FIRST COMMIT"

& git add --all
if ($LASTEXITCODE -ne 0) {
    Stop-Safely "Git could not stage the project files."
}

$StagedFiles = @(& git diff --cached --name-only --diff-filter=ACMR)
if ($LASTEXITCODE -ne 0) {
    Stop-Safely "Git could not list the staged files."
}

if ($StagedFiles.Count -eq 0) {
    $HeadCheck = @(& git rev-parse --verify HEAD 2>$null)
    if ($LASTEXITCODE -ne 0) {
        Stop-Safely "There are no files available for the first commit."
    }
}

$BlockedFiles = New-Object System.Collections.Generic.List[string]
$LargeFiles = New-Object System.Collections.Generic.List[string]

foreach ($RelativePath in $StagedFiles) {
    $Normalized = $RelativePath -replace "\\", "/"
    $Block = $false

    if ($Normalized -match "(?i)(^|/)\.env($|\.)") {
        $Block = $true
    }

    if ($Normalized -match "(?i)(^|/)(\.venv|venv|dist|build|build_output)/") {
        $Block = $true
    }

    if (
        $Normalized -match "(?i)(^|/)logs/" -and
        $Normalized -notmatch "(?i)(^|/)logs/\.gitkeep$"
    ) {
        $Block = $true
    }

    if ($Normalized -match "(?i)\.(heic|heif|jpg|jpeg|png|gif|webp|mov|mp4|avi|mkv|exe|msi|zip|7z|rar)$") {
        $Block = $true
    }

    if ($Block) {
        $BlockedFiles.Add($RelativePath)
    }

    $WindowsRelativePath = $RelativePath -replace "/", [System.IO.Path]::DirectorySeparatorChar
    $FullFilePath = Join-Path -Path $ResolvedPath -ChildPath $WindowsRelativePath

    if (Test-Path -LiteralPath $FullFilePath -PathType Leaf) {
        $FileInfo = Get-Item -LiteralPath $FullFilePath
        if ($FileInfo.Length -gt 90MB) {
            $LargeFiles.Add("$RelativePath ($([Math]::Round($FileInfo.Length / 1MB, 2)) MB)")
        }
    }
}

if ($BlockedFiles.Count -gt 0) {
    Write-Host "These staged files may contain private media, secrets, logs, builds, or archives:" -ForegroundColor Red
    $BlockedFiles | ForEach-Object { Write-Host "  $_" }
    Stop-Safely "Remove or ignore these files, then run the script again."
}

if ($LargeFiles.Count -gt 0) {
    Write-Host "These staged files are larger than 90 MB:" -ForegroundColor Red
    $LargeFiles | ForEach-Object { Write-Host "  $_" }
    Stop-Safely "Review large files before publishing."
}

Write-Host "Files prepared for the repository:" -ForegroundColor Green
& git status --short

Write-Host ""
Write-Host "PUBLIC REPOSITORY PLAN" -ForegroundColor Yellow
Write-Host "Owner:       $GitHubOwner"
Write-Host "Repository:  $RepositoryName"
Write-Host "Visibility:  PUBLIC"
Write-Host "Git root:    $VerifiedRoot"
Write-Host "Description: $Description"
Write-Host ""
Write-Host "Type PUBLISH to create the commit and public GitHub repository." -ForegroundColor Yellow

$Confirmation = Read-Host
if ($Confirmation -cne "PUBLISH") {
    Stop-Safely "Nothing was published. The local Git folder remains available."
}

Write-Section "6. CREATE THE FIRST COMMIT"

$HeadExists = $true
& git rev-parse --verify HEAD *> $null
if ($LASTEXITCODE -ne 0) {
    $HeadExists = $false
}

$CurrentlyStaged = @(& git diff --cached --name-only)

if (-not $HeadExists) {
    & git commit -m "feat: publish offline HEIC to JPG converter for Windows"
    if ($LASTEXITCODE -ne 0) {
        Stop-Safely "The first commit failed."
    }
}
elseif ($CurrentlyStaged.Count -gt 0) {
    & git commit -m "docs: prepare GitHub repository for public discovery"
    if ($LASTEXITCODE -ne 0) {
        Stop-Safely "The documentation commit failed."
    }
}
else {
    Write-Host "No new commit was needed." -ForegroundColor Green
}

Write-Section "7. CREATE AND PUSH THE GITHUB REPOSITORY"

$OriginOutput = @(& git remote get-url origin 2>$null)
$OriginExists = ($LASTEXITCODE -eq 0)
$OriginUrl = ""

if ($OriginExists) {
    $OriginUrl = (($OriginOutput -join "").Trim())
}

& gh repo view $RepositoryFullName --json nameWithOwner *> $null
$RemoteRepositoryExists = ($LASTEXITCODE -eq 0)

$ExpectedRemotePattern = "(?i)github\.com[:/]" +
    [regex]::Escape($GitHubOwner) +
    "/" +
    [regex]::Escape($RepositoryName) +
    "(\.git)?$"

if ($OriginExists -and $OriginUrl -notmatch $ExpectedRemotePattern) {
    Stop-Safely "The existing origin points somewhere else: $OriginUrl"
}

if (-not $OriginExists -and -not $RemoteRepositoryExists) {
    & gh repo create $RepositoryFullName `
        --public `
        --source "." `
        --remote origin `
        --push `
        --description $Description `
        --disable-wiki

    if ($LASTEXITCODE -ne 0) {
        Stop-Safely "GitHub repository creation or the first push failed."
    }
}
elseif ($OriginExists -and $RemoteRepositoryExists) {
    Write-Host "The correct GitHub repository and origin already exist." -ForegroundColor Green

    & git push --set-upstream origin main
    if ($LASTEXITCODE -ne 0) {
        Stop-Safely "The push to the existing repository failed."
    }
}
elseif (-not $OriginExists -and $RemoteRepositoryExists) {
    Stop-Safely "The GitHub repository already exists, but this local project has no origin. Review it before connecting."
}
else {
    Stop-Safely "The origin exists, but the expected GitHub repository could not be verified."
}

Write-Section "8. APPLY SEARCH-FRIENDLY REPOSITORY METADATA"

$EditArguments = @(
    "repo",
    "edit",
    $RepositoryFullName,
    "--description",
    $Description,
    "--default-branch",
    "main",
    "--enable-issues=true",
    "--enable-wiki=false"
)

foreach ($Topic in $Topics) {
    $EditArguments += @("--add-topic", $Topic)
}

& gh @EditArguments
if ($LASTEXITCODE -ne 0) {
    Stop-Safely "The repository was pushed, but its description or topics could not be fully applied."
}

Write-Section "REPOSITORY CREATED SUCCESSFULLY"

$FinalActiveLogin = ((@(& gh api user --jq ".login")) -join "").Trim()
$FinalOrigin = ((@(& git remote get-url origin)) -join "").Trim()

Write-Host "GitHub account: $FinalActiveLogin" -ForegroundColor Green
Write-Host "Git root:       $VerifiedRoot" -ForegroundColor Green
Write-Host "Branch:         main" -ForegroundColor Green
Write-Host "Remote:         $FinalOrigin" -ForegroundColor Green
Write-Host "Repository:     https://github.com/$RepositoryFullName" -ForegroundColor Green
Write-Host ""
Write-Host "The repository is public and configured with HEIC, JPG, Windows, iPhone, Python, batch conversion, offline, and privacy topics."
Write-Host "Opening the repository in your browser."

& gh repo view $RepositoryFullName --web

# SIG # Begin signature block
# MIIFggYJKoZIhvcNAQcCoIIFczCCBW8CAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQU5N6s/6/GbcJNZXYyvp0L75NJ
# c0KgggMWMIIDEjCCAfqgAwIBAgIQHMcFXO2KFp1HcmXs+nRW/DANBgkqhkiG9w0B
# AQsFADAhMR8wHQYDVQQDDBZIVi1Db2RlU2lnbi0yMDI2LUdFTjAxMB4XDTI2MDYx
# NzIxNTE1OVoXDTI4MDYxNzIyMDIwMFowITEfMB0GA1UEAwwWSFYtQ29kZVNpZ24t
# MjAyNi1HRU4wMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALV12gWV
# R1hHoSdHbVR5dyp99H5SL+b0VGPyxoZqPLz4GGGSzn3qdxgSEwduofW56UGcHFMF
# N3zI/YNh7tuyEIsLSQXKc1TiwqtD1b0D+XwGKY9Ns0Hc9eSSmCL2Yk7TTNVyMyyH
# P3fbK5aMokWFrSTbZnTmU0+ufcQkQaNygjrR2j3O+JOZyey6XlqV8WKxl5RN76WX
# v2baG0OP6ypswPFabSwrYblCfyfPgIQRtD1VFEG0B0WO3u+Agr9TMdrgDUW+JFPI
# eM06JfOHh2emr8lw/ijNFBojDxLDBnzcKUjbCn24QlC+qsLc3dRKv1JIDWP5DAuF
# PKa7E0h4zucm/LkCAwEAAaNGMEQwDgYDVR0PAQH/BAQDAgeAMBMGA1UdJQQMMAoG
# CCsGAQUFBwMDMB0GA1UdDgQWBBTv7z2lwMtf0vCCeuDDIyD3JiQKkzANBgkqhkiG
# 9w0BAQsFAAOCAQEAAtYpBx4018O+twFqLjZxMjRFPLI9rdN4+9msTd3e0bAmzPFU
# jRQO/8H/PsWNbKcPihugAc66YV8rWtQvDGO1XBy414jdgRzCOXLvrJWrt2N2nmBV
# opWK40pPzIhCC+EX1oX/mEEZVjoyzALXL5S55pygDCqY9n6ccG1qdDZ4Uy30Mz2A
# cAL1e8Try2gejKLJCUFoZErzmK289b2B8F7Howe9h8bekD1xWuUUR3+MGKYqP4Go
# HQ+dn8hpP2v2SslGouppBVs+T3MknKt1pP1f8VGpW53rzKZkxcNxQ/LzJO9gKzON
# mmlY+EWUXaYp9a0+7qCRvosdkf1bcx/y236y7zGCAdYwggHSAgEBMDUwITEfMB0G
# A1UEAwwWSFYtQ29kZVNpZ24tMjAyNi1HRU4wMQIQHMcFXO2KFp1HcmXs+nRW/DAJ
# BgUrDgMCGgUAoHgwGAYKKwYBBAGCNwIBDDEKMAigAoAAoQKAADAZBgkqhkiG9w0B
# CQMxDAYKKwYBBAGCNwIBBDAcBgorBgEEAYI3AgELMQ4wDAYKKwYBBAGCNwIBFTAj
# BgkqhkiG9w0BCQQxFgQUyHqpqPRIYALUSqtMBWTZm6R+CrAwDQYJKoZIhvcNAQEB
# BQAEggEAdFZ51/u88uuiqoAZz9tBxG1mLJjN2Lv0+qvDx1rZ9YcpKwfx91qbBkZJ
# hl68QTklTGC9n7tfwEJjiSo7MyvxCXfjrq6Nu+FsDhDVDqACMiIeTF2lYm/EHH3m
# m5oyTmSp6QcgewhVEtjETDumnNrczqYpscLwcbqyms6cMYkp3x32b8xLiuTiNvwn
# RR5WvyMNwETUsHDF+Td5gFLZkxec1TAo4Ad3a4+OW3Hb4sGVJjGwzc7I7S03P6et
# CQ2nUa+YJAnntgHaCOdqbCh53w71VuqsFb0dmdiFS6J2JzY9t8dWmNGu2B25ndiz
# 8bU/rYPpF4PwEmOZlRllQnN/qISbtg==
# SIG # End signature block

