from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CandidateSelectionResult:
    candidates_path: Path
    report_path: Path
    input_rows: int
    eligible_rows: int
    selected_rows: int
    metric_name: str
    direction: str


def select_candidates(
    registry_path: Path,
    output_dir: Path,
    metric_name: str | None = None,
    top: int = 10,
    direction: str = "auto",
) -> CandidateSelectionResult:
    rows = _read_registry(registry_path)
    eligible = [_normalize_row(row) for row in rows if _is_eligible(row, metric_name)]
    if not eligible:
        raise ValueError("No eligible succeeded rows with numeric metrics")
    selected_metric = metric_name or _first_metric_name(eligible)
    selected_direction = _resolve_direction(selected_metric, direction)
    reverse = selected_direction == "max"
    ranked = sorted(
        [row for row in eligible if row["metric_name"] == selected_metric],
        key=lambda row: float(row["metric_value"]),
        reverse=reverse,
    )
    selected = ranked[:top]

    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_path = output_dir / "model_candidates.csv"
    _write_candidates(candidates_path, selected)
    report_path = output_dir / "candidate_report.md"
    report_path.write_text(
        _format_report(
            registry_path=registry_path,
            input_count=len(rows),
            eligible_count=len(ranked),
            selected=selected,
            metric_name=selected_metric,
            direction=selected_direction,
        ),
        encoding="utf-8",
    )
    return CandidateSelectionResult(
        candidates_path=candidates_path,
        report_path=report_path,
        input_rows=len(rows),
        eligible_rows=len(ranked),
        selected_rows=len(selected),
        metric_name=selected_metric,
        direction=selected_direction,
    )


def _read_registry(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _is_eligible(row: dict[str, str], metric_name: str | None) -> bool:
    if row.get("status") != "succeeded":
        return False
    if metric_name is not None and row.get("metric_name") != metric_name:
        return False
    try:
        float(row.get("metric_value", ""))
    except ValueError:
        return False
    return bool(row.get("metric_name"))


def _normalize_row(row: dict[str, str]) -> dict[str, str]:
    return {key: value for key, value in row.items()}


def _first_metric_name(rows: list[dict[str, str]]) -> str:
    for row in rows:
        metric_name = row.get("metric_name", "")
        if metric_name:
            return metric_name
    raise ValueError("No metric_name found")


def _resolve_direction(metric_name: str, direction: str) -> str:
    if direction not in {"auto", "min", "max"}:
        raise ValueError("direction must be auto, min, or max")
    if direction in {"min", "max"}:
        return direction
    lowered = metric_name.lower()
    if any(token in lowered for token in ["rmse", "mae", "mse", "loss", "error"]):
        return "min"
    return "max"


def _write_candidates(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "rank",
        "task_id",
        "task_type",
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
        "normalization",
        "metric_name",
        "metric_value",
        "checkpoint",
        "task_dir",
        "train_size",
        "val_size",
        "feature_count",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for rank, row in enumerate(rows, start=1):
            output = {field: row.get(field, "") for field in fieldnames}
            output["rank"] = str(rank)
            writer.writerow(output)


def _format_report(
    registry_path: Path,
    input_count: int,
    eligible_count: int,
    selected: list[dict[str, str]],
    metric_name: str,
    direction: str,
) -> str:
    lines = [
        "# Candidate Selection Report",
        "",
        f"- registry: `{registry_path}`",
        f"- input_rows: {input_count}",
        f"- eligible_rows: {eligible_count}",
        f"- selected_rows: {len(selected)}",
        f"- metric_name: `{metric_name}`",
        f"- direction: `{direction}`",
        "",
        "| rank | task_id | task | fold | window | preprocess | model | pooling | metric | value | activation |",
        "|---:|---|---|---:|---|---|---|---|---|---:|---|",
    ]
    for rank, row in enumerate(selected, start=1):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    row.get("task_id", ""),
                    row.get("task", ""),
                    row.get("cv_fold", ""),
                    row.get("window_id", ""),
                    row.get("preprocess_id", ""),
                    row.get("model_id", ""),
                    row.get("pooling_id", ""),
                    row.get("metric_name", ""),
                    row.get("metric_value", ""),
                    row.get("activation", ""),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"
