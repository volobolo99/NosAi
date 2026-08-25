$ErrorActionPreference = "Stop"

Write-Host "NosAi Local Test Pilot - safe non-live bring-up"

$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) {
    throw "Python launcher 'py' was not found. Install Python 3.10+ and retry."
}

# Use the Python launcher default interpreter instead of hard-coding 3.10.
# The project declares Python >=3.10; this lets an installed compatible
# interpreter (e.g. 3.14) run the pilot without requiring an extra install.
& py -c "import sys; assert sys.version_info >= (3,10), sys.version; print('Using Python', sys.version)"
if ($LASTEXITCODE -ne 0) {
    throw "Python 3.10+ is required."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & py -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the Python virtual environment."
    }
}

$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual-environment Python was not created at $venvPython."
}

function Invoke-PythonStep {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$StepName
    )

    Write-Host ""
    Write-Host "==> $StepName"
    & $venvPython @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$StepName failed with exit code $LASTEXITCODE. See the output above."
    }
}

Invoke-PythonStep -Arguments @("-m", "pip", "install", "--upgrade", "pip") -StepName "Upgrade pip"
Invoke-PythonStep -Arguments @("-m", "pip", "install", "-e", ".[dev]") -StepName "Install NosAi development dependencies"
Invoke-PythonStep -Arguments @("-m", "pytest") -StepName "Run automated tests"
Invoke-PythonStep -Arguments @("-m", "app.preflight") -StepName "Run preflight"
Invoke-PythonStep -Arguments @("-m", "app.pilot.cli", "--cycle", "--ticks", "500") -StepName "Run Test Pilot cycle"

Write-Host ""
Write-Host "NosAi Test Pilot completed successfully."
Write-Host "Artifacts: artifacts\pilot\"
Write-Host "Live game actions are disabled by design."
