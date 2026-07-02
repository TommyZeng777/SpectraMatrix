from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetSpec:
    path: Path
    sample_id_column: str = "sample_id"
    target_column: str = "target"
    feature_columns: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], base_dir: Path) -> "DatasetSpec":
        path = Path(data["path"])
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        return cls(
            path=path,
            sample_id_column=data.get("sample_id_column", "sample_id"),
            target_column=data.get("target_column", "target"),
            feature_columns=data.get("feature_columns"),
        )


@dataclass(frozen=True)
class TaskSpec:
    kind: str
    target_column: str
    positive_label: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskSpec":
        kind = data.get("kind", "classification")
        if kind not in {"classification", "regression"}:
            raise ValueError(f"Unsupported task kind: {kind}")
        return cls(
            kind=kind,
            target_column=data["target_column"],
            positive_label=data.get("positive_label"),
        )


@dataclass(frozen=True)
class SplitSpec:
    method: str = "holdout"
    test_size: float = 0.2
    n_splits: int = 5
    stratify: bool = True
    seed: int = 42
    locked_test_column: str | None = None
    locked_test_value: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SplitSpec":
        return cls(
            method=data.get("method", "holdout"),
            test_size=float(data.get("test_size", 0.2)),
            n_splits=int(data.get("n_splits", 5)),
            stratify=bool(data.get("stratify", True)),
            seed=int(data.get("seed", 42)),
            locked_test_column=data.get("locked_test_column"),
            locked_test_value=data.get("locked_test_value"),
        )


@dataclass(frozen=True)
class PreprocessSpec:
    steps: list[str] = field(default_factory=lambda: ["raw"])

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PreprocessSpec":
        steps = data.get("steps", ["raw"])
        if isinstance(steps, str):
            steps = [steps]
        return cls(steps=list(steps))


@dataclass(frozen=True)
class ModelSpec:
    name: str
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelSpec":
        return cls(name=data.get("name", "nearest_centroid"), params=data.get("params", {}))


@dataclass(frozen=True)
class ExperimentSpec:
    name: str
    dataset: DatasetSpec
    task: TaskSpec
    split: SplitSpec
    preprocess: PreprocessSpec
    model: ModelSpec
    output_dir: Path

    @classmethod
    def from_dict(cls, data: dict[str, Any], config_path: Path) -> "ExperimentSpec":
        base_dir = config_path.parent
        output_dir = Path(data.get("output_dir", "outputs"))
        if not output_dir.is_absolute():
            output_dir = (base_dir / output_dir).resolve()
        return cls(
            name=data.get("name", config_path.stem),
            dataset=DatasetSpec.from_dict(data["dataset"], base_dir),
            task=TaskSpec.from_dict(data["task"]),
            split=SplitSpec.from_dict(data.get("split", {})),
            preprocess=PreprocessSpec.from_dict(data.get("preprocess", {})),
            model=ModelSpec.from_dict(data.get("model", {})),
            output_dir=output_dir,
        )

