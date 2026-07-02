from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    experiment_name: str
    dataset_path: str
    dataset_hash: str
    n_samples: int
    n_features: int
    task_kind: str
    target_column: str
    split_id: str
    train_size: int
    test_size: int
    preprocess_steps: list[str]
    model_name: str
    metrics: dict[str, float]


def write_manifest(manifest: RunManifest, run_dir: Path) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "manifest.json"
    path.write_text(
        json.dumps(asdict(manifest), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def write_registry_row(manifest: RunManifest, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "run_registry.csv"
    exists = path.exists()
    row = asdict(manifest)
    row["preprocess_steps"] = "|".join(manifest.preprocess_steps)
    row["metrics"] = json.dumps(manifest.metrics, ensure_ascii=False, sort_keys=True)
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)
    return path

