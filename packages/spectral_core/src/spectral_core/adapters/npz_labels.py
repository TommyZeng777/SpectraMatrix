from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NpzLabelsInspectionResult:
    config_path: Path
    status: str
    sample_count: int
    wavelength_count: int
    split_counts: dict[str, int]
    cv_fold_counts: dict[str, int]
    target_columns: dict[str, str]
    window_count: int
    manifest_path: Path | None
    report_path: Path | None


@dataclass(frozen=True)
class NpzCnn1DTaskResult:
    task_dir: Path
    task_id: str
    run_script: Path
    train_script: Path
    config_path: Path
    manifest_path: Path
    data_path: Path
    dataset_hash: str
    train_size: int
    augmented_train_size: int
    val_size: int
    feature_count: int


def inspect_npz_plus_labels_config(
    config_path: Path,
    output_dir: Path | None = None,
) -> NpzLabelsInspectionResult:
    try:
        import numpy as np
    except ModuleNotFoundError as exc:
        raise RuntimeError("inspect-dataset-config for npz_plus_labels requires numpy") from exc

    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("format") != "npz_plus_labels":
        raise ValueError(f"Unsupported dataset config format: {config.get('format')}")

    base_dir = config_path.parent if config.get("paths_relative_to_this_file", True) else Path.cwd()
    paths = _resolve_required_paths(
        config,
        base_dir,
        ["spectra_matrix", "labels", "split", "cv_folds", "band_windows"],
    )
    if "metadata" in config:
        paths["metadata"] = _resolve_config_path(base_dir, config["metadata"])
        _require_exists(paths["metadata"], "metadata")

    keys = config.get("npz_keys", {})
    x_key = str(keys.get("x", "x"))
    wavelengths_key = str(keys.get("wavelengths", "wavelengths"))
    sample_ids_key = str(keys.get("sample_ids", "sample_ids"))

    npz = np.load(paths["spectra_matrix"], allow_pickle=False)
    missing_npz_keys = [key for key in [x_key, wavelengths_key, sample_ids_key] if key not in npz.files]
    if missing_npz_keys:
        raise ValueError(f"Missing NPZ keys in {paths['spectra_matrix']}: {missing_npz_keys}")

    x = npz[x_key]
    wavelengths = npz[wavelengths_key]
    sample_ids = [str(value) for value in npz[sample_ids_key].tolist()]
    if x.ndim != 2:
        raise ValueError(f"Expected 2D spectra matrix at key {x_key}, got shape {x.shape}")
    if wavelengths.ndim != 1:
        raise ValueError(f"Expected 1D wavelength axis at key {wavelengths_key}, got shape {wavelengths.shape}")
    if len(sample_ids) != x.shape[0]:
        raise ValueError("sample_ids length must match spectra matrix rows")
    if len(wavelengths) != x.shape[1]:
        raise ValueError("wavelengths length must match spectra matrix columns")
    _reject_duplicates(sample_ids, "sample_ids")

    labels = _read_csv(paths["labels"])
    split = _read_csv(paths["split"])
    cv_folds = _read_csv(paths["cv_folds"])
    windows = _read_csv(paths["band_windows"])

    identity = config.get("identity", {})
    row_key = str(identity.get("row_key", "sample_id"))
    group_key = str(identity.get("group_key", "sample_link_code"))
    split_policy = config.get("split_policy", {})
    split_column = str(split_policy.get("split_column", "split"))
    development_value = str(split_policy.get("development_value", "dev"))
    locked_test_value = str(split_policy.get("locked_test_value", "test"))
    cv_fold_column = str(split_policy.get("cv_fold_column", "cv_fold"))

    _require_columns(labels.fieldnames, [row_key, group_key], paths["labels"])
    _require_columns(split.fieldnames, [row_key, group_key, split_column], paths["split"])
    _require_columns(cv_folds.fieldnames, [row_key, group_key, cv_fold_column], paths["cv_folds"])
    _require_columns(windows.fieldnames, ["window_id"], paths["band_windows"])

    labels_ids = _column_values(labels.rows, row_key)
    split_ids = _column_values(split.rows, row_key)
    cv_ids = _column_values(cv_folds.rows, row_key)
    _reject_duplicates(labels_ids, f"{paths['labels']}:{row_key}")
    _reject_duplicates(split_ids, f"{paths['split']}:{row_key}")
    _reject_duplicates(cv_ids, f"{paths['cv_folds']}:{row_key}")

    if labels_ids != sample_ids:
        raise ValueError("sample_id alignment mismatch between NPZ sample_ids and labels")
    if split_ids != sample_ids:
        raise ValueError("sample_id alignment mismatch between NPZ sample_ids and split")

    split_by_id = {row[row_key].strip(): row[split_column].strip() for row in split.rows}
    dev_ids = {sample_id for sample_id, value in split_by_id.items() if value == development_value}
    locked_test_ids = {sample_id for sample_id, value in split_by_id.items() if value == locked_test_value}
    cv_id_set = set(cv_ids)
    if cv_id_set != dev_ids:
        missing = sorted(dev_ids - cv_id_set)
        extra = sorted(cv_id_set - dev_ids)
        raise ValueError(
            "cv_folds sample IDs must match development split sample IDs "
            f"(missing_dev={missing}, extra_cv={extra})"
        )
    leaked_test_ids = sorted(cv_id_set & locked_test_ids)
    if leaked_test_ids:
        raise ValueError(f"Locked test samples found in cv_folds: {leaked_test_ids}")

    target_columns = _target_columns(config)
    _require_columns(labels.fieldnames, _target_required_columns(config), paths["labels"])

    split_counts = _sorted_counter(row[split_column].strip() for row in split.rows)
    cv_fold_counts = _sorted_counter(row[cv_fold_column].strip() for row in cv_folds.rows)
    window_ids = _column_values(windows.rows, "window_id")

    manifest = {
        "status": "ok",
        "config_path": str(config_path),
        "format": "npz_plus_labels",
        "paths": {key: str(value) for key, value in paths.items()},
        "shape": {
            "n_samples": int(x.shape[0]),
            "n_wavelengths": int(x.shape[1]),
        },
        "identity": {
            "row_key": row_key,
            "group_key": group_key,
        },
        "split_policy": {
            "split_column": split_column,
            "development_value": development_value,
            "locked_test_value": locked_test_value,
            "cv_fold_column": cv_fold_column,
        },
        "split_counts": split_counts,
        "cv_fold_counts": cv_fold_counts,
        "target_columns": target_columns,
        "window_count": len(window_ids),
        "window_ids": window_ids,
        "checks": [
            "all referenced files exist",
            "required NPZ keys exist",
            "spectra matrix shape matches sample_ids and wavelengths",
            "labels and split order match NPZ sample_ids",
            "cv_folds sample IDs match development split",
            "locked test samples are excluded from cv_folds",
            "configured target columns exist in labels",
        ],
    }

    manifest_path = None
    report_path = None
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / "dataset_inspection.json"
        report_path = output_dir / "dataset_inspection.md"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report_path.write_text(_format_report(manifest), encoding="utf-8")

    return NpzLabelsInspectionResult(
        config_path=config_path,
        status="ok",
        sample_count=int(x.shape[0]),
        wavelength_count=int(x.shape[1]),
        split_counts=split_counts,
        cv_fold_counts=cv_fold_counts,
        target_columns=target_columns,
        window_count=len(window_ids),
        manifest_path=manifest_path,
        report_path=report_path,
    )


