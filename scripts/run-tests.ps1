<#
.SYNOPSIS
Runs TWBlue tests with minimal runtime setup.

.DESCRIPTION
This script only executes pytest. It does not install dependencies,
create virtual environments, or initialize submodules.

Use `./scripts/bootstrap-dev.ps1` first to prepare a development environment.

.PARAMETER PytestTargets
One or more pytest target paths/files. Defaults to `src/test`.

.PARAMETER PytestArgs
Additional pytest arguments. Defaults to `-q`.

.PARAMETER SystemPython
Uses a detected system Python instead of `.venv`.

.EXAMPLE
./scripts/run-tests.ps1

.EXAMPLE
./scripts/run-tests.ps1 -PytestTargets src/test/sessions/blueski -PytestArgs "-q"

.EXAMPLE
./scripts/run-tests.ps1 -SystemPython
#>

param(
    [string[]]$PytestTargets = @("src/test"),
    [string[]]$PytestArgs = @("-q"),
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

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not $SystemPython -and -not (Test-Path $venvPython)) {
    throw "No .venv Python found. Run ./scripts/bootstrap-dev.ps1 first, or pass -SystemPython."
}

$python = Get-PythonSpec -RepoRoot $repoRoot -UseSystemPython $SystemPython.IsPresent
Write-Step "Using Python: $($python.Exe) $($python.BaseArgs -join ' ')"

Write-Step "Detecting Python architecture"
$archOutput = & $python.Exe @($python.BaseArgs + @("-c", "import struct; print('x64' if struct.calcsize('P')*8 == 64 else 'x86')"))
if ($LASTEXITCODE -ne 0 -or -not $archOutput) {
    throw "Could not determine Python architecture."
}
$arch = ($archOutput | Select-Object -Last 1).Trim()
if ($arch -ne "x86" -and $arch -ne "x64") {
    throw "Could not determine Python architecture (result: '$arch')."
}

$vlcPath = Join-Path $repoRoot "windows-dependencies\$arch"
if (-not (Test-Path $vlcPath)) {
    throw "Could not find '$vlcPath'. Run ./scripts/bootstrap-dev.ps1 first."
}

$env:PYTHON_VLC_MODULE_PATH = $vlcPath
if (-not ($env:PATH -split ';' | Where-Object { $_ -eq $vlcPath })) {
    $env:PATH = "$vlcPath;$env:PATH"
}

Write-Step "PYTHON_VLC_MODULE_PATH=$($env:PYTHON_VLC_MODULE_PATH)"

Write-Step "Running tests"
$pytestCommandArgs = @("-m", "pytest") + $PytestTargets + $PytestArgs
Invoke-Python -PythonSpec $python -Arguments $pytestCommandArgs -WorkingDirectory $repoRoot
