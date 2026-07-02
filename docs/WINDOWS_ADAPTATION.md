# Windows Development Gaps And Adaptation Guide

This document records the current Windows support boundary for SpectraMatrix.

## Current Status

The core Python package and FastAPI workbench are intended to run on Windows, macOS, and Linux.

The macOS launcher is macOS-only because it is implemented with Swift and builds a `.app` bundle. Windows users should start with the Python/FastAPI workflow.

## Recommended Windows Quickstart

Use PowerShell from the repository root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\script\quickstart.ps1
```

Then start the workbench:

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "packages/spectral_core/src"
spectral-api
```

Open:

```text
http://127.0.0.1:8765/
```

## Manual Windows Setup

If the quickstart script is not suitable:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e "packages/spectral_core[npz,api]"
$env:PYTHONPATH = "packages/spectral_core/src"
spectral-api
```

Generate synthetic smoke-test CSV files:

```powershell
python script\generate_sample_csv.py --out datasets\sample_csv
```

## PyTorch On Windows

1D-CNN task folders require PyTorch in the environment that executes `train.py`.

Install the CPU or CUDA build that matches the machine from the official PyTorch selector. After installation:

```powershell
python - <<'PY'
import torch
print(torch.__version__)
print("cuda:", torch.cuda.is_available())
PY
```

If PowerShell does not accept the heredoc syntax above, run:

```powershell
python -c "import torch; print(torch.__version__); print('cuda:', torch.cuda.is_available())"
```

## Known Gaps

- No native Windows launcher is included yet.
- No Windows installer is included yet.
- The macOS `script/build_macos_launcher.sh` path does not apply to Windows.
- Training queue behavior should be tested on real Windows machines before claiming full Windows parity.
- Long paths can still be painful on Windows; keep project folders close to the drive root, for example `C:\work\SpectraMatrix`.
- Non-ASCII paths should work in Python, but ASCII-only paths are still recommended for portable task folders.

## Windows Adaptation Plan

The practical adaptation path is:

1. Keep the Python/FastAPI workflow as the first-class Windows path.
2. Add CI smoke tests on Windows for import, matrix generation, queue dry-run, result scan, and candidate selection.
3. Add a native Windows launcher only after the web workflow stabilizes.
4. Package the launcher with a clear private-data boundary: app code in the installer, user assets outside the installer.
5. Document GPU setup separately for CPU, NVIDIA CUDA, and lab workstation environments.

## Troubleshooting

If `spectral-api` is not recognized, reactivate the environment and reinstall:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e "packages/spectral_core[npz,api]"
```

If port `8765` is occupied:

```powershell
$env:PYTHONPATH = "packages/spectral_core/src"
python -m uvicorn spectral_core.api.app:create_app --factory --host 127.0.0.1 --port 8766
```

If task scripts fail because `run.sh` is not convenient on Windows, run the task directly:

```powershell
python path\to\task_000001\train.py --config path\to\task_000001\config.json
```