def create_npz_cnn1d_task(
    config_path: Path,
    task_id: str,
    output_dir: Path,
    task: str,
    cv_fold: int,
    window_id: str,
    preprocess_id: str = "raw_standard",
    model_id: str = "cnn3",
    pooling_id: str = "POOL0",
    activation_id: str = "relu",
    dropout: float = 0.2,
    learning_rate: float = 0.001,
    weight_decay: float = 0.0,
    batch_size: int = 32,
    epochs: int = 20,
    seed: int = 42,
    channels: list[int] | None = None,
    kernel_size: int = 5,
    target_transform: str = "linear",
    loss_id: str = "default",
    augmentation_id: str = "AUG0",
    augmentation_multiplier: int = 1,
) -> NpzCnn1DTaskResult:
    try:
        import numpy as np
    except ModuleNotFoundError as exc:
        raise RuntimeError("create-npz-cnn1d-task requires numpy") from exc

    loaded = _load_npz_plus_labels(config_path)
    config = loaded["config"]
    labels = loaded["labels"]
    split = loaded["split"]
    cv_folds = loaded["cv_folds"]
    windows = loaded["windows"]
    x = loaded["x"]
    wavelengths = loaded["wavelengths"]
    sample_ids = loaded["sample_ids"]
    paths = loaded["paths"]
    row_key = loaded["row_key"]
    group_key = loaded["group_key"]
    cv_fold_column = loaded["cv_fold_column"]

    task_spec = _task_spec(config, task)
    target_column = task_spec["column"]
    task_kind = task_spec["kind"]
    metric_name = task_spec["metric_name"]
    higher_is_better = task_spec["higher_is_better"]

    intervals = _window_intervals(windows, window_id)
    feature_mask = _window_mask(np, wavelengths, intervals)
    x_window = x[:, feature_mask].astype(np.float32)
    selected_wavelengths = wavelengths[feature_mask].astype(np.float32)

    id_to_index = {sample_id: index for index, sample_id in enumerate(sample_ids)}
    train_ids = [
        row[row_key].strip()
        for row in cv_folds.rows
        if int(row[cv_fold_column]) != int(cv_fold)
    ]
    val_ids = [
        row[row_key].strip()
        for row in cv_folds.rows
        if int(row[cv_fold_column]) == int(cv_fold)
    ]
    if not train_ids or not val_ids:
        raise ValueError(f"Empty train/val split for cv_fold={cv_fold}")
    train_indices = np.array([id_to_index[sample_id] for sample_id in train_ids], dtype=np.int64)
    val_indices = np.array([id_to_index[sample_id] for sample_id in val_ids], dtype=np.int64)
    augmentation_multiplier = max(1, int(augmentation_multiplier))
    planned_augmented_train_size = int(len(train_indices) * augmentation_multiplier) if augmentation_id != "AUG0" else int(len(train_indices))
    augmentation_method = _augmentation_method_label(augmentation_id)
    augmentation_multiplier_label = _augmentation_multiplier_label(augmentation_id, augmentation_multiplier)

    label_by_id = {row[row_key].strip(): row for row in labels.rows}
    ordered_label_rows = [label_by_id[sample_id] for sample_id in sample_ids]
    y_all = _target_array(np, ordered_label_rows, task_spec)
    label_names = _label_names(np, y_all, task_kind, task_spec)

    task_dir = output_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    _reset_task_outputs(task_dir)
    data_path = task_dir / "task_data.npz"
    np.savez_compressed(
        data_path,
        x_train=x_window[train_indices],
        y_train=y_all[train_indices],
        train_sample_ids=np.array([sample_ids[index] for index in train_indices]),
        train_group_keys=np.array([label_by_id[sample_ids[index]][group_key] for index in train_indices]),
        x_val=x_window[val_indices],
        y_val=y_all[val_indices],
        val_sample_ids=np.array([sample_ids[index] for index in val_indices]),
        val_group_keys=np.array([label_by_id[sample_ids[index]][group_key] for index in val_indices]),
        wavelengths=selected_wavelengths,
        label_names=label_names,
    )
    dataset_hash = _hash_paths([config_path.resolve(), data_path])
    channels = channels or _default_channels(model_id)

    task_config = {
        "task_id": task_id,
        "task_type": "npz_cnn1d_training",
        "dataset_config": str(config_path.resolve()),
        "dataset_hash": dataset_hash,
        "task": task,
        "task_kind": task_kind,
        "target_column": target_column,
        "cv_fold": int(cv_fold),
        "window_id": window_id,
        "preprocess_id": preprocess_id,
        "data_path": str(data_path.resolve()),
        "model": {
            "architecture": "cnn1d_npz",
            "model_id": model_id,
            "pooling_id": pooling_id,
            "activation": activation_id,
            "channels": channels,
            "kernel_size": int(kernel_size),
            "dropout": float(dropout),
        },
        "trainer": {
            "learning_rate": float(learning_rate),
            "weight_decay": float(weight_decay),
            "batch_size": int(batch_size),
            "epochs": int(epochs),
            "seed": int(seed),
        },
        "augmentation": {
            "augmentation_id": augmentation_id,
            "method": augmentation_method,
            "multiplier": augmentation_multiplier,
            "multiplier_label": augmentation_multiplier_label,
            "apply_to": "training_only",
        },
        "objective": {
            "metric_name": metric_name,
            "higher_is_better": bool(higher_is_better),
            "target_transform": target_transform,
            "loss_id": loss_id,
            "target_policy": task_spec["policy"],
        },
    }
    config_out_path = task_dir / "config.json"
    config_out_path.write_text(json.dumps(task_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "task_id": task_id,
        "task_type": "npz_cnn1d_training",
        "dataset_hash": dataset_hash,
        "dataset_config": str(config_path.resolve()),
        "source_paths": {key: str(value) for key, value in paths.items()},
        "task": task,
        "target_column": target_column,
        "target_policy": task_spec["policy"],
        "task_kind": task_kind,
        "cv_fold": int(cv_fold),
        "window_id": window_id,
        "preprocess_id": preprocess_id,
        "architecture": "cnn1d_npz",
        "model_id": model_id,
        "pooling_id": pooling_id,
        "activation": activation_id,
        "channels": channels,
        "kernel_size": int(kernel_size),
        "dropout": float(dropout),
        "augmentation_id": augmentation_id,
        "augmentation_method": augmentation_method,
        "augmentation_multiplier": augmentation_multiplier,
        "augmentation_multiplier_label": augmentation_multiplier_label,
        "loss_id": loss_id,
        "train_size": int(len(train_indices)),
        "augmented_train_size": planned_augmented_train_size,
        "val_size": int(len(val_indices)),
        "feature_count": int(len(selected_wavelengths)),
        "status": "pending",
        "locked_test_policy": config.get("split_policy", {}).get("locked_test_policy", ""),
    }
    manifest_path = task_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (task_dir / "status.json").write_text(json.dumps({"status": "pending"}, indent=2) + "\n", encoding="utf-8")
    train_script = task_dir / "train.py"
    train_script.write_text(_npz_cnn1d_train_source(), encoding="utf-8")
    run_script = task_dir / "run.sh"
    default_python = sys.executable or "python3"
    run_script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"\"${{PYTHON:-{default_python}}}\" train.py\n",
        encoding="utf-8",
    )
    os.chmod(run_script, 0o755)
    (task_dir / "requirements.txt").write_text("torch\nnumpy\n", encoding="utf-8")

    return NpzCnn1DTaskResult(
        task_dir=task_dir,
        task_id=task_id,
        run_script=run_script,
        train_script=train_script,
        config_path=config_out_path,
        manifest_path=manifest_path,
        data_path=data_path,
        dataset_hash=dataset_hash,
        train_size=int(len(train_indices)),
        augmented_train_size=planned_augmented_train_size,
        val_size=int(len(val_indices)),
        feature_count=int(len(selected_wavelengths)),
    )


