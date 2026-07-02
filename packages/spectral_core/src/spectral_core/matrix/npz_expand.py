from __future__ import annotations

import csv
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spectral_core.adapters import create_npz_cnn1d_task


@dataclass(frozen=True)
class NpzMatrixResult:
    matrix_dir: Path
    tasks_dir: Path
    task_index_path: Path
    manifest_path: Path
    task_count: int


@dataclass(frozen=True)
class NpzMatrixPreview:
    name: str
    description: str
    source_config: Path
    dataset_config: Path
    fixed: dict[str, Any]
    grid: list[dict[str, Any]]
    task_specific_overrides: dict[str, list[dict[str, Any]]]
    total_combinations: int
    formula: str


@dataclass(frozen=True)
class FullFactorialDesignResult:
    config_path: Path
    preview: NpzMatrixPreview


def preview_npz_cnn1d_matrix(config_path: Path) -> NpzMatrixPreview:
    config_path = config_path.resolve()
    config = _load_matrix_config(config_path)
    matrix_name = str(config.get("name", config_path.stem))
    description = str(config.get("description", ""))
    fixed = dict(config.get("fixed", {}))
    grid = dict(config.get("grid", {}))
    task_specific_overrides = dict(config.get("task_specific_overrides", {}))
    dataset_config = _resolve_dataset_config(config, dict(fixed), config_path.parent)
    combinations = _expanded_task_params(dict(fixed), grid, task_specific_overrides)
    grid_summary = _grid_summary(grid)
    override_summary = {
        str(task): _grid_summary(overrides)
        for task, overrides in task_specific_overrides.items()
        if isinstance(overrides, dict)
    }
    return NpzMatrixPreview(
        name=matrix_name,
        description=description,
        source_config=config_path,
        dataset_config=dataset_config,
        fixed=fixed,
        grid=grid_summary,
        task_specific_overrides=override_summary,
        total_combinations=len(combinations),
        formula=_formula_text(grid_summary, override_summary, len(combinations)),
    )


