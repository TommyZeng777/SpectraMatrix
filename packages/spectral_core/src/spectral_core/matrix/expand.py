from __future__ import annotations

import csv
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spectral_core.tasks import create_cnn1d_task


@dataclass(frozen=True)
class MatrixResult:
    matrix_dir: Path
    tasks_dir: Path
    task_index_path: Path
    manifest_path: Path
    task_count: int


def create_cnn1d_matrix(
    config_path: Path,
    output_dir: Path,
    max_tasks: int | None = None,
) -> MatrixResult:
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    fixed = dict(config.get("fixed", {}))
    grid = dict(config.get("grid", {}))
    matrix_name = config.get("name", config_path.stem)
    matrix_dir = output_dir.resolve()
    tasks_dir = matrix_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    _validate_fixed(fixed)
    combinations = _expand_grid(grid)
    if max_tasks is not None and len(combinations) > max_tasks:
        raise ValueError(f"Matrix would create {len(combinations)} tasks, above max_tasks={max_tasks}")

    task_rows: list[dict[str, str]] = []
    for index, params in enumerate(combinations, start=1):
        merged = {**fixed, **params}
        task_id = f"{matrix_name}_task_{index:06d}"
        channels = _coerce_channels(merged.get("channels", [16, 32, 64]))
        result = create_cnn1d_task(
            dataset_dir=Path(merged["dataset_dir"]).resolve(),
            task_id=task_id,
            output_dir=tasks_dir,
            target_column=str(merged["target_column"]),
            task_kind=str(merged["task_kind"]),
            feature_prefix=str(merged.get("feature_prefix", "w")),
            activation=str(merged.get("activation", "relu")),
            normalization=str(merged.get("normalization", "batch_norm")),
            channels=channels,
            kernel_size=int(merged.get("kernel_size", 5)),
            dropout=float(merged.get("dropout", 0.2)),
            learning_rate=float(merged.get("learning_rate", 0.001)),
            batch_size=int(merged.get("batch_size", 16)),
            epochs=int(merged.get("epochs", 20)),
            seed=int(merged.get("seed", 42)),
        )
        task_rows.append(_task_row(task_id, result.task_dir, merged, channels))

    task_index_path = matrix_dir / "task_index.csv"
    _write_task_index(task_index_path, task_rows)
    manifest = {
        "name": matrix_name,
        "source_config": str(config_path),
        "task_count": len(task_rows),
        "tasks_dir": str(tasks_dir),
        "grid_keys": list(grid.keys()),
        "fixed_keys": list(fixed.keys()),
    }
    manifest_path = matrix_dir / "matrix_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return MatrixResult(
        matrix_dir=matrix_dir,
        tasks_dir=tasks_dir,
        task_index_path=task_index_path,
        manifest_path=manifest_path,
        task_count=len(task_rows),
    )


def _validate_fixed(fixed: dict[str, Any]) -> None:
    required = ["dataset_dir", "target_column", "task_kind"]
    missing = [key for key in required if key not in fixed]
    if missing:
        raise ValueError(f"Matrix fixed config missing required keys: {missing}")


def _expand_grid(grid: dict[str, Any]) -> list[dict[str, Any]]:
    if not grid:
        return [{}]
    keys = list(grid.keys())
    values = [_ensure_list(grid[key]) for key in keys]
    combinations: list[dict[str, Any]] = []
    for items in itertools.product(*values):
        combinations.append(dict(zip(keys, items)))
    return combinations


def _ensure_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return [value]


def _coerce_channels(value: Any) -> list[int]:
    if isinstance(value, str):
        return [int(part.strip()) for part in value.split(",") if part.strip()]
    if isinstance(value, list):
        return [int(part) for part in value]
    raise ValueError(f"Unsupported channels value: {value!r}")


def _task_row(task_id: str, task_dir: Path, params: dict[str, Any], channels: list[int]) -> dict[str, str]:
    return {
        "task_id": task_id,
        "task_dir": str(task_dir),
        "task_kind": str(params["task_kind"]),
        "target_column": str(params["target_column"]),
        "feature_prefix": str(params.get("feature_prefix", "w")),
        "activation": str(params.get("activation", "relu")),
        "normalization": str(params.get("normalization", "batch_norm")),
        "channels": "-".join(str(value) for value in channels),
        "kernel_size": str(params.get("kernel_size", 5)),
        "dropout": str(params.get("dropout", 0.2)),
        "learning_rate": str(params.get("learning_rate", 0.001)),
        "batch_size": str(params.get("batch_size", 16)),
        "epochs": str(params.get("epochs", 20)),
        "seed": str(params.get("seed", 42)),
    }


def _write_task_index(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "task_id",
        "task_dir",
        "task_kind",
        "target_column",
        "feature_prefix",
        "activation",
        "normalization",
        "channels",
        "kernel_size",
        "dropout",
        "learning_rate",
        "batch_size",
        "epochs",
        "seed",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

