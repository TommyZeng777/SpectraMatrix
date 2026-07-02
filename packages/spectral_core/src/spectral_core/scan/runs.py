from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScanResult:
    registry_path: Path
    scanned: int
    succeeded: int
    failed: int


def scan_runs(runs_dir: Path, output_dir: Path) -> ScanResult:
    if not runs_dir.exists():
        raise FileNotFoundError(runs_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    scanned = 0
    succeeded = 0
    failed = 0
    for task_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
        manifest_path = task_dir / "manifest.json"
        status_path = task_dir / "status.json"
        summary_path = task_dir / "summary.json"
        config_path = task_dir / "config.json"
        if not manifest_path.exists():
            continue
        scanned += 1
        manifest = _read_json(manifest_path)
        status = _read_json(status_path) if status_path.exists() else {"status": "unknown"}
        summary = _read_json(summary_path) if summary_path.exists() else {}
        config = _read_json(config_path) if config_path.exists() else {}
        current_status = str(summary.get("status") or status.get("status") or manifest.get("status") or "unknown")
        augmentation_id = str(
            _first_value(
                summary.get("augmentation_id"),
                manifest.get("augmentation_id"),
                _nested(config, "augmentation", "augmentation_id"),
                default="AUG0",
            )
        )
        augmentation_multiplier = str(
            _first_value(
                summary.get("augmentation_multiplier"),
                manifest.get("augmentation_multiplier"),
                _nested(config, "augmentation", "multiplier"),
                default="1",
            )
        )
        if current_status == "succeeded":
            succeeded += 1
        elif current_status == "failed":
            failed += 1
        rows.append(
            {
                "task_id": str(manifest.get("task_id", task_dir.name)),
                "task_type": str(manifest.get("task_type", "")),
                "task_dir": str(task_dir),
                "status": current_status,
                "dataset_hash": str(summary.get("dataset_hash") or manifest.get("dataset_hash", "")),
                "task": str(manifest.get("task", "")),
                "cv_fold": str(manifest.get("cv_fold", "")),
                "window_id": str(manifest.get("window_id", "")),
                "preprocess_id": str(manifest.get("preprocess_id", "")),
                "model_id": str(manifest.get("model_id", "")),
                "pooling_id": str(manifest.get("pooling_id", "")),
                "architecture": str(
                    _first_value(summary.get("architecture"), manifest.get("architecture"), _nested(config, "model", "architecture"))
                ),
                "activation": str(
                    _first_value(summary.get("activation"), manifest.get("activation"), _nested(config, "model", "activation"))
                ),
                "kernel_size": str(_first_value(manifest.get("kernel_size"), _nested(config, "model", "kernel_size"))),
                "dropout": str(_first_value(manifest.get("dropout"), _nested(config, "model", "dropout"))),
                "augmentation_id": augmentation_id,
                "augmentation_method": str(
                    _first_value(
                        summary.get("augmentation_method"),
                        manifest.get("augmentation_method"),
                        _nested(config, "augmentation", "method"),
                        default=_augmentation_method_label(augmentation_id),
                    )
                ),
                "augmentation_multiplier": augmentation_multiplier,
                "augmentation_multiplier_label": str(
                    _first_value(
                        summary.get("augmentation_multiplier_label"),
                        manifest.get("augmentation_multiplier_label"),
                        _nested(config, "augmentation", "multiplier_label"),
                        default=_augmentation_multiplier_label(augmentation_id, augmentation_multiplier),
                    )
                ),
                "learning_rate": str(_first_value(manifest.get("learning_rate"), _nested(config, "trainer", "learning_rate"))),
                "weight_decay": str(_first_value(manifest.get("weight_decay"), _nested(config, "trainer", "weight_decay"))),
                "batch_size": str(_first_value(manifest.get("batch_size"), _nested(config, "trainer", "batch_size"))),
                "epochs": str(_first_value(manifest.get("epochs"), _nested(config, "trainer", "epochs"))),
                "seed": str(_first_value(manifest.get("seed"), _nested(config, "trainer", "seed"))),
                "loss_id": str(_first_value(manifest.get("loss_id"), _nested(config, "objective", "loss_id"))),
                "normalization": str(summary.get("normalization") or manifest.get("normalization", "")),
                "metric_name": str(summary.get("metric_name", "")),
                "metric_value": str(summary.get("metric_value", "")),
                "checkpoint": str(summary.get("checkpoint", "")),
                "train_size": str(manifest.get("train_size", "")),
                "augmented_train_size": str(summary.get("n_train") or manifest.get("augmented_train_size", "")),
                "val_size": str(manifest.get("val_size", "")),
                "feature_count": str(manifest.get("feature_count", "")),
            }
        )
    registry_path = output_dir / "run_registry.csv"
    with registry_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "task_id",
            "task_type",
            "task_dir",
            "status",
            "dataset_hash",
            "task",
            "cv_fold",
            "window_id",
            "preprocess_id",
            "model_id",
            "pooling_id",
            "architecture",
            "activation",
            "kernel_size",
            "dropout",
            "augmentation_id",
            "augmentation_method",
            "augmentation_multiplier",
            "augmentation_multiplier_label",
            "learning_rate",
            "weight_decay",
            "batch_size",
            "epochs",
            "seed",
            "loss_id",
            "normalization",
            "metric_name",
            "metric_value",
            "checkpoint",
            "train_size",
            "augmented_train_size",
            "val_size",
            "feature_count",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return ScanResult(registry_path=registry_path, scanned=scanned, succeeded=succeeded, failed=failed)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict, *keys: str) -> object:
    current: object = data
    for key in keys:
        if not isinstance(current, dict):
            return ""
        current = current.get(key, "")
    return current


def _first_value(*values: object, default: object = "") -> object:
    for value in values:
        if value is None:
            continue
        if value == "":
            continue
        return value
    return default


def _augmentation_method_label(augmentation_id: str) -> str:
    labels = {
        "AUG0": "不使用数据增强",
        "AUG1": "加噪增强",
        "AUG2": "基线扰动增强",
        "AUG3": "加噪 + 小幅波长位移",
        "AUG4": "组合增强（加噪 + 基线扰动 + 位移）",
    }
    return labels.get(augmentation_id, augmentation_id)


def _augmentation_multiplier_label(augmentation_id: str, multiplier: str) -> str:
    if augmentation_id == "AUG0":
        return "不扩增"
    try:
        count = max(1, int(float(multiplier)))
    except ValueError:
        count = 1
    return f"{count}× 训练集扩增"
