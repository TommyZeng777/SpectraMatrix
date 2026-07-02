# Running SpectraMatrix

This document explains how to prepare a clean open-source checkout, start the local workbench, prepare CSV inputs, generate a training matrix, and run tests.

Recommended GitHub repository name:

```text
SpectraMatrix
```

The public repository should include source code, templates, and small configuration examples. It should not include private laboratory data, generated training tasks, diagnostic logs, local project files, or model outputs.

For the full source/data boundary, read:

```text
docs/DATA_BOUNDARY.md
```

For Windows-specific setup notes, read:

```text
docs/WINDOWS_ADAPTATION.md
```

For a complete dependency matrix, read:

```text
docs/INSTALLATION_REQUIREMENTS.md
```

## 1. Clone And Enter The Project

```bash
git clone https://github.com/<your-account>/SpectraMatrix.git
cd SpectraMatrix
```

If you are publishing from the existing local folder, use this folder as the repository root:

```bash
cd "/path/to/SpectraMatrix"
```

## 2. Create A Python Environment

Fast path on macOS or Linux:

```bash
./script/quickstart.sh
```

Fast path on Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\script\quickstart.ps1
```

Manual setup is below.

Use Python 3.10 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
```

Install SpectraMatrix core with NPZ and API support:

```bash
python -m pip install -e "packages/spectral_core[npz,api]"
```

The generated 1D-CNN task folders use PyTorch. Install the PyTorch build that matches your machine. For CPU-only testing, follow the official PyTorch installation instructions for your platform.

After PyTorch is installed, verify it:

```bash
python - <<'PY'
import torch
print(torch.__version__)
print("cuda:", torch.cuda.is_available())
PY
```

## 3. Start The Local Workbench

Start the FastAPI workbench:

```bash
PYTHONPATH=packages/spectral_core/src spectral-api
```

Open the browser:

```text
http://127.0.0.1:8765/
```

Alternative uvicorn command:

```bash
PYTHONPATH=packages/spectral_core/src python -m uvicorn \
  spectral_core.api.app:create_app --factory --host 127.0.0.1 --port 8765
```

Check that the service is alive:

```bash
curl http://127.0.0.1:8765/health
```

Expected output:

```json
{"status":"ok"}
```

## 4. macOS Launcher

On macOS, the launcher builds a local `.app` that starts the same localhost workbench.

Build and verify:

```bash
./script/build_and_run.sh verify
```

Build only:

```bash
./script/build_macos_launcher.sh build
```

Install to `/Applications`:

```bash
./script/build_macos_launcher.sh install
```

The launcher writes backend logs to:

```text
logs/launcher_backend.log
```

Logs are ignored by Git and should not be published.

The macOS launcher is not the Windows path. Windows users should run the FastAPI workbench directly as described in `docs/WINDOWS_ADAPTATION.md`.

## 5. Prepare CSV Files

The normal import workflow uses two CSV files.

Templates are in:

```text
CSV导入模板/
```

For a first smoke test without private data, generate synthetic CSV files:

```bash
python script/generate_sample_csv.py --out datasets/sample_csv
```

The generated files are fake and ignored by Git.

### 5.1 Spectral Matrix CSV

Required structure:

```csv
sample_id,sample_link_code,500,501,502
sample_001,LC001,0.123,0.124,0.125
sample_002,LC002,0.221,0.219,0.218
```

Rules:

- `sample_id` identifies the row or scan.
- `sample_link_code` connects this row with the supervision CSV.
- Wavelength columns should be numeric column names such as `500`, `501`, `502`.
- Intensity values should be numeric.
- Repeated scans can share a `sample_link_code` when they belong to the same supervised sample.

### 5.2 Supervision CSV

Required structure:

```csv
sample_link_code,ppm_mg_kg
LC001,320
LC002,980
```

Rules:

- `sample_link_code` must match the spectral CSV.
- Target columns should be numeric.
- A regression target can be used directly.
- Binary and three-class targets can be derived from numeric thresholds in the workbench.

## 6. Import Data In The Workbench

1. Open `http://127.0.0.1:8765/`.
2. Go to `Data Import`.
3. Drag the spectral matrix CSV into the spectral file area.
4. Drag the supervision CSV into the supervision file area.
5. Click import/check if the page does not check automatically.
6. Confirm the imported dataset.
7. Enter a training data code, for example:

```text
demo_csv_001
```