def _reset_task_outputs(task_dir: Path) -> None:
    for directory_name in ["logs", "checkpoints"]:
        directory = task_dir / directory_name
        if directory.exists():
            shutil.rmtree(directory)
    for filename in ["metrics.csv", "predictions.csv", "summary.json"]:
        path = task_dir / filename
        if path.exists():
            path.unlink()


@dataclass(frozen=True)
class _CsvRows:
    fieldnames: list[str]
    rows: list[dict[str, str]]


def _load_npz_plus_labels(config_path: Path) -> dict[str, Any]:
    try:
        import numpy as np
    except ModuleNotFoundError as exc:
        raise RuntimeError("npz_plus_labels adapter requires numpy") from exc

    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("format") != "npz_plus_labels":
        raise ValueError(f"Unsupported dataset config format: {config.get('format')}")

    base_dir = config_path.parent if config.get("paths_relative_to_this_file", True) else Path.cwd()
    paths = _resolve_required_paths(
        config,
        base_dir,
        ["spectra_matrix", "labels", "split", "cv_folds", "band_windows"],
    )
    if "metadata" in config:
        paths["metadata"] = _resolve_config_path(base_dir, config["metadata"])
        _require_exists(paths["metadata"], "metadata")

    keys = config.get("npz_keys", {})
    x_key = str(keys.get("x", "x"))
    wavelengths_key = str(keys.get("wavelengths", "wavelengths"))
    sample_ids_key = str(keys.get("sample_ids", "sample_ids"))

    npz = np.load(paths["spectra_matrix"], allow_pickle=False)
    missing_npz_keys = [key for key in [x_key, wavelengths_key, sample_ids_key] if key not in npz.files]
    if missing_npz_keys:
        raise ValueError(f"Missing NPZ keys in {paths['spectra_matrix']}: {missing_npz_keys}")

    x = npz[x_key]
    wavelengths = npz[wavelengths_key]
    sample_ids = [str(value) for value in npz[sample_ids_key].tolist()]
    if x.ndim != 2:
        raise ValueError(f"Expected 2D spectra matrix at key {x_key}, got shape {x.shape}")
    if wavelengths.ndim != 1:
        raise ValueError(f"Expected 1D wavelength axis at key {wavelengths_key}, got shape {wavelengths.shape}")
    if len(sample_ids) != x.shape[0]:
        raise ValueError("sample_ids length must match spectra matrix rows")
    if len(wavelengths) != x.shape[1]:
        raise ValueError("wavelengths length must match spectra matrix columns")
    _reject_duplicates(sample_ids, "sample_ids")

    labels = _read_csv(paths["labels"])
    split = _read_csv(paths["split"])
    cv_folds = _read_csv(paths["cv_folds"])
    windows = _read_csv(paths["band_windows"])

    identity = config.get("identity", {})
    row_key = str(identity.get("row_key", "sample_id"))
    group_key = str(identity.get("group_key", "sample_link_code"))
    split_policy = config.get("split_policy", {})
    split_column = str(split_policy.get("split_column", "split"))
    development_value = str(split_policy.get("development_value", "dev"))
    locked_test_value = str(split_policy.get("locked_test_value", "test"))
    cv_fold_column = str(split_policy.get("cv_fold_column", "cv_fold"))

    _require_columns(labels.fieldnames, [row_key, group_key], paths["labels"])
    _require_columns(split.fieldnames, [row_key, group_key, split_column], paths["split"])
    _require_columns(cv_folds.fieldnames, [row_key, group_key, cv_fold_column], paths["cv_folds"])
    _require_columns(windows.fieldnames, ["window_id"], paths["band_windows"])

    labels_ids = _column_values(labels.rows, row_key)
    split_ids = _column_values(split.rows, row_key)
    cv_ids = _column_values(cv_folds.rows, row_key)
    _reject_duplicates(labels_ids, f"{paths['labels']}:{row_key}")
    _reject_duplicates(split_ids, f"{paths['split']}:{row_key}")
    _reject_duplicates(cv_ids, f"{paths['cv_folds']}:{row_key}")

    if labels_ids != sample_ids:
        raise ValueError("sample_id alignment mismatch between NPZ sample_ids and labels")
    if split_ids != sample_ids:
        raise ValueError("sample_id alignment mismatch between NPZ sample_ids and split")

    split_by_id = {row[row_key].strip(): row[split_column].strip() for row in split.rows}
    dev_ids = {sample_id for sample_id, value in split_by_id.items() if value == development_value}
    locked_test_ids = {sample_id for sample_id, value in split_by_id.items() if value == locked_test_value}
    cv_id_set = set(cv_ids)
    if cv_id_set != dev_ids:
        missing = sorted(dev_ids - cv_id_set)
        extra = sorted(cv_id_set - dev_ids)
        raise ValueError(
            "cv_folds sample IDs must match development split sample IDs "
            f"(missing_dev={missing}, extra_cv={extra})"
        )
    leaked_test_ids = sorted(cv_id_set & locked_test_ids)
    if leaked_test_ids:
        raise ValueError(f"Locked test samples found in cv_folds: {leaked_test_ids}")

    return {
        "config_path": config_path,
        "config": config,
        "paths": paths,
        "x": x,
        "wavelengths": wavelengths,
        "sample_ids": sample_ids,
        "labels": labels,
        "split": split,
        "cv_folds": cv_folds,
        "windows": windows,
        "row_key": row_key,
        "group_key": group_key,
        "split_column": split_column,
        "development_value": development_value,
        "locked_test_value": locked_test_value,
        "cv_fold_column": cv_fold_column,
    }


