from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FinalReportResult:
    report_path: Path
    registry_rows: int
    candidate_rows: int


def generate_final_report(
    dataset_manifest_path: Path,
    registry_path: Path,
    candidates_path: Path,
    output_path: Path,
    matrix_manifest_path: Path | None = None,
    title: str = "Spectral Deep Matrix Report",
) -> FinalReportResult:
    dataset_manifest = _read_json(dataset_manifest_path)
    matrix_manifest = _read_json(matrix_manifest_path) if matrix_manifest_path else None
    registry_rows = _read_csv(registry_path)
    candidate_rows = _read_csv(candidates_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        _format_report(
            title=title,
            dataset_manifest_path=dataset_manifest_path,
            dataset_manifest=dataset_manifest,
            matrix_manifest_path=matrix_manifest_path,
            matrix_manifest=matrix_manifest,
            registry_path=registry_path,
            registry_rows=registry_rows,
            candidates_path=candidates_path,
            candidate_rows=candidate_rows,
        ),
        encoding="utf-8",
    )
    return FinalReportResult(
        report_path=output_path,
        registry_rows=len(registry_rows),
        candidate_rows=len(candidate_rows),
    )


def _read_json(path: Path | None) -> dict:
    if path is None:
        return {}
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _format_report(
    title: str,
    dataset_manifest_path: Path,
    dataset_manifest: dict,
    matrix_manifest_path: Path | None,
    matrix_manifest: dict | None,
    registry_path: Path,
    registry_rows: list[dict[str, str]],
    candidates_path: Path,
    candidate_rows: list[dict[str, str]],
) -> str:
    status_counts = Counter(row.get("status", "unknown") for row in registry_rows)
    task_type_counts = Counter(row.get("task_type", "unknown") for row in registry_rows)
    lines = [
        f"# {title}",
        "",
        "## Data",
        "",
        f"- dataset_manifest: `{dataset_manifest_path}`",
    ]
    lines.extend(_data_lines(dataset_manifest))
    lines.append("")
    if matrix_manifest is not None:
        lines.extend(
            [
                "## Matrix",
                "",
                f"- matrix_manifest: `{matrix_manifest_path}`",
                f"- name: `{matrix_manifest.get('name', '')}`",
                f"- task_count: {matrix_manifest.get('task_count', '')}",
                f"- tasks_dir: `{matrix_manifest.get('tasks_dir', '')}`",
                f"- grid_keys: `{', '.join(matrix_manifest.get('grid_keys', []))}`",
                "",
            ]
        )
    else:
        lines.extend(["## Matrix", "", "- matrix_manifest: not provided", ""])

    lines.extend(
        [
            "## Run Registry",
            "",
            f"- registry: `{registry_path}`",
            f"- total_rows: {len(registry_rows)}",
            f"- status_counts: `{_format_counter(status_counts)}`",
            f"- task_type_counts: `{_format_counter(task_type_counts)}`",
            "",
            "| status | count |",
            "|---|---:|",
        ]
    )
    for status, count in sorted(status_counts.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(["", "## Candidates", "", f"- candidates: `{candidates_path}`", f"- candidate_rows: {len(candidate_rows)}", ""])
    lines.extend(_candidate_table(candidate_rows))
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This report summarizes the current local registry and candidate files.",
            "- Candidate ranking is only as reliable as the metric protocol used to create the registry.",
            "- Locked independent test evaluation should remain a separate final stage.",
        ]
    )
    return "\n".join(lines) + "\n"


def _data_lines(dataset_manifest: dict) -> list[str]:
    if dataset_manifest.get("format") == "npz_plus_labels":
        shape = dataset_manifest.get("shape", {})
        identity = dataset_manifest.get("identity", {})
        return [
            f"- format: `{dataset_manifest.get('format', '')}`",
            f"- samples: {shape.get('n_samples', '')}",
            f"- wavelengths: {shape.get('n_wavelengths', '')}",
            f"- row_key: `{identity.get('row_key', '')}`",
            f"- group_key: `{identity.get('group_key', '')}`",
            f"- split_counts: `{_format_mapping(dataset_manifest.get('split_counts', {}))}`",
            f"- cv_fold_counts: `{_format_mapping(dataset_manifest.get('cv_fold_counts', {}))}`",
            f"- target_columns: `{_format_mapping(dataset_manifest.get('target_columns', {}))}`",
            f"- window_count: {dataset_manifest.get('window_count', '')}",
        ]
    return [
        f"- dataset_hash: `{dataset_manifest.get('dataset_hash', '')}`",
        f"- link_key: `{dataset_manifest.get('link_key', '')}`",
        f"- target_column: `{dataset_manifest.get('target_column', '')}`",
        f"- spectra_rows: {dataset_manifest.get('spectra_rows', '')}",
        f"- supervision_rows: {dataset_manifest.get('supervision_rows', '')}",
        f"- joined_rows: {dataset_manifest.get('joined_rows', '')}",
        f"- spectra_only_count: {dataset_manifest.get('spectra_only_count', '')}",
        f"- supervision_only_count: {dataset_manifest.get('supervision_only_count', '')}",
    ]


def _format_counter(counter: Counter) -> str:
    if not counter:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counter.items()))


def _format_mapping(mapping: dict) -> str:
    if not mapping:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(mapping.items()))


def _candidate_table(rows: list[dict[str, str]]) -> list[str]:
    lines = [
        "| rank | task_id | task | fold | window | preprocess | model | pooling | metric | value | activation | checkpoint |",
        "|---:|---|---|---:|---|---|---|---|---|---:|---|---|",
    ]
    if not rows:
        lines.append("|  |  |  |  |  |  |  |  |  |  |  |  |")
        return lines
    for row in rows:
        checkpoint = row.get("checkpoint", "")
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("rank", ""),
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
                    checkpoint,
                ]
            )
            + " |"
        )
    return lines
