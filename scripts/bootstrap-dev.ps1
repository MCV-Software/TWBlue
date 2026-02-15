<#
.SYNOPSIS
Bootstraps a local TWBlue development environment on Windows.

.DESCRIPTION
This script initializes git submodules, creates/uses a virtual environment,
and installs Python dependencies from requirements.txt.
It is intended to be run once when starting on the repository (or whenever
you need to rebuild your local environment).

.PARAMETER RecreateVenv
Deletes and recreates the `.venv` folder before installing dependencies.

.PARAMETER UpgradePip
Upgrades `pip`, `setuptools`, and `wheel` before installing requirements.

.PARAMETER SkipSubmodules
Skips `git submodule init` and `git submodule update --recursive`.

.PARAMETER SystemPython
Uses a detected system Python instead of creating/using `.venv`.

.EXAMPLE
./scripts/bootstrap-dev.ps1

.EXAMPLE
./scripts/bootstrap-dev.ps1 -RecreateVenv -UpgradePip

.EXAMPLE
./scripts/bootstrap-dev.ps1 -SystemPython -SkipSubmodules
#>

param(
    [switch]$RecreateVenv,
    [switch]$UpgradePip,
    [switch]$SkipSubmodules,
    [switch]$SystemPython
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Resolve-RepoRoot {
    param([string]$ScriptDir)
    return (Resolve-Path (Join-Path $ScriptDir "..")).Path
}

function Test-PythonCandidate {
    param(
        [string]$Exe,
        [string[]]$BaseArgs = @()
    )

    try {
        & $Exe @BaseArgs -c "import sys; print(sys.version)" | Out-Null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

function New-PythonSpec {
    param(
        [string]$Exe,
        [string[]]$BaseArgs = @()
    )

    return [pscustomobject]@{
        Exe = $Exe
        BaseArgs = $BaseArgs
    }
}

function Get-PythonSpec {
    param([string]$RepoRoot, [bool]$UseSystemPython)

    if (-not $UseSystemPython) {
        $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
        if (Test-Path $venvPython) {
            return (New-PythonSpec -Exe $venvPython)
        }
    }

    $candidates = @()

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $candidates += ,(New-PythonSpec -Exe "python")
    }

    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        $candidates += ,(New-PythonSpec -Exe "py" -BaseArgs @("-3.10"))
        $candidates += ,(New-PythonSpec -Exe "py" -BaseArgs @("-3"))
    }

    foreach ($candidate in $candidates) {
        if (Test-PythonCandidate -Exe $candidate.Exe -BaseArgs $candidate.BaseArgs) {
            return $candidate
        }
    }

    throw "Could not find a usable Python. Install Python 3.10+ and try again."
}

function Invoke-Python {
    param(
        [pscustomobject]$PythonSpec,
        [string[]]$Arguments,
        [string]$WorkingDirectory
    )

    Push-Location $WorkingDirectory
    try {
        & $PythonSpec.Exe @($PythonSpec.BaseArgs + $Arguments)
        if ($LASTEXITCODE -ne 0) {
            throw "Python command failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-RepoRoot -ScriptDir $scriptDir

Write-Step "Repository: $repoRoot"

if (-not $SkipSubmodules) {
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd) {
        Write-Step "Initializing/updating submodules"
        Push-Location $repoRoot
        try {
            & git submodule init | Out-Host
            & git submodule update --recursive | Out-Host
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Warning "Git is not available. Skipping submodule initialization."
    }
}

$venvPath = Join-Path $repoRoot ".venv"
if ($RecreateVenv -and (Test-Path $venvPath)) {
    Write-Step "Removing existing virtual environment"
    Remove-Item -Recurse -Force $venvPath
}

if (-not $SystemPython -and -not (Test-Path (Join-Path $venvPath "Scripts\python.exe"))) {
    Write-Step "Creating virtual environment in .venv"
    $bootstrapPython = Get-PythonSpec -RepoRoot $repoRoot -UseSystemPython $true
    Invoke-Python -PythonSpec $bootstrapPython -Arguments @("-m", "venv", ".venv") -WorkingDirectory $repoRoot
}

$python = Get-PythonSpec -RepoRoot $repoRoot -UseSystemPython $SystemPython.IsPresent
Write-Step "Using Python: $($python.Exe) $($python.BaseArgs -join ' ')"

if ($UpgradePip) {
    Write-Step "Upgrading pip/setuptools/wheel"
    Invoke-Python -PythonSpec $python -Arguments @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel") -WorkingDirectory $repoRoot
}

Write-Step "Installing dependencies"
Invoke-Python -PythonSpec $python -Arguments @("-m", "pip", "install", "-r", "requirements.txt") -WorkingDirectory $repoRoot

Write-Step "Bootstrap completed"