def _resolve_required_paths(config: dict[str, Any], base_dir: Path, names: list[str]) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for name in names:
        if name not in config:
            raise ValueError(f"Missing dataset config path: {name}")
        paths[name] = _resolve_config_path(base_dir, config[name])
        _require_exists(paths[name], name)
    return paths


def _resolve_config_path(base_dir: Path, raw_path: object) -> Path:
    path = Path(str(raw_path))
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _require_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label}: {path}")


def _read_csv(path: Path) -> _CsvRows:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not fieldnames:
        raise ValueError(f"CSV has no header: {path}")
    if not rows:
        raise ValueError(f"CSV has no rows: {path}")
    return _CsvRows(fieldnames=fieldnames, rows=rows)


def _require_columns(fieldnames: list[str], required: list[str], path: Path) -> None:
    missing = [name for name in required if name not in fieldnames]
    if missing:
        raise ValueError(f"Missing columns in {path}: {missing}")


def _column_values(rows: list[dict[str, str]], column: str) -> list[str]:
    return [row.get(column, "").strip() for row in rows]


def _reject_duplicates(values: list[str], label: str) -> None:
    counts = Counter(values)
    duplicates = sorted(value for value, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate values in {label}: {duplicates}")


def _target_columns(config: dict[str, Any]) -> dict[str, str]:
    targets = config.get("targets", {})
    output: dict[str, str] = {}
    for task_name, task_spec in targets.items():
        if not isinstance(task_spec, dict):
            continue
        mode = str(task_spec.get("mode", "use_existing_column"))
        if mode == "derive_from_numeric" and task_spec.get("source_column"):
            output[str(task_name)] = f"derived_from:{task_spec['source_column']}"
        elif task_spec.get("column"):
            output[str(task_name)] = str(task_spec["column"])
    if not output:
        raise ValueError("Dataset config must define at least one target column")
    return output


def _target_required_columns(config: dict[str, Any]) -> list[str]:
    targets = config.get("targets", {})
    required: list[str] = []
    for task_spec in targets.values():
        if not isinstance(task_spec, dict):
            continue
        mode = str(task_spec.get("mode", "use_existing_column"))
        if mode == "derive_from_numeric":
            source_column = str(task_spec.get("source_column", "")).strip()
            if source_column:
                required.append(source_column)
            _validate_bins(task_spec)
        else:
            column = str(task_spec.get("column", "")).strip()
            if column:
                required.append(column)
    return sorted(set(required))


def _sorted_counter(values: object) -> dict[str, int]:
    return {key: count for key, count in sorted(Counter(values).items(), key=lambda item: item[0])}


def _format_report(manifest: dict[str, Any]) -> str:
    split_lines = "\n".join(f"- {key}: {value}" for key, value in manifest["split_counts"].items())
    cv_lines = "\n".join(f"- fold {key}: {value}" for key, value in manifest["cv_fold_counts"].items())
    target_lines = "\n".join(f"- {key}: `{value}`" for key, value in manifest["target_columns"].items())
    return (
        "# Dataset Config Inspection\n\n"
        f"- status: `{manifest['status']}`\n"
        f"- format: `{manifest['format']}`\n"
        f"- samples: {manifest['shape']['n_samples']}\n"
        f"- wavelengths: {manifest['shape']['n_wavelengths']}\n"
        f"- row_key: `{manifest['identity']['row_key']}`\n"
        f"- group_key: `{manifest['identity']['group_key']}`\n"
        f"- window_count: {manifest['window_count']}\n\n"
        "## Split Counts\n\n"
        f"{split_lines}\n\n"
        "## CV Fold Counts\n\n"
        f"{cv_lines}\n\n"
        "## Target Columns\n\n"
        f"{target_lines}\n"
    )


def _task_spec(config: dict[str, Any], task: str) -> dict[str, Any]:
    targets = config.get("targets", {})
    aliases = {
        "ppm": "regression",
        "regression": "regression",
        "binary": "binary",
        "high_risk_gt500": "binary",
        "tri": "tri_class",
        "tri_class": "tri_class",
    }
    target_key = aliases.get(task, task)
    if target_key not in targets or not isinstance(targets[target_key], dict):
        raise ValueError(f"Unknown task target in dataset config: {task}")
    raw = targets[target_key]
    mode = str(raw.get("mode", "use_existing_column"))
    if mode == "derive_from_numeric":
        _validate_bins(raw)
        column = str(raw.get("source_column", "")).strip()
        if not column:
            raise ValueError(f"Missing source_column for derived task: {task}")
    elif mode == "use_existing_column":
        column = str(raw.get("column", "")).strip()
        if not column:
            raise ValueError(f"Missing target column for task: {task}")
    else:
        raise ValueError(f"Unsupported target mode for {task}: {mode}")
    if target_key == "regression":
        task_kind = "regression"
        default_metric = "val_rmse"
        higher_is_better = False
    else:
        task_kind = "classification"
        default_metric = "val_accuracy"
        higher_is_better = True
    return {
        "column": column,
        "kind": task_kind,
        "metric_name": str(raw.get("default_metric", default_metric)),
        "higher_is_better": bool(raw.get("higher_is_better", higher_is_better)),
        "policy": _target_policy(raw, mode, column),
    }


def _window_intervals(windows: _CsvRows, window_id: str) -> list[tuple[float, float]]:
    matches = [row for row in windows.rows if row.get("window_id", "").strip() == str(window_id)]
    if not matches:
        raise ValueError(f"Unknown window_id: {window_id}")
    row = matches[0]
    intervals_raw = row.get("intervals_nm", "").strip()
    if intervals_raw:
        intervals = []
        for item in intervals_raw.split(";"):
            if not item.strip():
                continue
            start_raw, end_raw = item.split("-", 1)
            intervals.append((float(start_raw), float(end_raw)))
        if intervals:
            return intervals
    return [(float(row["start_nm"]), float(row["end_nm"]))]


def _window_mask(np: Any, wavelengths: Any, intervals: list[tuple[float, float]]) -> Any:
    masks = [(wavelengths >= start) & (wavelengths <= end) for start, end in intervals]
    mask = np.logical_or.reduce(masks)
    if not bool(np.any(mask)):
        raise ValueError(f"No wavelengths found for intervals: {intervals}")
    return mask


def _target_array(np: Any, rows: list[dict[str, str]], task_spec: dict[str, Any]) -> Any:
    task_kind = str(task_spec["kind"])
    policy = task_spec["policy"]
    if policy["mode"] == "derive_from_numeric":
        values = [_derive_label(float(row[policy["source_column"]]), policy) for row in rows]
        return np.array(values, dtype=np.int64)
    values = [row[task_spec["column"]] for row in rows]
    if task_kind == "regression":
        return np.array([float(value) for value in values], dtype=np.float32)
    return np.array([int(float(value)) for value in values], dtype=np.int64)


def _label_names(np: Any, y_values: Any, task_kind: str, task_spec: dict[str, Any]) -> Any:
    if task_kind == "regression":
        return np.array([], dtype=str)
    policy = task_spec["policy"]
    if policy["mode"] == "derive_from_numeric":
        names_by_label = {int(item["label"]): str(item["name"]) for item in policy["bins"]}
        max_label = max(names_by_label) if names_by_label else -1
        return np.array([names_by_label.get(index, str(index)) for index in range(max_label + 1)])
    max_label = int(np.max(y_values)) if len(y_values) else -1
    return np.array([str(index) for index in range(max_label + 1)])


def _target_policy(raw: dict[str, Any], mode: str, column: str) -> dict[str, Any]:
    if mode == "derive_from_numeric":
        return {
            "mode": mode,
            "source_column": column,
            "boundary": str(raw.get("boundary", "left_closed_right_open")),
            "bins": [
                {
                    "label": int(item["label"]),
                    "name": str(item.get("name", item["label"])),
                    "min": item.get("min"),
                    "max": item.get("max"),
                }
                for item in raw.get("bins", [])
            ],
        }
    return {"mode": mode, "column": column}


def _validate_bins(raw: dict[str, Any]) -> None:
    bins = raw.get("bins", [])
    if not isinstance(bins, list) or not bins:
        raise ValueError("derive_from_numeric target requires non-empty bins")
    seen_labels: set[int] = set()
    previous_max: float | None = None
    for index, item in enumerate(bins):
        if not isinstance(item, dict):
            raise ValueError("Each bin must be an object")
        if "label" not in item:
            raise ValueError("Each bin must define label")
        label = int(item["label"])
        if label in seen_labels:
            raise ValueError(f"Duplicate derived class label: {label}")
        seen_labels.add(label)
        min_value = _optional_float(item.get("min"))
        max_value = _optional_float(item.get("max"))
        if min_value is None and index != 0:
            raise ValueError("Only the first bin may have min=null")
        if max_value is None and index != len(bins) - 1:
            raise ValueError("Only the last bin may have max=null")
        if min_value is not None and max_value is not None and min_value >= max_value:
            raise ValueError("Bin min must be smaller than max")
        if previous_max is not None and min_value != previous_max:
            raise ValueError("Derived bins must be contiguous")
        previous_max = max_value
    expected_labels = set(range(len(bins)))
    if seen_labels != expected_labels:
        raise ValueError("Derived class labels must be contiguous integers from 0")


def _derive_label(value: float, policy: dict[str, Any]) -> int:
    boundary = str(policy.get("boundary", "left_closed_right_open"))
    for item in policy["bins"]:
        min_value = _optional_float(item.get("min"))
        max_value = _optional_float(item.get("max"))
        left_ok = value >= min_value if min_value is not None else True
        if boundary == "left_closed_right_open":
            right_ok = value < max_value if max_value is not None else True
        elif boundary == "left_open_right_closed":
            left_ok = value > min_value if min_value is not None else True
            right_ok = value <= max_value if max_value is not None else True
        else:
            raise ValueError(f"Unsupported bin boundary: {boundary}")
        if left_ok and right_ok:
            return int(item["label"])
    raise ValueError(f"Value does not fit any derived target bin: {value}")


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)


