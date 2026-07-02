from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DummyTaskResult:
    task_dir: Path
    task_id: str
    run_script: Path
    train_script: Path
    manifest_path: Path
    status_path: Path


def create_dummy_task(
    dataset_dir: Path,
    task_id: str,
    output_dir: Path,
    metric_value: float = 0.75,
) -> DummyTaskResult:
    dataset_manifest_path = dataset_dir / "dataset_manifest.json"
    if not dataset_manifest_path.exists():
        raise FileNotFoundError(f"Missing dataset manifest: {dataset_manifest_path}")
    dataset_manifest = json.loads(dataset_manifest_path.read_text(encoding="utf-8"))

    task_dir = output_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "task_id": task_id,
        "task_type": "pipeline_validation",
        "dataset_dir": str(dataset_dir.resolve()),
        "dataset_hash": dataset_manifest["dataset_hash"],
        "metric_value": metric_value,
        "model": {
            "architecture": "dummy_cnn1d_placeholder",
            "activation": "relu",
            "normalization": "batch_norm",
        },
    }
    (task_dir / "config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "task_id": task_id,
        "task_type": "pipeline_validation",
        "dataset_hash": dataset_manifest["dataset_hash"],
        "dataset_dir": str(dataset_dir.resolve()),
        "status": "pending",
    }
    manifest_path = task_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    status_path = task_dir / "status.json"
    status_path.write_text(json.dumps({"status": "pending"}, indent=2) + "\n", encoding="utf-8")
    train_script = task_dir / "train.py"
    train_script.write_text(_dummy_train_source(), encoding="utf-8")
    run_script = task_dir / "run.sh"
    run_script.write_text("#!/usr/bin/env bash\nset -euo pipefail\n\"${PYTHON:-python3}\" train.py\n", encoding="utf-8")
    os.chmod(run_script, 0o755)
    (task_dir / "requirements.txt").write_text("# Dummy task uses Python standard library only.\n", encoding="utf-8")
    return DummyTaskResult(
        task_dir=task_dir,
        task_id=task_id,
        run_script=run_script,
        train_script=train_script,
        manifest_path=manifest_path,
        status_path=status_path,
    )


def _dummy_train_source() -> str:
    return '''from __future__ import annotations

import csv
import json
import time
from pathlib import Path


def main() -> int:
    task_dir = Path(__file__).resolve().parent
    config = json.loads((task_dir / "config.json").read_text(encoding="utf-8"))
    _write_json(task_dir / "status.json", {"status": "running", "started_at": time.time()})
    (task_dir / "logs").mkdir(exist_ok=True)
    (task_dir / "checkpoints").mkdir(exist_ok=True)
    metric_value = float(config.get("metric_value", 0.75))
    with (task_dir / "metrics.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerow({"metric": "val_score", "value": metric_value})
    with (task_dir / "predictions.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample_id", "y_true", "y_pred"])
        writer.writeheader()
        writer.writerow({"sample_id": "SMOKE001", "y_true": "class_a", "y_pred": "class_a"})
    (task_dir / "checkpoints" / "best.ckpt").write_text("dummy checkpoint\\n", encoding="utf-8")
    summary = {
        "task_id": config["task_id"],
        "status": "succeeded",
        "dataset_hash": config["dataset_hash"],
        "metric_name": "val_score",
        "metric_value": metric_value,
        "checkpoint": str(task_dir / "checkpoints" / "best.ckpt"),
    }
    _write_json(task_dir / "summary.json", summary)
    _write_json(task_dir / "status.json", {"status": "succeeded", "finished_at": time.time()})
    return 0


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
'''
