$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

function Find-Python {
    $candidates = @(
        "$ProjectRoot\venv\Scripts\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
    )
    foreach ($path in $candidates) {
        if (Test-Path $path) { return $path }
    }
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notlike "*WindowsApps*") { return $cmd.Source }
    return $null
}

function Ensure-Venv {
    param([string]$PythonExe)
    $venvPython = "$ProjectRoot\venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        try {
            & $venvPython -c "import fastapi, uvicorn" 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { return $venvPython }
        } catch {}
        Write-Host "Recreating broken virtual environment..."
        Remove-Item -Recurse -Force "$ProjectRoot\venv" -ErrorAction SilentlyContinue
    }
    Write-Host "Creating virtual environment..."
    & $PythonExe -m venv "$ProjectRoot\venv"
    & "$ProjectRoot\venv\Scripts\python.exe" -m pip install --upgrade pip
    & "$ProjectRoot\venv\Scripts\pip.exe" install -r "$ProjectRoot\requirements.txt"
    return "$ProjectRoot\venv\Scripts\python.exe"
}

$python = Find-Python
if (-not $python) {
    Write-Host "Python 3.10+ is required."
    Write-Host "Install from https://www.python.org/downloads/ then run this script again."
    exit 1
}

$venvPython = Ensure-Venv -PythonExe $python

Write-Host "Initializing database..."
& $venvPython "$ProjectRoot\backend\create_database.py"

Write-Host "Starting API on http://127.0.0.1:8000"
Start-Process -FilePath $venvPython `
    -ArgumentList "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000", "--reload" `
    -WorkingDirectory "$ProjectRoot\backend"

Start-Sleep -Seconds 2

Push-Location "$ProjectRoot\dashboard"
if (-not (Test-Path node_modules)) {
    Write-Host "Installing dashboard dependencies..."
    npm install
}
Write-Host "Starting dashboard on http://localhost:5173"
npm run dev
Pop-Location
