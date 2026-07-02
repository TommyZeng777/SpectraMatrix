# SpectraMatrix

BY HKBU MSc GT PHYS7371 Project in Green Technology Group C2

SpectraMatrix is a local, file-based workbench for reproducible spectral modeling experiments. It is designed for small-to-medium laboratory datasets where each sample has a spectral matrix and a supervised measurement table linked by a sample code.

The current focus is deep spectral modeling with 1D-CNN training matrices: import two CSV files, define target tasks and data splits, expand a full-factorial model design, export portable training task folders, run or resume the local queue, scan results, select candidates, and view model outputs.

中文简介：SpectraMatrix 是一个面向光谱实验的本地建模工作台，核心目标是把“光谱矩阵 + 监督数据 + 训练矩阵 + 队列执行 + 结果筛选”做成可复现、可搬走、可继续运行的实验流程。

## Status

This project is in active alpha development. The architecture and core workflow are usable, but APIs, project-file details, and UI wording may still change.

## Public Repository Contents

The public repository is intended to include source code, CSV templates, configuration templates, and documentation only. Real laboratory data, local demo CSV files, generated training matrices, project files, diagnostic logs, and model outputs are excluded by default.

Use `CSV导入模板/` to prepare your own spectral matrix CSV and supervision CSV.

For the detailed source/data boundary, see:

```text
docs/DATA_BOUNDARY.md
```

## What It Does

- Imports wide spectral CSV files and supervision CSV files linked by `sample_link_code`.
- Generates an internal dataset configuration automatically; users do not need to write JSON for normal imports.
- Supports regression, binary classification, and three-class classification tasks derived from numeric supervision values.
- Creates full-factorial training matrices from selected optional parameters.
- Exports portable 1D-CNN task folders with scripts, configs, manifests, and status files.
- Runs local task queues with resume and rerun-failed behavior.
- Scans task outputs into a run registry.
- Selects candidate models by metrics such as RMSE, R2, accuracy, balanced accuracy, or F1.
- Provides a local FastAPI + browser UI workbench.
- Includes a macOS launcher for one-click local startup.

## Why This Project Exists

Many spectral modeling projects start as a set of one-off notebooks and scripts. That becomes fragile when you need to compare many training settings, preserve split rules, avoid leaking independent test data, and resume unfinished training runs.

SpectraMatrix keeps the experiment lifecycle explicit:

1. Import and validate data.
2. Confirm a training dataset code.
3. Design model-training tasks.
4. Generate or export a training matrix.
5. Run tasks locally or move the task folders elsewhere.
6. Scan and rank results.
7. Train or inspect selected model routes.
8. Produce model-output views and reports.

## Repository Layout

```text
.
├── packages/spectral_core/        # Core Python package, CLI, FastAPI app, static workbench UI
├── launcher/                      # macOS Swift launcher source and app assets
├── script/                        # Build and launch helper scripts
├── configs/                       # Shared configuration templates
├── examples/                      # Small examples and project adapters
├── CSV导入模板/                    # CSV import templates
├── docs/                          # Running guide and design notes
├── matrices/                      # Generated training matrices, ignored by default
├── results/                       # Generated result registries and reports, ignored by default
├── imports/                       # Uploaded/imported local data, ignored by default
├── projects/                      # Local workbench project files, ignored by default
└── diagnostics/                   # Local diagnostic logs, ignored by default
```

## Fast Start

For macOS or Linux:

```bash
./script/quickstart.sh
```

For Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\script\quickstart.ps1
```

The quickstart scripts create a local virtual environment, install the editable Python package with API support, and generate a tiny synthetic CSV dataset under `datasets/sample_csv/`. That folder is ignored by Git and contains fake data only.

After quickstart, start the workbench:

```bash
PYTHONPATH=packages/spectral_core/src spectral-api
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "packages/spectral_core/src"
spectral-api
```

Then open `http://127.0.0.1:8765/`.

## Installation

Use Python 3.10 or newer.

```bash
git clone <your-fork-or-repo-url>
cd SpectraMatrix
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "packages/spectral_core[npz,api]"
```

The generated 1D-CNN training tasks require PyTorch in the Python environment that executes those task folders. PyTorch is not installed automatically by the core package because users may need CPU, CUDA, or Apple Silicon-specific builds.

For a more detailed setup and running guide, see:

```text
docs/RUNNING.md
```

For a clear list of required and optional environments, see:

```text
docs/INSTALLATION_REQUIREMENTS.md
```

Windows users should also read:

```text
docs/WINDOWS_ADAPTATION.md
```

## Start The Local Workbench

Run the FastAPI workbench directly:

```bash
PYTHONPATH=packages/spectral_core/src spectral-api
```

Then open:

```text
http://127.0.0.1:8765/
```

You can also launch through uvicorn:

```bash
PYTHONPATH=packages/spectral_core/src python -m uvicorn \
  spectral_core.api.app:create_app --factory --host 127.0.0.1 --port 8765
```

On macOS, the local launcher can be built and run with:

```bash
./script/build_and_run.sh verify
```

To build and install the launcher app:

```bash
./script/build_macos_launcher.sh install
```

## CSV Import Format

The ordinary workflow uses two CSV files.

### Spectral Matrix CSV

Required columns:

- `sample_id`: row-level sample or scan identifier
- `sample_link_code`: code used to join with supervision data
- wavelength columns, for example `500`, `501`, ..., `2500`

