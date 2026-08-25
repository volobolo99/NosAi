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
}

$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -e ".[dev]"
& $venvPython -m pytest
& $venvPython -m app.preflight
& $venvPython -m app.pilot.cli --cycle --ticks 500

Write-Host ""
Write-Host "NosAi Test Pilot completed safely."
Write-Host "Artifacts: artifacts\pilot\"
Write-Host "Live game actions are disabled by design."