def _default_channels(model_id: str) -> list[int]:
    if model_id == "cnn3":
        return [16, 32, 64]
    if model_id == "cnn4":
        return [16, 32, 64, 128]
    if model_id == "dilated_cnn4":
        return [16, 32, 64, 128]
    return [16, 32, 64]


def _augmentation_method_label(augmentation_id: str) -> str:
    labels = {
        "AUG0": "不使用数据增强",
        "AUG1": "加噪增强",
        "AUG2": "基线扰动增强",
        "AUG3": "加噪 + 小幅波长位移",
        "AUG4": "组合增强（加噪 + 基线扰动 + 位移）",
    }
    if augmentation_id not in labels:
        raise ValueError(f"Unsupported augmentation_id: {augmentation_id}")
    return labels[augmentation_id]


def _augmentation_multiplier_label(augmentation_id: str, multiplier: int) -> str:
    if augmentation_id == "AUG0":
        return "不扩增"
    return f"{max(1, int(multiplier))}× 训练集扩增"


def _hash_paths(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def _npz_cnn1d_train_source() -> str:
    return r'''from __future__ import annotations

import csv
import json
import random
import time
import traceback
from pathlib import Path


def main() -> int:
    task_dir = Path(__file__).resolve().parent
    try:
        import numpy as np
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except Exception as exc:
        _fail(task_dir, exc)
        return 1

    try:
        config = _read_json(task_dir / "config.json")
        _write_json(task_dir / "status.json", {"status": "running", "started_at": time.time()})
        _set_seed(np, torch, int(config["trainer"]["seed"]))
        data = np.load(Path(config["data_path"]), allow_pickle=False)
        x_train = data["x_train"].astype(np.float32)
        y_train = data["y_train"]
        x_val = data["x_val"].astype(np.float32)
        y_val = data["y_val"]
        val_sample_ids = [str(value) for value in data["val_sample_ids"].tolist()]
        label_names = [str(value) for value in data["label_names"].tolist()]

        x_train, x_val, preprocess_state = _preprocess(np, x_train, x_val, config["preprocess_id"])
        x_train, y_train = _augment_training_data(
            np,
            x_train,
            y_train,
            config.get("augmentation", {}).get("augmentation_id", "AUG0"),
            int(config["trainer"]["seed"]),
            int(config.get("augmentation", {}).get("multiplier", 1)),
        )
        x_train_t = torch.tensor(x_train, dtype=torch.float32).unsqueeze(1)
        x_val_t = torch.tensor(x_val, dtype=torch.float32).unsqueeze(1)
        task_kind = config["task_kind"]
        if task_kind == "classification":
            y_train_t = torch.tensor(y_train, dtype=torch.long)
            y_val_t = torch.tensor(y_val, dtype=torch.long)
            output_dim = int(max(y_train.max(), y_val.max())) + 1
            criterion = _make_loss(nn, task_kind, config["objective"].get("loss_id", "default"))
        else:
            y_train_np = _transform_target(np, y_train.astype(np.float32), config["objective"]["target_transform"])
            y_val_np = _transform_target(np, y_val.astype(np.float32), config["objective"]["target_transform"])
            y_train_t = torch.tensor(y_train_np.reshape(-1, 1), dtype=torch.float32)
            y_val_t = torch.tensor(y_val_np.reshape(-1, 1), dtype=torch.float32)
            output_dim = 1
            criterion = _make_loss(nn, task_kind, config["objective"].get("loss_id", "default"))

        CNN1D = _make_cnn1d_class(torch, nn)
        model = CNN1D(
            input_length=x_train.shape[1],
            output_dim=output_dim,
            channels=list(config["model"]["channels"]),
            kernel_size=int(config["model"]["kernel_size"]),
            dropout=float(config["model"]["dropout"]),
            activation_name=str(config["model"]["activation"]),
            pooling_id=str(config["model"]["pooling_id"]),
        )
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=float(config["trainer"]["learning_rate"]),
            weight_decay=float(config["trainer"].get("weight_decay", 0.0)),
        )
        loader = DataLoader(
            TensorDataset(x_train_t, y_train_t),
            batch_size=int(config["trainer"]["batch_size"]),
            shuffle=True,
        )
        metric_name = str(config["objective"]["metric_name"])
        higher_is_better = bool(config["objective"]["higher_is_better"])
        best_metric = None
        best_state = None
        logs = []
        for epoch in range(1, int(config["trainer"]["epochs"]) + 1):
            model.train()
            total_loss = 0.0
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                output = model(batch_x)
                loss = criterion(output, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += float(loss.item()) * len(batch_x)
            metric_value = _evaluate(np, torch, model, x_val_t, y_val_t, y_val, task_kind, config["objective"]["target_transform"], metric_name)
            logs.append({"epoch": epoch, "train_loss": total_loss / len(x_train_t), metric_name: metric_value})
            if best_metric is None or _is_better(metric_value, best_metric, higher_is_better):
                best_metric = metric_value
                best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}

        (task_dir / "logs").mkdir(exist_ok=True)
        (task_dir / "checkpoints").mkdir(exist_ok=True)
        with (task_dir / "metrics.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["epoch", "train_loss", metric_name])
            writer.writeheader()
            writer.writerows(logs)
        checkpoint_path = task_dir / "checkpoints" / "best.pt"
        torch.save(
            {
                "state_dict": best_state,
                "config": config,
                "preprocess_state": preprocess_state,
                "label_names": label_names,
                "best_metric": best_metric,
            },
            checkpoint_path,
        )
        if best_state is not None:
            model.load_state_dict(best_state)
        predictions_path = _write_predictions(
            np,
            torch,
            task_dir,
            model,
            x_val_t,
            y_val,
            task_kind,
            label_names,
            val_sample_ids,
            config["objective"]["target_transform"],
        )
        summary = {
            "task_id": config["task_id"],
            "status": "succeeded",
            "dataset_hash": config["dataset_hash"],
            "metric_name": metric_name,
            "metric_value": best_metric,
            "checkpoint": str(checkpoint_path),
            "predictions": str(predictions_path),
            "n_train": int(len(x_train)),
            "n_val": int(len(x_val)),
            "n_features": int(x_train.shape[1]),
            "architecture": config["model"]["architecture"],
            "activation": config["model"]["activation"],
            "augmentation_id": config.get("augmentation", {}).get("augmentation_id", "AUG0"),
            "augmentation_method": config.get("augmentation", {}).get("method", ""),
            "augmentation_multiplier": int(config.get("augmentation", {}).get("multiplier", 1)),
            "augmentation_multiplier_label": config.get("augmentation", {}).get("multiplier_label", ""),
            "normalization": "",
        }
        _write_json(task_dir / "summary.json", summary)
        _write_json(task_dir / "status.json", {"status": "succeeded", "finished_at": time.time()})
        return 0
    except Exception as exc:
        _fail(task_dir, exc)
        return 1


def _make_cnn1d_class(torch, nn):
    def activation(name):
        if name == "relu":
            return nn.ReLU()
        if name == "leaky_relu":
            return nn.LeakyReLU()
        if name == "gelu":
            return nn.GELU()
        if name == "silu":
            return nn.SiLU()
        if name == "elu":
            return nn.ELU()
        raise ValueError(f"Unsupported activation: {name}")

    class CNN1D(nn.Module):
        def __init__(self, input_length, output_dim, channels, kernel_size, dropout, activation_name, pooling_id):
            super().__init__()
            layers = []
            in_channels = 1
            dilation = 1
            for out_channels in channels:
                padding = (kernel_size // 2) * dilation
                layers.append(nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, padding=padding, dilation=dilation))
                layers.append(nn.BatchNorm1d(out_channels))
                layers.append(activation(activation_name))
                layers.append(nn.MaxPool1d(kernel_size=2, stride=2))
                in_channels = out_channels
                if pooling_id == "POOL2":
                    dilation = min(dilation * 2, 4)
            self.features = nn.Sequential(*layers)
            with torch.no_grad():
                dummy = torch.zeros(1, 1, input_length)
                z = self.features(dummy)
                pooled_dim = z.shape[1] * (2 if pooling_id == "POOL3" else 1)
            self.pooling_id = pooling_id
            hidden_dim = max(16, min(128, pooled_dim))
            self.head = nn.Sequential(
                nn.Dropout(dropout),
                nn.Linear(pooled_dim, hidden_dim),
                activation(activation_name),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, output_dim),
            )

        def forward(self, x):
            z = self.features(x)
            avg = torch.nn.functional.adaptive_avg_pool1d(z, 1).flatten(1)
            if self.pooling_id == "POOL3":
                mx = torch.nn.functional.adaptive_max_pool1d(z, 1).flatten(1)
                pooled = torch.cat([avg, mx], dim=1)
            else:
                pooled = avg
            return self.head(pooled)

    return CNN1D


def _make_loss(nn, task_kind, loss_id):
    loss_id = str(loss_id or "default").lower()
    if task_kind == "regression":
        if loss_id in {"default", "mse", "mse_loss", "mean_squared_error"}:
            return nn.MSELoss()
        if loss_id in {"smoothl1", "smooth_l1", "huber"}:
            return nn.SmoothL1Loss()
        if loss_id in {"mae", "l1", "l1_loss"}:
            return nn.L1Loss()
        raise ValueError(f"Unsupported regression loss_id: {loss_id}")
    if loss_id in {"default", "cross_entropy", "ce"}:
        return nn.CrossEntropyLoss()
    raise ValueError(f"Unsupported classification loss_id: {loss_id}")


def _augment_training_data(np, x, y, augmentation_id, seed, multiplier):
    augmentation_id = str(augmentation_id or "AUG0")
    multiplier = max(1, int(multiplier or 1))
    if augmentation_id == "AUG0" or multiplier <= 1:
        return x, y
    if augmentation_id not in {"AUG1", "AUG2", "AUG3", "AUG4"}:
        raise ValueError(f"Unsupported augmentation_id: {augmentation_id}")
    rng = np.random.default_rng(seed)
    xs = [x.astype(np.float32)]
    ys = [y.copy()]
    feature_scale = np.std(x, axis=0, keepdims=True)
    feature_scale = np.where(feature_scale > 1e-6, feature_scale, 1.0)
    t = np.linspace(-1.0, 1.0, x.shape[1], dtype=np.float32)[None, :]
    for _ in range(multiplier - 1):
        z = x.copy()
        if augmentation_id in {"AUG1", "AUG3", "AUG4"}:
            z = z + rng.normal(0.0, 0.01, size=z.shape).astype(np.float32) * feature_scale
        if augmentation_id in {"AUG2", "AUG4"}:
            scale = rng.normal(1.0, 0.025, size=(z.shape[0], 1)).astype(np.float32)
            offset = rng.normal(0.0, 0.02, size=(z.shape[0], 1)).astype(np.float32)
            slope = rng.normal(0.0, 0.015, size=(z.shape[0], 1)).astype(np.float32)
            z = z * scale + offset + slope * t
        if augmentation_id in {"AUG3", "AUG4"}:
            z = _tiny_shift(np, z, rng)
        xs.append(z.astype(np.float32))
        ys.append(y.copy())
    return np.vstack(xs).astype(np.float32), np.concatenate(ys)


def _tiny_shift(np, x, rng, max_shift=2):
    out = np.empty_like(x)
    grid = np.arange(x.shape[1])
    for index, row in enumerate(x):
        shift = int(rng.integers(-max_shift, max_shift + 1))
        if shift == 0:
            out[index] = row
        else:
            out[index] = np.interp(grid, grid + shift, row, left=row[0], right=row[-1])
    return out


def _preprocess(np, x_train, x_val, preprocess_id):
    if preprocess_id == "raw_standard":
        return _standardize(np, x_train, x_val)
    if preprocess_id == "snv_standard":
        x_train = _snv(np, x_train)
        x_val = _snv(np, x_val)
        return _standardize(np, x_train, x_val)
    if preprocess_id == "none":
        return x_train, x_val, {"preprocess_id": preprocess_id}
    raise ValueError(f"Unsupported preprocess_id in portable task: {preprocess_id}")


def _standardize(np, x_train, x_val):
    mean = x_train.mean(axis=0, keepdims=True)
    std = x_train.std(axis=0, keepdims=True)
    std = np.where(std < 1e-8, 1.0, std)
    return (x_train - mean) / std, (x_val - mean) / std, {"mean": mean.reshape(-1).tolist(), "std": std.reshape(-1).tolist()}


def _snv(np, x):
    mean = x.mean(axis=1, keepdims=True)
    std = x.std(axis=1, keepdims=True)
    std = np.where(std < 1e-8, 1.0, std)
    return (x - mean) / std


def _transform_target(np, y, transform_id):
    if transform_id == "linear":
        return y
    if transform_id == "log1p":
        return np.log1p(np.clip(y, a_min=0.0, a_max=None)).astype(np.float32)
    if transform_id == "sqrt":
        return np.sqrt(np.clip(y, a_min=0.0, a_max=None)).astype(np.float32)
    raise ValueError(f"Unsupported target_transform: {transform_id}")


def _inverse_target(np, y, transform_id):
    if transform_id == "linear":
        return y
    if transform_id == "log1p":
        return np.expm1(y).astype(np.float32)
    if transform_id == "sqrt":
        return np.square(y).astype(np.float32)
    raise ValueError(f"Unsupported target_transform: {transform_id}")


def _evaluate(np, torch, model, x_val, y_val_t, y_val_raw, task_kind, target_transform, metric_name):
    model.eval()
    with torch.no_grad():
        output = model(x_val)
        if task_kind == "classification":
            predicted = output.argmax(dim=1)
            truth = y_val_t.detach().cpu().numpy()
            pred = predicted.detach().cpu().numpy()
            return _classification_metric(np, truth, pred, metric_name)
        pred = output.reshape(-1).detach().cpu().numpy()
        pred = _inverse_target(np, pred, target_transform)
        truth = y_val_raw.astype(np.float32)
        rmse = float(np.sqrt(np.mean((pred - truth) ** 2)))
        return rmse


def _is_better(value, best, higher_is_better):
    return value > best if higher_is_better else value < best


def _classification_metric(np, truth, pred, metric_name):
    labels = sorted(set(truth.tolist()) | set(pred.tolist()))
    if not labels:
        return 0.0
    if metric_name in {"val_accuracy", "accuracy"}:
        return float(np.mean(pred == truth))
    recalls = []
    precisions = []
    f1_scores = []
    for label in labels:
        tp = float(np.sum((pred == label) & (truth == label)))
        fp = float(np.sum((pred == label) & (truth != label)))
        fn = float(np.sum((pred != label) & (truth == label)))
        support = float(np.sum(truth == label))
        recall = tp / support if support else 0.0
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        f1 = 2.0 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        recalls.append(recall)
        precisions.append(precision)
        f1_scores.append(f1)
    if metric_name in {"val_balanced_accuracy", "balanced_accuracy"}:
        return float(np.mean(recalls))
    if metric_name in {"val_macro_f1", "macro_f1"}:
        return float(np.mean(f1_scores))
    if metric_name in {"val_class1_recall", "class1_recall"}:
        return recalls[labels.index(1)] if 1 in labels else 0.0
    return float(np.mean(pred == truth))


def _write_predictions(np, torch, task_dir, model, x_val, y_val_raw, task_kind, label_names, sample_ids, target_transform):
    path = task_dir / "predictions.csv"
    model.eval()
    with torch.no_grad():
        output = model(x_val)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id", "y_true", "y_pred"])
            writer.writeheader()
            if task_kind == "classification":
                predicted = output.argmax(dim=1).tolist()
                truth = y_val_raw.tolist()
                for sample_id, y_true, y_pred in zip(sample_ids, truth, predicted):
                    y_true_name = label_names[int(y_true)] if label_names else str(y_true)
                    y_pred_name = label_names[int(y_pred)] if label_names else str(y_pred)
                    writer.writerow({"sample_id": sample_id, "y_true": y_true_name, "y_pred": y_pred_name})
            else:
                pred = output.reshape(-1).detach().cpu().numpy()
                pred = _inverse_target(np, pred, target_transform)
                for sample_id, y_true, y_pred in zip(sample_ids, y_val_raw.reshape(-1).tolist(), pred.reshape(-1).tolist()):
                    writer.writerow({"sample_id": sample_id, "y_true": y_true, "y_pred": y_pred})
    return path


def _set_seed(np, torch, seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fail(task_dir, exc):
    (task_dir / "logs").mkdir(exist_ok=True)
    error = {"status": "failed", "error": repr(exc)}
    _write_json(task_dir / "status.json", error)
    (task_dir / "logs" / "error.log").write_text(traceback.format_exc(), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
'''
