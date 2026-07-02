from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MatrixAggregateResult:
    summary_path: Path
    details_path: Path
    report_path: Path
    input_rows: int
    eligible_rows: int
    group_count: int
    metric_name: str
    direction: str
    group_by: list[str]


def aggregate_matrix_results(
    registry_path: Path,
    output_dir: Path,
    metric_name: str | None = None,
    group_by: list[str] | None = None,
    direction: str = "auto",
) -> MatrixAggregateResult:
    rows = _read_csv(registry_path)
    selected_metric = metric_name or _first_metric_name(rows)
    selected_direction = _resolve_direction(selected_metric, direction)
    groups = group_by or ["window_id", "activation"]
    eligible = [_normalize_row(row) for row in rows if _is_eligible(row, selected_metric)]
    if not eligible:
        raise ValueError("No eligible succeeded rows with numeric metrics")
    for field in groups:
        if field not in eligible[0]:
            raise ValueError(f"group_by field not found in registry: {field}")

    summaries = _summarize_groups(eligible, groups, selected_metric, selected_direction)
    details = _rank_details(eligible, selected_metric, selected_direction)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "group_summary.csv"
    details_path = output_dir / "run_details.csv"
    report_path = output_dir / "aggregate_report.md"
    _write_csv(summary_path, summaries, _summary_fieldnames(groups))
    _write_csv(details_path, details, _details_fieldnames(details))
    report_path.write_text(
        _format_report(
            registry_path=registry_path,
            summary_path=summary_path,
            details_path=details_path,
            input_rows=len(rows),
            eligible_rows=len(eligible),
            summaries=summaries,
            metric_name=selected_metric,
            direction=selected_direction,
            group_by=groups,
        ),
        encoding="utf-8",
    )
    return MatrixAggregateResult(
        summary_path=summary_path,
        details_path=details_path,
        report_path=report_path,
        input_rows=len(rows),
        eligible_rows=len(eligible),
        group_count=len(summaries),
        metric_name=selected_metric,
        direction=selected_direction,
        group_by=groups,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _first_metric_name(rows: list[dict[str, str]]) -> str:
    for row in rows:
        if row.get("metric_name"):
            return str(row["metric_name"])
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


def _is_eligible(row: dict[str, str], metric_name: str) -> bool:
    if row.get("status") != "succeeded":
        return False
    if row.get("metric_name") != metric_name:
        return False
    try:
        value = float(row.get("metric_value", ""))
    except ValueError:
        return False
    return math.isfinite(value)


def _normalize_row(row: dict[str, str]) -> dict[str, str]:
    output = {key: value for key, value in row.items()}
    output["metric_value_float"] = str(float(row["metric_value"]))
    return output


def _summarize_groups(
    rows: list[dict[str, str]],
    group_by: list[str],
    metric_name: str,
    direction: str,
) -> list[dict[str, str]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(field, "") for field in group_by)].append(row)
    summaries: list[dict[str, str]] = []
    for key, group_rows in grouped.items():
        values = [float(row["metric_value"]) for row in group_rows]
        best_row = _best_row(group_rows, direction)
        record = {field: value for field, value in zip(group_by, key)}
        record.update(
            {
                "metric_name": metric_name,
                "n": str(len(values)),
                "mean": _fmt(statistics.mean(values)),
                "std": _fmt(statistics.stdev(values) if len(values) > 1 else 0.0),
                "min": _fmt(min(values)),
                "max": _fmt(max(values)),
                "best_value": _fmt(float(best_row["metric_value"])),
                "best_task_id": best_row.get("task_id", ""),
                "best_cv_fold": best_row.get("cv_fold", ""),
                "best_checkpoint": best_row.get("checkpoint", ""),
            }
        )
        summaries.append(record)
    reverse = direction == "max"
    summaries.sort(key=lambda row: float(row["mean"]), reverse=reverse)
    for rank, row in enumerate(summaries, start=1):
        row["rank"] = str(rank)
    return summaries


def _best_row(rows: list[dict[str, str]], direction: str) -> dict[str, str]:
    reverse = direction == "max"
    return sorted(rows, key=lambda row: float(row["metric_value"]), reverse=reverse)[0]


def _rank_details(rows: list[dict[str, str]], metric_name: str, direction: str) -> list[dict[str, str]]:
    reverse = direction == "max"
    ranked = sorted(rows, key=lambda row: float(row["metric_value"]), reverse=reverse)
    details: list[dict[str, str]] = []
    for rank, row in enumerate(ranked, start=1):
        record = {key: value for key, value in row.items() if key != "metric_value_float"}
        record["rank"] = str(rank)
        record["metric_name"] = metric_name
        details.append(record)
    return details


def _summary_fieldnames(group_by: list[str]) -> list[str]:
    return [
        "rank",
        *group_by,
        "metric_name",
        "n",
        "mean",
        "std",
        "min",
        "max",
        "best_value",
        "best_task_id",
        "best_cv_fold",
        "best_checkpoint",
    ]


def _details_fieldnames(rows: list[dict[str, str]]) -> list[str]:
    preferred = [
        "rank",
        "task_id",
        "task",
        "cv_fold",
        "window_id",
        "preprocess_id",
        "model_id",
        "pooling_id",
        "activation",
        "metric_name",
        "metric_value",
        "checkpoint",
        "train_size",
        "val_size",
        "feature_count",
        "task_dir",
    ]
    keys = sorted({key for row in rows for key in row})
    return preferred + [key for key in keys if key not in preferred]


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _format_report(
    registry_path: Path,
    summary_path: Path,
    details_path: Path,
    input_rows: int,
    eligible_rows: int,
    summaries: list[dict[str, str]],
    metric_name: str,
    direction: str,
    group_by: list[str],
) -> str:
    lines = [
        "# Matrix Aggregate Report",
        "",
        f"- registry: `{registry_path}`",
        f"- metric_name: `{metric_name}`",
        f"- direction: `{direction}`",
        f"- group_by: `{', '.join(group_by)}`",
        f"- input_rows: {input_rows}",
        f"- eligible_rows: {eligible_rows}",
        f"- group_count: {len(summaries)}",
        f"- group_summary: `{summary_path}`",
        f"- run_details: `{details_path}`",
        "",
        "## Group Ranking",
        "",
    ]
    lines.extend(_summary_table(summaries, group_by))
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Group ranking uses the mean metric value across eligible succeeded runs.",
            "- The independent locked test split is not evaluated here.",
        ]
    )
    return "\n".join(lines) + "\n"


def _summary_table(rows: list[dict[str, str]], group_by: list[str]) -> list[str]:
    header = ["rank", *group_by, "n", "mean", "std", "min", "max", "best_task_id"]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---:" if field in {"rank", "n", "mean", "std", "min", "max"} else "---" for field in header) + " |",
    ]
    if not rows:
        lines.append("| " + " | ".join("" for _ in header) + " |")
        return lines
    for row in rows:
        lines.append("| " + " | ".join(row.get(field, "") for field in header) + " |")
    return lines


def _fmt(value: float) -> str:
    return f"{value:.6g}"
