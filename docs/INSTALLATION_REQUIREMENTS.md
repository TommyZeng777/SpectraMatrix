# Installation And Environment Requirements

This document lists the runtime requirements for SpectraMatrix.

## Recommended Setup

For most users:

- Python: 3.10 or newer
- Package manager: `pip`
- Environment: Python `venv`
- Operating system:
  - macOS: supported for Python workbench and native launcher
  - Windows: supported for Python/FastAPI workbench; native launcher not included yet
  - Linux: supported for Python/FastAPI workbench

The easiest path is:

```bash
./script/quickstart.sh
```

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\script\quickstart.ps1
```

## Environment Matrix

| Capability | Required packages or tools | Install command | Notes |
| --- | --- | --- | --- |
| Core CLI and file workflow | Python >= 3.10 | `python -m pip install -e packages/spectral_core` | CSV loading, configs, matrix expansion, queue utilities |
| NPZ dataset support | `numpy >= 1.26` | `python -m pip install -e "packages/spectral_core[npz]"` | Needed for NPZ spectral matrix adapters |
| Local browser workbench | `fastapi >= 0.110`, `uvicorn >= 0.27`, plus NPZ support | `python -m pip install -e "packages/spectral_core[npz,api]"` | Recommended install for most users |
| 1D-CNN task training | PyTorch | install the PyTorch build that matches CPU/CUDA/Apple Silicon | Not installed automatically |
| macOS launcher | Swift toolchain / Xcode command line tools | `xcode-select --install` | macOS only |
| Frontend syntax check | Node.js | `node --check packages/spectral_core/src/spectral_core/api/static/app.js` | Development check only |
| GitHub publishing | Git and GitHub CLI | `gh auth login` | Maintainer workflow only |

## Minimal Install

Use this only if you want the CLI and do not need the browser UI:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e packages/spectral_core
```

## Recommended Install

Use this for the local browser workbench:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "packages/spectral_core[npz,api]"
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e "packages/spectral_core[npz,api]"
```

## Start The Workbench

macOS/Linux:

```bash
PYTHONPATH=packages/spectral_core/src spectral-api
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "packages/spectral_core/src"
spectral-api
```

Open:

```text
http://127.0.0.1:8765/
```

## PyTorch Requirement

SpectraMatrix can generate portable 1D-CNN task folders. Those task folders require PyTorch only when you actually run training.

PyTorch is intentionally not a default dependency because each user may need a different build:

- CPU-only
- NVIDIA CUDA
- Apple Silicon
- institutional workstation image

After installing PyTorch, verify it:

```bash
python -c "import torch; print(torch.__version__); print('cuda:', torch.cuda.is_available())"
```

## Configuration Files

Public configuration templates are stored in:

```text
configs/
examples/
CSV导入模板/
```

Machine-specific local paths should not be committed. Use this template only as a guide:

```text
configs/local_paths.example.json
```

Private project files, imported datasets, generated matrices, results, and logs should remain in ignored folders such as:

```text
datasets/
imports/
matrices/
projects/
results/
diagnostics/
logs/
```

## Smoke Test Without Private Data

Generate fake CSV files:

```bash
python script/generate_sample_csv.py --out datasets/sample_csv
```

Then import:

```text
datasets/sample_csv/sample_spectra.csv
datasets/sample_csv/sample_supervision.csv
```

These files are synthetic and ignored by Git.

## Validation Commands

Run Python tests:

```bash
PYTHONPATH=packages/spectral_core/src python -m unittest discover -s packages/spectral_core/tests -v
```

Run frontend JavaScript syntax check:

```bash
node --check packages/spectral_core/src/spectral_core/api/static/app.js
```

Run public tree audit before publishing:

```bash
python script/audit_public_tree.py
```

## Common Problems

### `spectral-api` is not found

Reactivate the environment and reinstall:

```bash
. .venv/bin/activate
python -m pip install -e "packages/spectral_core[npz,api]"
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e "packages/spectral_core[npz,api]"
```

### `ModuleNotFoundError: fastapi`

Install the API extra:

```bash
python -m pip install -e "packages/spectral_core[api]"
```

For the full workbench, prefer:

```bash
python -m pip install -e "packages/spectral_core[npz,api]"
```

### `ModuleNotFoundError: numpy`

Install the NPZ extra:

```bash
python -m pip install -e "packages/spectral_core[npz]"
```

### `ModuleNotFoundError: torch`

Install PyTorch in the same environment that runs the generated task folder.

### Port `8765` is occupied

Use another port:

```bash
PYTHONPATH=packages/spectral_core/src python -m uvicorn \
  spectral_core.api.app:create_app --factory --host 127.0.0.1 --port 8766
```