def apply_full_factorial_design(
    base_config_path: Path,
    factors: list[dict[str, Any]],
    output_dir: Path,
    name: str | None = None,
    fixed_overrides: dict[str, Any] | None = None,
) -> FullFactorialDesignResult:
    base_config_path = base_config_path.resolve()
    config = _load_matrix_config(base_config_path)
    source_grid = dict(config.get("grid", {}))
    grid = _normalise_factor_grid(factors)
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = str(config.get("name", base_config_path.stem))
    generated_name = name.strip() if isinstance(name, str) and name.strip() else _generated_design_name(base_name)
    fixed = dict(config.get("fixed", {}))
    fixed.update(dict(fixed_overrides or {}))
    dataset_config = _resolve_dataset_config(config, dict(fixed), base_config_path.parent)
    fixed.pop("dataset_config", None)
    for key in grid:
        fixed.pop(key, None)
    _preserve_required_fixed_values(fixed, grid, source_grid)
    if "cv_fold" not in grid and "cv_fold" not in fixed:
        fixed["cv_fold"] = 1
    dataset_config = _ensure_generated_windows_dataset_config(
        dataset_config,
        _window_values_from_params(fixed, grid),
        output_dir,
    )
    generated = dict(config)
    generated["name"] = generated_name
    generated["status"] = "generated_full_factorial"
    generated["description"] = str(
        config.get("description") or f"Full factorial design generated from {base_config_path.name}."
    )
    generated["dataset_config"] = str(dataset_config)
    generated["fixed"] = fixed
    generated["grid"] = grid
    generated["task_specific_overrides"] = {}
    generated["design"] = {
        "type": "full_factorial",
        "source_config": str(base_config_path),
        "factor_count": len(grid),
        "factor_keys": list(grid.keys()),
    }

    config_path = output_dir / f"{_safe_config_stem(generated_name)}.json"
    config_path.write_text(json.dumps(generated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    preview = preview_npz_cnn1d_matrix(config_path)
    return FullFactorialDesignResult(config_path=config_path, preview=preview)


def _window_values_from_params(fixed: dict[str, Any], grid: dict[str, list[Any]]) -> list[str]:
    values: list[str] = []
    if "window_id" in fixed:
        values.append(str(fixed["window_id"]))
    for value in grid.get("window_id", []):
        values.append(str(value))
    return values


def _ensure_generated_windows_dataset_config(
    dataset_config_path: Path,
    window_ids: list[str],
    output_dir: Path,
) -> Path:
    generated_ids = [window_id for window_id in window_ids if _is_generated_window_id(window_id)]
    needs_full_alias = "WFULL_500_2500" in window_ids
    if not generated_ids and not needs_full_alias:
        return dataset_config_path

    dataset_config_path = dataset_config_path.resolve()
    config = _load_matrix_config(dataset_config_path)
    base_dir = dataset_config_path.parent if config.get("paths_relative_to_this_file", True) else Path.cwd()
    band_windows_path = _resolve_config_path(base_dir, config.get("band_windows"))
    rows, fieldnames = _read_csv_dicts(band_windows_path)
    existing = {str(row.get("window_id", "")).strip() for row in rows}
    start_nm, end_nm = _full_window_bounds(rows)
    added_ids: list[str] = []

    if needs_full_alias and "WFULL_500_2500" not in existing:
        rows.append(
            {
                "window_id": "WFULL_500_2500",
                "start_nm": f"{start_nm:.6g}",
                "end_nm": f"{end_nm:.6g}",
                "intervals_nm": f"{start_nm:.6g}-{end_nm:.6g}",
                "description": "Full spectral window alias for generated training matrix",
            }
        )
        existing.add("WFULL_500_2500")
        added_ids.append("WFULL_500_2500")

    for window_id in generated_ids:
        if window_id in existing:
            continue
        rows.append(_generated_window_row(window_id, start_nm, end_nm))
        existing.add(window_id)
        added_ids.append(window_id)

    if not added_ids:
        return dataset_config_path

    fieldnames = _window_fieldnames(fieldnames)
    generated_windows_path = output_dir / "band_windows.generated.csv"
    with generated_windows_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    generated_config = dict(config)
    for key in ["spectra_matrix", "metadata", "labels", "split", "cv_folds"]:
        if key in generated_config:
            generated_config[key] = str(_resolve_config_path(base_dir, generated_config[key]))
    generated_config["band_windows"] = str(generated_windows_path)
    generated_config["paths_relative_to_this_file"] = False
    generated_config["generated_windows"] = {
        "source_band_windows": str(band_windows_path),
        "window_ids": added_ids,
    }
    generated_config_path = output_dir / "dataset_config.generated_windows.json"
    generated_config_path.write_text(json.dumps(generated_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return generated_config_path


def _is_generated_window_id(window_id: str) -> bool:
    return window_id.startswith("AUTO5_") or window_id.startswith("CUSTOM_")


def _read_csv_dicts(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader], list(reader.fieldnames or [])


def _resolve_config_path(base_dir: Path, raw_path: object) -> Path:
    path = Path(str(raw_path))
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _full_window_bounds(rows: list[dict[str, str]]) -> tuple[float, float]:
    preferred_ids = {"WFULL_500_2500", "W_FULL", "full_spectrum"}
    for row in rows:
        if str(row.get("window_id", "")).strip() in preferred_ids:
            return float(row["start_nm"]), float(row["end_nm"])
    starts = [float(row["start_nm"]) for row in rows if row.get("start_nm")]
    ends = [float(row["end_nm"]) for row in rows if row.get("end_nm")]
    if not starts or not ends:
        raise ValueError("Cannot derive full spectral window bounds from band_windows")
    return min(starts), max(ends)


def _generated_window_row(window_id: str, full_start_nm: float, full_end_nm: float) -> dict[str, str]:
    if window_id.startswith("AUTO5_"):
        index = int(window_id.rsplit("_", 1)[1])
        if index < 1 or index > 5:
            raise ValueError(f"Unsupported auto window id: {window_id}")
        width = (full_end_nm - full_start_nm) / 5.0
        start_nm = full_start_nm + (index - 1) * width
        end_nm = full_end_nm if index == 5 else full_start_nm + index * width
        return {
            "window_id": window_id,
            "start_nm": f"{start_nm:.6g}",
            "end_nm": f"{end_nm:.6g}",
            "intervals_nm": f"{start_nm:.6g}-{end_nm:.6g}",
            "description": f"Auto equal split segment {index}/5 from full spectral window",
        }
    intervals = _custom_window_intervals(window_id)
    start_nm = min(start for start, _end in intervals)
    end_nm = max(end for _start, end in intervals)
    return {
        "window_id": window_id,
        "start_nm": f"{start_nm:.6g}",
        "end_nm": f"{end_nm:.6g}",
        "intervals_nm": ";".join(f"{start:.6g}-{end:.6g}" for start, end in intervals),
        "description": "User custom spectral window",
    }


def _custom_window_intervals(window_id: str) -> list[tuple[float, float]]:
    raw = window_id.removeprefix("CUSTOM_")
    intervals: list[tuple[float, float]] = []
    for item in raw.split("__"):
        start_raw, end_raw = item.split("_", 1)
        start = float(start_raw.replace("p", "."))
        end = float(end_raw.replace("p", "."))
        if end <= start:
            raise ValueError(f"Invalid custom window interval: {item}")
        intervals.append((start, end))
    if not intervals:
        raise ValueError(f"Invalid custom window id: {window_id}")
    return intervals


def _window_fieldnames(fieldnames: list[str]) -> list[str]:
    result = list(fieldnames)
    for key in ["window_id", "start_nm", "end_nm", "intervals_nm", "description"]:
        if key not in result:
            result.append(key)
    return result


def create_npz_cnn1d_matrix(
    config_path: Path,
    output_dir: Path,
    max_tasks: int | None = None,
) -> NpzMatrixResult:
    config_path = config_path.resolve()
    config = _load_matrix_config(config_path)
    matrix_name = str(config.get("name", config_path.stem))
    fixed = dict(config.get("fixed", {}))
    grid = dict(config.get("grid", {}))
    task_specific_overrides = dict(config.get("task_specific_overrides", {}))
    dataset_config = _resolve_dataset_config(config, fixed, config_path.parent)

    matrix_dir = output_dir.resolve()
    tasks_dir = matrix_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    combinations = _expanded_task_params(fixed, grid, task_specific_overrides)
    if max_tasks is not None and len(combinations) > max_tasks:
        raise ValueError(f"Matrix would create {len(combinations)} tasks, above max_tasks={max_tasks}")

    task_rows: list[dict[str, str]] = []
    for index, params in enumerate(combinations, start=1):
        task_id = f"{matrix_name}_task_{index:06d}"
        channels = _coerce_channels(params["channels"]) if "channels" in params else None
        result = create_npz_cnn1d_task(
            config_path=dataset_config,
            task_id=task_id,
            output_dir=tasks_dir,
            task=str(params["task"]),
            cv_fold=int(params["cv_fold"]),
            window_id=str(params["window_id"]),
            preprocess_id=str(params.get("preprocess_id", "raw_standard")),
            model_id=str(params.get("model_id", "cnn3")),
            pooling_id=str(params.get("pooling_id", "POOL0")),
            activation_id=str(params.get("activation_id", "relu")),
            dropout=float(params.get("dropout", 0.2)),
            learning_rate=float(params.get("learning_rate", 0.001)),
            weight_decay=float(params.get("weight_decay", 0.0)),
            batch_size=int(params.get("batch_size", 32)),
            epochs=_int_param(params, "epochs", "max_epochs", default=20),
            seed=int(params.get("seed", 42)),
            channels=channels,
            kernel_size=int(params.get("kernel_size", 5)),
            target_transform=str(params.get("target_transform", "linear")),
            loss_id=str(params.get("loss_id", "default")),
            augmentation_id=str(params.get("augmentation_id", "AUG0")),
            augmentation_multiplier=int(params.get("augmentation_multiplier", 1)),
        )
        task_rows.append(_task_row(task_id, result.task_dir, result, params))

    task_index_path = matrix_dir / "task_index.csv"
    _write_task_index(task_index_path, task_rows)
    manifest = {
        "name": matrix_name,
        "matrix_type": "npz_cnn1d",
        "source_config": str(config_path),
        "dataset_config": str(dataset_config),
        "task_count": len(task_rows),
        "tasks_dir": str(tasks_dir),
        "grid_keys": list(grid.keys()),
        "fixed_keys": list(fixed.keys()),
        "task_specific_override_keys": {
            str(task): list(overrides.keys())
            for task, overrides in task_specific_overrides.items()
            if isinstance(overrides, dict)
        },
    }
    manifest_path = matrix_dir / "matrix_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return NpzMatrixResult(
        matrix_dir=matrix_dir,
        tasks_dir=tasks_dir,
        task_index_path=task_index_path,
        manifest_path=manifest_path,
        task_count=len(task_rows),
    )


def _resolve_dataset_config(config: dict[str, Any], fixed: dict[str, Any], base_dir: Path) -> Path:
    raw_path = fixed.pop("dataset_config", None) or config.get("dataset_config")
    if not raw_path:
        raise ValueError("NPZ matrix config must define dataset_config")
    path = Path(str(raw_path))
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _expanded_task_params(
    fixed: dict[str, Any],
    grid: dict[str, Any],
    task_specific_overrides: dict[str, Any],
) -> list[dict[str, Any]]:
    base_combinations = _expand_grid(grid)
    if not base_combinations:
        base_combinations = [{}]
    rows: list[dict[str, Any]] = []
    for base in base_combinations:
        merged = {**fixed, **base}
        _validate_base_params(merged)
        overrides = task_specific_overrides.get(str(merged["task"]), {})
        if not isinstance(overrides, dict):
            overrides = {}
        override_combinations = _expand_grid(overrides)
        if not override_combinations:
            override_combinations = [{}]
        for override in override_combinations:
            rows.append({**merged, **override})
    return rows


def _validate_base_params(params: dict[str, Any]) -> None:
    required = ["task", "cv_fold", "window_id"]
    missing = [key for key in required if key not in params]
    if missing:
        raise ValueError(f"NPZ matrix config missing required task keys: {missing}")


def _expand_grid(grid: dict[str, Any]) -> list[dict[str, Any]]:
    if not grid:
        return []
    keys = list(grid.keys())
    values = [_ensure_list(grid[key]) for key in keys]
    return [dict(zip(keys, items)) for items in itertools.product(*values)]


def _ensure_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return [value]


def _normalise_factor_grid(factors: list[dict[str, Any]]) -> dict[str, list[Any]]:
    grid: dict[str, list[Any]] = {}
    for index, factor in enumerate(factors, start=1):
        key = str(factor.get("key", "")).strip()
        if not key:
            raise ValueError(f"Factor #{index} is missing a parameter key")
        if key in grid:
            raise ValueError(f"Duplicate factor key: {key}")
        values = factor.get("values")
        if not isinstance(values, list):
            values = _ensure_list(values)
        clean_values = [value for value in values if not (isinstance(value, str) and value.strip() == "")]
        if not clean_values:
            raise ValueError(f"Factor {key} must contain at least one level")
        grid[key] = clean_values
    return grid


def _preserve_required_fixed_values(
    fixed: dict[str, Any],
    grid: dict[str, list[Any]],
    source_grid: dict[str, Any],
) -> None:
    defaults = {
        "task": "ppm",
        "window_id": "WFULL_500_2500",
    }
    for key, default in defaults.items():
        if key in grid or key in fixed:
            continue
        source_values = _ensure_list(source_grid.get(key, [])) if key in source_grid else []
        fixed[key] = source_values[0] if source_values else default


def _generated_design_name(base_name: str) -> str:
    clean = base_name
    suffix = "_full_factorial"
    while clean.endswith(suffix):
        clean = clean[: -len(suffix)]
    return f"{clean or 'matrix'}{suffix}"


def _safe_config_stem(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value.strip())
    safe = safe.strip("._-")
    return safe or "full_factorial_matrix"


def _coerce_channels(value: Any) -> list[int]:
    if isinstance(value, str):
        return [int(part.strip()) for part in value.split(",") if part.strip()]
    if isinstance(value, list):
        return [int(part) for part in value]
    raise ValueError(f"Unsupported channels value: {value!r}")


def _int_param(params: dict[str, Any], primary: str, fallback: str, default: int) -> int:
    if primary in params:
        return int(params[primary])
    if fallback in params:
        return int(params[fallback])
    return default


def _task_row(task_id: str, task_dir: Path, result: Any, params: dict[str, Any]) -> dict[str, str]:
    row = {
        "task_id": task_id,
        "task_dir": str(task_dir),
        "task": str(params["task"]),
        "cv_fold": str(params["cv_fold"]),
        "window_id": str(params["window_id"]),
        "preprocess_id": str(params.get("preprocess_id", "raw_standard")),
        "model_id": str(params.get("model_id", "cnn3")),
        "pooling_id": str(params.get("pooling_id", "POOL0")),
        "activation_id": str(params.get("activation_id", "relu")),
        "channels": _channels_text(params.get("channels")),
        "kernel_size": str(params.get("kernel_size", 5)),
        "dropout": str(params.get("dropout", 0.2)),
        "augmentation_id": str(params.get("augmentation_id", "AUG0")),
        "augmentation_method": str(getattr(result, "augmentation_method", "") or _augmentation_method_label(str(params.get("augmentation_id", "AUG0")))),
        "augmentation_multiplier": str(params.get("augmentation_multiplier", 1)),
        "augmentation_multiplier_label": _augmentation_multiplier_label(
            str(params.get("augmentation_id", "AUG0")),
            int(params.get("augmentation_multiplier", 1)),
        ),
        "learning_rate": str(params.get("learning_rate", 0.001)),
        "weight_decay": str(params.get("weight_decay", 0.0)),
        "batch_size": str(params.get("batch_size", 32)),
        "epochs": str(params.get("epochs", params.get("max_epochs", 20))),
        "seed": str(params.get("seed", 42)),
        "target_transform": str(params.get("target_transform", "linear")),
        "loss_id": str(params.get("loss_id", "default")),
        "train_size": str(result.train_size),
        "augmented_train_size": str(result.augmented_train_size),
        "val_size": str(result.val_size),
        "feature_count": str(result.feature_count),
    }
    for key, value in sorted(params.items()):
        row.setdefault(str(key), str(value))
    return row


def _channels_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "-".join(str(item) for item in value)
    return str(value)


def _write_task_index(path: Path, rows: list[dict[str, str]]) -> None:
    preferred = [
        "task_id",
        "task_dir",
        "task",
        "cv_fold",
        "window_id",
        "preprocess_id",
        "model_id",
        "pooling_id",
        "activation_id",
        "channels",
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
        "target_transform",
        "loss_id",
        "train_size",
        "augmented_train_size",
        "val_size",
        "feature_count",
    ]
    all_keys = sorted({key for row in rows for key in row})
    fieldnames = preferred + [key for key in all_keys if key not in preferred]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_matrix_config(config_path: Path) -> dict[str, Any]:
    return json.loads(config_path.read_text(encoding="utf-8"))


def _augmentation_method_label(augmentation_id: str) -> str:
    labels = {
        "AUG0": "不使用数据增强",
        "AUG1": "加噪增强",
        "AUG2": "基线扰动增强",
        "AUG3": "加噪 + 小幅波长位移",
        "AUG4": "组合增强（加噪 + 基线扰动 + 位移）",
    }
    return labels.get(augmentation_id, augmentation_id)


def _augmentation_multiplier_label(augmentation_id: str, multiplier: int) -> str:
    if augmentation_id == "AUG0":
        return "不扩增"
    return f"{max(1, int(multiplier))}× 训练集扩增"


def _grid_summary(grid: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, raw_values in grid.items():
        values = _ensure_list(raw_values)
        rows.append({"key": str(key), "values": values, "count": len(values)})
    return rows


def _formula_text(
    grid_summary: list[dict[str, Any]],
    override_summary: dict[str, list[dict[str, Any]]],
    total_combinations: int,
) -> str:
    parts = [f"{item['key']}({item['count']})" for item in grid_summary]
    base = " × ".join(parts) if parts else "fixed(1)"
    if override_summary:
        return f"{base}; task-specific overrides => {total_combinations}"
    return base
