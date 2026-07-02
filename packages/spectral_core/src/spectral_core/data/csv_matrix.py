from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

from spectral_core.schema import DatasetSpec


@dataclass(frozen=True)
class SpectralDataset:
    sample_ids: list[str]
    feature_names: list[str]
    x: list[list[float]]
    y: list[str]
    rows: list[dict[str, str]]
    source_path: Path
    content_hash: str

    @property
    def n_samples(self) -> int:
        return len(self.sample_ids)

    @property
    def n_features(self) -> int:
        return len(self.feature_names)


def load_csv_matrix(spec: DatasetSpec) -> SpectralDataset:
    if not spec.path.exists():
        raise FileNotFoundError(spec.path)

    raw_bytes = spec.path.read_bytes()
    content_hash = hashlib.sha256(raw_bytes).hexdigest()[:16]

    with spec.path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")
        rows = list(reader)

    if not rows:
        raise ValueError("CSV has no rows")

    fieldnames = list(reader.fieldnames or [])
    required = {spec.sample_id_column, spec.target_column}
    missing = sorted(required - set(fieldnames))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    feature_names = spec.feature_columns or [
        name for name in fieldnames if name not in {spec.sample_id_column, spec.target_column}
    ]
    if not feature_names:
        raise ValueError("No feature columns were found")

    sample_ids: list[str] = []
    targets: list[str] = []
    x: list[list[float]] = []

    for row_index, row in enumerate(rows, start=2):
        sample_id = row.get(spec.sample_id_column, "").strip()
        target = row.get(spec.target_column, "").strip()
        if not sample_id:
            raise ValueError(f"Missing sample id at CSV row {row_index}")
        if not target:
            raise ValueError(f"Missing target at CSV row {row_index}")
        values: list[float] = []
        for column in feature_names:
            raw_value = row.get(column, "").strip()
            if raw_value == "":
                raise ValueError(f"Missing value for {column} at CSV row {row_index}")
            try:
                values.append(float(raw_value))
            except ValueError as exc:
                raise ValueError(f"Non-numeric value for {column} at CSV row {row_index}: {raw_value}") from exc
        sample_ids.append(sample_id)
        targets.append(target)
        x.append(values)

    if len(set(sample_ids)) != len(sample_ids):
        raise ValueError("Sample ids must be unique")

    return SpectralDataset(
        sample_ids=sample_ids,
        feature_names=feature_names,
        x=x,
        y=targets,
        rows=rows,
        source_path=spec.path,
        content_hash=content_hash,
    )

