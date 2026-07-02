param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

& $Python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e "packages/spectral_core[npz,api]"
& .\.venv\Scripts\python.exe script\generate_sample_csv.py --out datasets\sample_csv

Write-Host ""
Write-Host "SpectraMatrix quickstart is ready."
Write-Host ""
Write-Host "Start the workbench with:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  `$env:PYTHONPATH = 'packages/spectral_core/src'"
Write-Host "  spectral-api"
Write-Host ""
Write-Host "Then open:"
Write-Host "  http://127.0.0.1:8765/"
Write-Host ""
Write-Host "Synthetic CSV files were generated under:"
Write-Host "  datasets\sample_csv\"
