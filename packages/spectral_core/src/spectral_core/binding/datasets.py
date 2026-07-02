from __future__ import annotations

import csv
import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class BindResult:
    output_dir: Path
    joined_path: Path
    manifest_path: Path
    report_path: Path
    dataset_hash: str
    spectra_rows: int
    supervision_rows: int
    joined_rows: int
    spectra_only: list[str]
    supervision_only: list[str]


def bind_spectrum_supervision(
    spectra_path: Path,
    supervision_path: Path,
    link_key: str,
    target_column: str,
    output_dir: Path,
) -> BindResult:
    spectra_rows = _read_csv(spectra_path)
    supervision_rows = _read_csv(supervision_path)
    _require_columns(spectra_rows.fieldnames, [link_key], spectra_path)
    _require_columns(supervision_rows.fieldnames, [link_key, target_column], supervision_path)

    spectra_by_key = _index_rows(spectra_rows.rows, link_key, spectra_path)
    supervision_by_key = _index_rows(supervision_rows.rows, link_key, supervision_path)
    spectra_keys = set(spectra_by_key)
    supervision_keys = set(supervision_by_key)
    shared_keys = sorted(spectra_keys & supervision_keys)
    spectra_only = sorted(spectra_keys - supervision_keys)
    supervision_only = sorted(supervision_keys - spectra_keys)
    if not shared_keys:
        raise ValueError("No matching samples after link_key join")

    output_dir.mkdir(parents=True, exist_ok=True)
    copied_spectra = output_dir / "spectrum_matrix.csv"
    copied_supervision = output_dir / "supervision_table.csv"
    shutil.copyfile(spectra_path, copied_spectra)
    shutil.copyfile(supervision_path, copied_supervision)

    joined_path = output_dir / "joined_dataset.csv"
    joined_fieldnames = _joined_fieldnames(
        spectra_rows.fieldnames,
        supervision_rows.fieldnames,
        link_key,
    )
    with joined_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=joined_fieldnames)
        writer.writeheader()
        for key in shared_keys:
            writer.writerow(_join_row(spectra_by_key[key], supervision_by_key[key], joined_fieldnames, link_key))

    dataset_hash = _hash_files([copied_spectra, copied_supervision, joined_path])
    manifest = {
        "dataset_hash": dataset_hash,
        "link_key": link_key,
        "target_column": target_column,
        "spectra_path": str(copied_spectra),
        "supervision_path": str(copied_supervision),
        "joined_path": str(joined_path),
        "spectra_rows": len(spectra_rows.rows),
        "supervision_rows": len(supervision_rows.rows),
        "joined_rows": len(shared_keys),
        "spectra_only_count": len(spectra_only),
        "supervision_only_count": len(supervision_only),
        "spectra_only": spectra_only,
        "supervision_only": supervision_only,
    }
    manifest_path = output_dir / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path = output_dir / "join_report.md"
    report_path.write_text(_format_report(manifest), encoding="utf-8")

    return BindResult(
        output_dir=output_dir,
        joined_path=joined_path,
        manifest_path=manifest_path,
        report_path=report_path,
        dataset_hash=dataset_hash,
        spectra_rows=len(spectra_rows.rows),
        supervision_rows=len(supervision_rows.rows),
        joined_rows=len(shared_keys),
        spectra_only=spectra_only,
        supervision_only=supervision_only,
    )


@dataclass(frozen=True)
class _CsvRows:
    fieldnames: list[str]
    rows: list[dict[str, str]]


def _read_csv(path: Path) -> _CsvRows:
    if not path.exists():
        raise FileNotFoundError(path)
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


def _index_rows(rows: list[dict[str, str]], link_key: str, path: Path) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        key = row.get(link_key, "").strip()
        if not key:
            raise ValueError(f"Missing {link_key} at {path}:{row_number}")
        if key in indexed:
            raise ValueError(f"Duplicate {link_key} in {path}: {key}")
        indexed[key] = row
    return indexed


def _joined_fieldnames(
    spectra_fields: list[str],
    supervision_fields: list[str],
    link_key: str,
) -> list[str]:
    output = list(spectra_fields)
    for field in supervision_fields:
        if field == link_key:
            continue
        if field in output:
            output.append(f"supervision__{field}")
        else:
            output.append(field)
    return output


def _join_row(
    spectra_row: dict[str, str],
    supervision_row: dict[str, str],
    fieldnames: list[str],
    link_key: str,
) -> dict[str, str]:
    output = dict(spectra_row)
    for field, value in supervision_row.items():
        if field == link_key:
            continue
        target = field if field not in output else f"supervision__{field}"
        output[target] = value
    return {field: output.get(field, "") for field in fieldnames}


def _hash_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def _format_report(manifest: dict[str, object]) -> str:
    return (
        "# Dataset Join Report\n\n"
        f"- dataset_hash: `{manifest['dataset_hash']}`\n"
        f"- link_key: `{manifest['link_key']}`\n"
        f"- target_column: `{manifest['target_column']}`\n"
        f"- spectra_rows: {manifest['spectra_rows']}\n"
        f"- supervision_rows: {manifest['supervision_rows']}\n"
        f"- joined_rows: {manifest['joined_rows']}\n"
        f"- spectra_only_count: {manifest['spectra_only_count']}\n"
        f"- supervision_only_count: {manifest['supervision_only_count']}\n"
    )