The training data code is carried into model design, training, result selection, and outputs so users can see which dataset a matrix belongs to.

## 7. Design A Training Matrix

Go to `Model Training Design`.

Typical steps:

1. Confirm the dataset code shown at the top of the design page.
2. Choose target tasks:
   - regression
   - binary classification
   - three-class classification
3. If classification is selected, set threshold or range rules.
4. Choose data split settings.
5. Choose optional model parameters, such as:
   - spectral window
   - learning rate
   - dropout
   - activation
   - loss function
   - data augmentation method
   - kernel size
   - batch size
   - epoch count
6. The matrix preview shows the current full-factorial task count.
7. Click `Generate Training Matrix` to write runnable task folders.
8. Or click `Export Training Matrix Package` to create a portable training matrix package.

The matrix count is computed from the selected values. You do not need to enter the number of models manually.

## 8. Run Or Resume Training

Go to `Model Training Desk`.

The task grid shows one block per training task. A task can be pending, running, succeeded, failed, or skipped.

Typical controls:

- Run queue: execute pending tasks.
- Stop: interrupt the current queue.
- Resume: continue from existing task status files.
- Rerun failed: run failed tasks again.
- Refresh tasks: reload task states from disk.

Each task folder writes status and metrics files. The queue skips succeeded tasks by default.

## 9. Scan And Select Results

After training:

1. Go to `Result Selection`.
2. Scan the task folder if needed.
3. Choose the metric and ranking direction.
4. Select top candidate models.
5. Open the selected result in `Model Outputs`.

Regression outputs typically use:

- R2
- RMSE
- MAE
- predicted vs measured plots
- residual plots

Classification outputs typically use:

- accuracy
- balanced accuracy
- macro F1
- confusion matrix
- per-class metrics

## 10. CLI Smoke Workflow

The CLI is useful for testing the file workflow without the browser.

Create a matrix from a template:

```bash
PYTHONPATH=packages/spectral_core/src python -m spectral_core.cli.main create-matrix \
  --config examples/matrix_configs/cnn1d_smoke_matrix.json \
  --out matrices/cnn1d_smoke \
  --max-tasks 20
```

Dry-run a queue:

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

Select candidates:

```bash
PYTHONPATH=packages/spectral_core/src python -m spectral_core.cli.main select-candidates \
  --registry results/cnn1d_smoke/run_registry.csv \
  --out results/cnn1d_smoke/candidates \
  --metric val_rmse \
  --top 5
```

Generated `matrices/` and `results/` folders are ignored by Git.

## 11. Run Tests

Run all Python tests:

```bash
PYTHONPATH=packages/spectral_core/src python -m unittest discover -s packages/spectral_core/tests -v
```

Check the browser JavaScript syntax:

```bash
node --check packages/spectral_core/src/spectral_core/api/static/app.js
```

## 12. Open-Source Publishing Checklist

Before pushing to GitHub, inspect what will be committed:

```bash
git status --short
git add -A
git diff --cached --stat
```

Run the public-tree audit:

```bash
python script/audit_public_tree.py
```

Confirm that `LICENSE`, `README.md`, and `ACKNOWLEDGEMENTS.md` are included in the first commit.

Do not publish these folders unless you have manually cleaned and approved them:

```text
datasets/
diagnostics/
examples/**/data/*.csv
imports/
logs/
matrices/
outputs/
projects/
results/
dist/*.app
演示数据集/*.csv
演示数据集/template/*.csv
```

Suggested first commit:

```bash
git init
git add -A
git status --short
git commit -m "Initial open-source release of SpectraMatrix"
```

Create and push a public GitHub repo:

```bash
gh repo create SpectraMatrix --public --source=. --remote=origin --push
```

## 13. Troubleshooting

If `spectral-api` cannot be found, reinstall the package:

```bash
python -m pip install -e "packages/spectral_core[npz,api]"
```

If port `8765` is occupied, stop the old service or run uvicorn on another port:

```bash
PYTHONPATH=packages/spectral_core/src python -m uvicorn \
  spectral_core.api.app:create_app --factory --host 127.0.0.1 --port 8766
```

If generated training tasks fail with `ModuleNotFoundError: torch`, install PyTorch in the environment used to run the task folder.

If browser UI changes do not appear, refresh with a cache-busting query string:

```text
http://127.0.0.1:8765/?bust=local-refresh
```