Example:

```csv
sample_id,sample_link_code,500,501,502
sample_001,LC001,0.123,0.124,0.125
sample_002,LC002,0.221,0.219,0.218
```

### Supervision CSV

Required columns:

- `sample_link_code`: code used to join with the spectral matrix
- one or more numeric target columns, for example `ppm_mg_kg`

Example:

```csv
sample_link_code,ppm_mg_kg
LC001,320
LC002,980
```

Templates are included in:

```text
CSV导入模板/
```

Real project data and local demo CSV files are intentionally not required for the public repository. Prepare your own two CSV files from the templates, then import them through the workbench.

Template-only files are included in:

```text
CSV导入模板/
```

## Model Training Design

The workbench expands selected optional parameters into a full-factorial training matrix. For example:

```text
task type      regression, binary, three-class
learning rate  0.001, 0.0003
dropout        0.1, 0.2
activation     ReLU, GELU
augmentation   no augmentation, noise, baseline perturbation
```

The total task count is computed from the Cartesian product of selected values. Clicking "Generate Training Matrix" or "Export Training Matrix Package" uses the current selections directly.

Generated matrix folders contain:

```text
matrix_manifest.json
task_index.csv
tasks/
  task_000001/
    config.json
    manifest.json
    run.sh
    train.py
    status.json
```

Each task folder is portable and can be copied to another machine.

## CLI Examples

Install the package first:

```bash
python -m pip install -e "packages/spectral_core[npz,api]"
```

After preparing your own CSV files from `CSV导入模板/`, bind a dataset:

```bash
PYTHONPATH=packages/spectral_core/src python -m spectral_core.cli.main bind-data \
  --spectra path/to/your_spectra.csv \
  --supervision path/to/your_supervision.csv \
  --link-key sample_link_code \
  --target ppm_mg_kg \
  --out datasets/frozen/my_dataset
```

Create a matrix:

```bash
PYTHONPATH=packages/spectral_core/src python -m spectral_core.cli.main create-matrix \
  --config examples/matrix_configs/cnn1d_smoke_matrix.json \
  --out matrices/cnn1d_smoke \
  --max-tasks 20
```

Run a queue:

```bash
PYTHONPATH=packages/spectral_core/src python -m spectral_core.cli.main run-queue \
  --tasks matrices/cnn1d_smoke/tasks \
  --max-tasks 3 \
  --dry-run
```

Scan runs:

```bash
PYTHONPATH=packages/spectral_core/src python -m spectral_core.cli.main scan-runs \
  --runs matrices/cnn1d_smoke/tasks \
  --out results/cnn1d_smoke
```

Select candidate models:

```bash
PYTHONPATH=packages/spectral_core/src python -m spectral_core.cli.main select-candidates \
  --registry results/cnn1d_smoke/run_registry.csv \
  --out results/cnn1d_smoke/candidates \
  --metric val_rmse \
  --top 5
```

## API

The local API is intentionally file-based and localhost-first.

Common endpoints:

- `GET /`
- `GET /health`
- `GET /api/templates/spectra`
- `GET /api/templates/supervision`
- `GET /api/workbench/defaults`
- `POST /api/dataset/import-files`
- `POST /api/dataset/inspect`
- `POST /api/matrix/full-factorial`
- `POST /api/matrix/create-npz`
- `POST /api/queue/start`
- `GET /api/queue/jobs/{job_id}`
- `POST /api/tasks/list`
- `POST /api/tasks/log`
- `POST /api/runs/scan`
- `POST /api/candidates/select`
- `POST /api/matrix/aggregate`
- `POST /api/outputs/summary`
- `POST /api/project/save`
- `POST /api/project/open`

## Testing

Run the test suite:

```bash
PYTHONPATH=packages/spectral_core/src python -m unittest discover -s packages/spectral_core/tests -v
```

Check the browser UI JavaScript syntax:

```bash
node --check packages/spectral_core/src/spectral_core/api/static/app.js
```

## Data And Privacy Notes

SpectraMatrix is designed for local laboratory use. Generated task folders, uploaded datasets, diagnostic logs, project files, and result registries may contain private experiment information. They are ignored by default in `.gitignore`.

Before publishing a repository, review these directories carefully:

```text
imports/
matrices/
results/
projects/
diagnostics/
logs/
outputs/
dist/
```

Before pushing public changes, run:

```bash
python script/audit_public_tree.py
```

This checks Git-tracked files for blocked runtime folders, local absolute paths, private experiment markers, and agent-workspace traces.

## Third-Party Assets

The workbench vendors open-source UI assets so it can run offline:

- Tabler Core CSS, MIT License
- Tabler Icons webfont, MIT License

See:

```text
packages/spectral_core/src/spectral_core/api/static/vendor/README.md
```

## Acknowledgements

SpectraMatrix was designed after studying several open-source project templates and application architecture references. See `ACKNOWLEDGEMENTS.md` for details.

## Roadmap

- Stabilize `.spectramatrix.json` project files.
- Improve final-model training from selected candidate routes.
- Add richer model-output plots and exportable reports.
- Expand model-workshop experiments such as MLP heads or hybrid neural-network modules.
- Add clearer packaging instructions for Windows and Linux.
- Keep PLS and PLS-DA as optional baselines without mixing them into the deep-learning core.

## License

This project is released under the MIT License. See `LICENSE`.
