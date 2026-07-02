from __future__ import annotations

import base64
import binascii
import csv
import json
import math
import re
import threading
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from spectral_core.adapters import inspect_npz_plus_labels_config
from spectral_core.matrix import apply_full_factorial_design, create_npz_cnn1d_matrix, preview_npz_cnn1d_matrix
from spectral_core.queue import run_queue
from spectral_core.reports import aggregate_matrix_results
from spectral_core.scan import scan_runs
from spectral_core.selection import select_candidates


class InspectDatasetRequest(BaseModel):
    config: str
    out: str | None = None


class ImportFilePayload(BaseModel):
    name: str
    content_base64: str
    size: int = Field(default=0, ge=0)
    mime_type: str = ""


class ImportDatasetFilesRequest(BaseModel):
    files: list[ImportFilePayload] = Field(default_factory=list, min_length=1)


class ScanRunsRequest(BaseModel):
    runs: str
    out: str


class CreateNpzMatrixRequest(BaseModel):
    config: str
    out: str
    max_tasks: int | None = Field(default=None, ge=1)


class PreviewNpzMatrixRequest(BaseModel):
    config: str


class FullFactorialFactor(BaseModel):
    key: str
    values: list[Any] = Field(min_length=1)


class ApplyFullFactorialDesignRequest(BaseModel):
    config: str
    factors: list[FullFactorialFactor] = Field(default_factory=list)
    fixed: dict[str, Any] = Field(default_factory=dict)
    name: str | None = None
    out: str | None = None


class RunQueueRequest(BaseModel):
    tasks: str
    max_tasks: int | None = Field(default=None, ge=1)
    rerun_failed: bool = False
    dry_run: bool = False


class ListTasksRequest(BaseModel):
    tasks: str


class TaskLogRequest(BaseModel):
    task_dir: str
    log: Literal["queue_stdout", "queue_stderr", "status", "summary", "manifest"] = "queue_stdout"
    max_chars: int = Field(default=8000, ge=1, le=50000)


class SaveDiagnosticsRequest(BaseModel):
    out: str | None = None
    session_id: str
    started_at: str
    stopped_at: str
    url: str = ""
    user_agent: str = ""
    events: list[dict[str, Any]] = Field(default_factory=list)


class SelectCandidatesRequest(BaseModel):
    registry: str
    out: str
    metric: str | None = None
    top: int = Field(default=10, ge=1)
    direction: Literal["auto", "min", "max"] = "auto"


class AggregateMatrixRequest(BaseModel):
    registry: str
    out: str
    metric: str | None = None
    group_by: list[str] = Field(default_factory=lambda: ["window_id", "activation"])
    direction: Literal["auto", "min", "max"] = "auto"


class ModelOutputsRequest(BaseModel):
    registry: str | None = None
    tasks: str | None = None
    metric: str | None = None
    direction: Literal["auto", "min", "max"] = "auto"
    task_id: str | None = None


class ProjectSaveRequest(BaseModel):
    path: str | None = None
    filename: str | None = None
    project: dict[str, Any] = Field(default_factory=dict)


class ProjectOpenRequest(BaseModel):
    path: str


class ProjectImportFileRequest(BaseModel):
    file: ImportFilePayload


def create_app() -> FastAPI:
    static_dir = Path(__file__).resolve().parent / "static"
    app = FastAPI(
        title="SpectraMatrix API",
        version="0.1.0",
        description="Thin file-based API for the SpectraMatrix local spectral model training platform.",
    )
    app.state.queue_jobs = {}
    app.state.queue_jobs_lock = threading.Lock()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    def workbench() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/api/templates/spectra", include_in_schema=False)
    def spectra_template() -> FileResponse:
        return _template_response("01_光谱矩阵模板.csv")

    @app.get("/api/templates/supervision", include_in_schema=False)
    def supervision_template() -> FileResponse:
        return _template_response("02_监督标签模板.csv")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/workbench/defaults")
    def workbench_defaults() -> dict[str, object]:
        root = Path.cwd()
        ui_matrix_dir = root / "matrices/yam_sulfite_ui_smoke_matrix"
        return {
            "root": str(root),
            "dataset_config": str(root / "examples/yam_sulfite/configs/dataset_yamsulfcnn_dl154.json"),
            "dataset_inspect_out": str(root / "results/yam_sulfite/dataset_inspection"),
            "matrix_config": str(root / "configs/matrix/spectramatrix_ui_base.json"),
            "matrix_out": str(ui_matrix_dir),
            "matrix_max_tasks": None,
            "runs_dir": str(ui_matrix_dir / "tasks"),
            "queue_max_tasks": None,
            "queue_dry_run": False,
            "project_path": str(root / "projects" / "autosave.spectramatrix.json"),
            "demo_project_path": str(root / "projects" / "SpectraMatrix_Demo_GoodRoute.spectramatrix.json"),
            "diagnostics_out": str(root / "diagnostics"),
            "monitor_tasks_dir": str(ui_matrix_dir / "tasks"),
            "registry_out": str(root / "results/yam_sulfite_5fold_small_matrix"),
            "registry": str(root / "results/yam_sulfite_5fold_small_matrix/run_registry.csv"),
            "candidates_out": str(root / "results/yam_sulfite_5fold_small_matrix/candidates"),
            "aggregate_out": str(root / "results/yam_sulfite_5fold_small_matrix/aggregate"),
            "metric": "val_balanced_accuracy",
            "group_by": ["window_id", "activation"],
        }

    @app.post("/api/dataset/inspect")
    def inspect_dataset(request: InspectDatasetRequest) -> dict[str, object]:
        try:
            result = inspect_npz_plus_labels_config(
                config_path=Path(request.config),
                output_dir=Path(request.out).resolve() if request.out else None,
            )
        except Exception as exc:  # pragma: no cover - exercised by FastAPI response behavior
            raise _bad_request(exc) from exc
        return {
            "status": result.status,
            "samples": result.sample_count,
            "wavelengths": result.wavelength_count,
            "split_counts": result.split_counts,
            "cv_fold_counts": result.cv_fold_counts,
            "target_columns": result.target_columns,
            "window_count": result.window_count,
            "manifest": _path_or_none(result.manifest_path),
            "report": _path_or_none(result.report_path),
        }

    @app.post("/api/dataset/import-files")
    def import_dataset_files(request: ImportDatasetFilesRequest) -> dict[str, object]:
        try:
            result = _import_dataset_files(Path.cwd(), request.files)
        except Exception as exc:
            raise _bad_request(exc) from exc
        return result

    @app.post("/api/demo/import")
    def import_demo_dataset() -> dict[str, object]:
        try:
            result = _import_demo_dataset(Path.cwd())
        except Exception as exc:
            raise _bad_request(exc) from exc
        return result

    @app.post("/api/matrix/preview")
    def preview_matrix(request: PreviewNpzMatrixRequest) -> dict[str, object]:
        try:
            result = preview_npz_cnn1d_matrix(config_path=Path(request.config))
        except Exception as exc:
            raise _bad_request(exc) from exc
        return _matrix_preview_payload(result)

    @app.post("/api/matrix/full-factorial")
    def full_factorial_matrix(request: ApplyFullFactorialDesignRequest) -> dict[str, object]:
        try:
            output_dir = (
                Path(request.out).resolve()
                if request.out
                else Path.cwd() / "matrices" / "full_factorial_configs" / (time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
            )
            result = apply_full_factorial_design(
                base_config_path=Path(request.config),
                factors=[_model_payload(factor) for factor in request.factors],
                output_dir=output_dir,
                name=request.name,
                fixed_overrides=request.fixed,
            )
        except Exception as exc:
            raise _bad_request(exc) from exc
        return {
            "config": str(result.config_path),
            "preview": _matrix_preview_payload(result.preview),
        }

    @app.post("/api/matrix/create-npz")
    def create_matrix(request: CreateNpzMatrixRequest) -> dict[str, object]:
        try:
            result = create_npz_cnn1d_matrix(
                config_path=Path(request.config),
                output_dir=Path(request.out).resolve(),
                max_tasks=request.max_tasks,
            )
        except Exception as exc:
            raise _bad_request(exc) from exc
        return {
            "matrix_dir": str(result.matrix_dir),
            "tasks_dir": str(result.tasks_dir),
            "task_count": result.task_count,
            "task_index": str(result.task_index_path),
            "manifest": str(result.manifest_path),
        }

    @app.post("/api/queue/run")
    def queue(request: RunQueueRequest) -> dict[str, object]:
        try:
            result = run_queue(
                tasks_dir=Path(request.tasks).resolve(),
                max_tasks=request.max_tasks,
                rerun_failed=request.rerun_failed,
                dry_run=request.dry_run,
            )
        except Exception as exc:
            raise _bad_request(exc) from exc
        return {
            "tasks_dir": str(result.tasks_dir),
            "selected": result.selected,
            "executed": result.executed,
            "skipped": result.skipped,
            "succeeded": result.succeeded,
            "failed": result.failed,
            "dry_run": result.dry_run,
            "cancelled": result.cancelled,
            "task_ids": result.task_ids,
        }

    @app.post("/api/queue/start")
    def start_queue_job(request: RunQueueRequest) -> dict[str, object]:
        try:
            tasks_dir = Path(request.tasks).resolve()
            if not tasks_dir.exists():
                raise FileNotFoundError(tasks_dir)
            payload = _model_payload(request)
            payload["tasks"] = str(tasks_dir)
            job_id = uuid.uuid4().hex[:12]
            now = time.time()
            job = {
                "job_id": job_id,
                "status": "queued",
                "created_at": now,
                "updated_at": now,
                "request": payload,
                "result": None,
                "error": None,
            }
            _set_queue_job(app, job_id, job)
            worker = threading.Thread(target=_run_queue_job, args=(app, job_id, payload), daemon=True)
            worker.start()
        except Exception as exc:
            raise _bad_request(exc) from exc
        return _get_queue_job(app, job_id)

    @app.get("/api/queue/jobs/{job_id}")
    def queue_job(job_id: str) -> dict[str, object]:
        try:
            return _get_queue_job(app, job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Queue job not found: {job_id}") from exc

    @app.post("/api/queue/jobs/{job_id}/stop")
    def stop_queue_job(job_id: str) -> dict[str, object]:
        try:
            job = _get_queue_job(app, job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Queue job not found: {job_id}") from exc
        if job.get("status") not in {"succeeded", "failed", "cancelled"}:
            _update_queue_job(app, job_id, status="stopping", cancel_requested=True)
        return _get_queue_job(app, job_id)

    @app.post("/api/project/save")
    def save_project(request: ProjectSaveRequest) -> dict[str, object]:
        try:
            return _save_project_file(request)
        except Exception as exc:
            raise _bad_request(exc) from exc

    @app.post("/api/project/open")
    def open_project(request: ProjectOpenRequest) -> dict[str, object]:
        try:
            return _open_project_file(Path(request.path).expanduser().resolve())
        except Exception as exc:
            raise _bad_request(exc) from exc

    @app.post("/api/project/import-file")
    def import_project_file(request: ProjectImportFileRequest) -> dict[str, object]:
        try:
            return _import_project_file(request.file)
        except Exception as exc:
            raise _bad_request(exc) from exc

    @app.post("/api/tasks/list")
    def list_tasks(request: ListTasksRequest) -> dict[str, object]:
        try:
            tasks_dir = Path(request.tasks).resolve()
            rows = _list_task_rows(tasks_dir)
        except Exception as exc:
            raise _bad_request(exc) from exc
        counts = dict(sorted(Counter(row["status"] for row in rows).items()))
        return {
            "tasks_dir": str(tasks_dir),
            "total": len(rows),
            "counts": counts,
            "rows": rows,
        }

    @app.post("/api/tasks/log")
    def task_log(request: TaskLogRequest) -> dict[str, object]:
        try:
            task_dir = Path(request.task_dir).resolve()
            path = _task_log_path(task_dir, request.log)
            exists = path.exists()
            content = path.read_text(encoding="utf-8", errors="replace") if exists else ""
            if len(content) > request.max_chars:
                content = content[-request.max_chars :]
        except Exception as exc:
            raise _bad_request(exc) from exc
        return {
            "task_dir": str(task_dir),
            "log": request.log,
            "path": str(path),
            "exists": exists,
            "content": content,
        }

    @app.post("/api/diagnostics/save")
    def save_diagnostics(request: SaveDiagnosticsRequest) -> dict[str, object]:
        try:
            result = _save_diagnostics_session(request)
        except Exception as exc:
            raise _bad_request(exc) from exc
        return result

    @app.post("/api/runs/scan")
    def scan(request: ScanRunsRequest) -> dict[str, object]:
        try:
            result = scan_runs(runs_dir=Path(request.runs).resolve(), output_dir=Path(request.out).resolve())
        except Exception as exc:
            raise _bad_request(exc) from exc
        return {
            "scanned": result.scanned,
            "succeeded": result.succeeded,
            "failed": result.failed,
            "registry": str(result.registry_path),
        }

    @app.post("/api/candidates/select")
    def candidates(request: SelectCandidatesRequest) -> dict[str, object]:
        try:
            result = select_candidates(
                registry_path=Path(request.registry).resolve(),
                output_dir=Path(request.out).resolve(),
                metric_name=request.metric,
                top=request.top,
                direction=request.direction,
            )
        except Exception as exc:
            raise _bad_request(exc) from exc
        return {
            "input_rows": result.input_rows,
            "eligible_rows": result.eligible_rows,
            "selected_rows": result.selected_rows,
            "metric": result.metric_name,
            "direction": result.direction,
            "candidates": str(result.candidates_path),
            "report": str(result.report_path),
        }

    @app.post("/api/matrix/aggregate")
    def aggregate(request: AggregateMatrixRequest) -> dict[str, object]:
        try:
            result = aggregate_matrix_results(
                registry_path=Path(request.registry).resolve(),
                output_dir=Path(request.out).resolve(),
                metric_name=request.metric,
                group_by=request.group_by,
                direction=request.direction,
            )
        except Exception as exc:
            raise _bad_request(exc) from exc
        return {
            "input_rows": result.input_rows,
            "eligible_rows": result.eligible_rows,
            "group_count": result.group_count,
            "metric": result.metric_name,
            "direction": result.direction,
            "group_by": result.group_by,
            "group_summary": str(result.summary_path),
            "run_details": str(result.details_path),
            "report": str(result.report_path),
        }

    @app.post("/api/outputs/summary")
    def outputs_summary(request: ModelOutputsRequest) -> dict[str, object]:
        try:
            result = _model_outputs_summary(request)
        except Exception as exc:
            raise _bad_request(exc) from exc
        return result

    return app


def _path_or_none(path: Path | None) -> str | None:
    return str(path) if path is not None else None


def _template_response(filename: str) -> FileResponse:
    path = _project_template_dir() / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Template not found: {filename}")
    return FileResponse(path, media_type="text/csv; charset=utf-8", filename=filename)


def _project_template_dir() -> Path:
    cwd_template_dir = Path.cwd() / "CSV导入模板"
    if cwd_template_dir.exists():
        return cwd_template_dir
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "CSV导入模板"
        if candidate.exists():
            return candidate
    return cwd_template_dir


def _save_diagnostics_session(request: SaveDiagnosticsRequest) -> dict[str, object]:
    output_dir = Path(request.out).expanduser().resolve() if request.out else (Path.cwd() / "diagnostics").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_session_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", request.session_id).strip("-") or uuid.uuid4().hex[:12]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    base = output_dir / f"diagnostic-session-{stamp}-{safe_session_id}"
    payload = {
        "app": "SpectraMatrix",
        "session_id": request.session_id,
        "started_at": request.started_at,
        "stopped_at": request.stopped_at,
        "url": request.url,
        "user_agent": request.user_agent,
        "event_count": len(request.events),
        "events": request.events,
    }
    json_path = base.with_suffix(".json")
    md_path = base.with_suffix(".md")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_diagnostics_markdown(payload), encoding="utf-8")
    return {
        "status": "saved",
        "event_count": len(request.events),
        "directory": str(output_dir),
        "json": str(json_path),
        "markdown": str(md_path),
    }


def _diagnostics_markdown(payload: dict[str, Any]) -> str:
    events = list(payload.get("events", []))
    problem_events = [
        event for event in events
        if _diagnostic_event_is_problem(event)
    ]
    lines = [
        "# SpectraMatrix diagnostic session",
        "",
        f"- session_id: `{payload.get('session_id', '')}`",
        f"- started_at: `{payload.get('started_at', '')}`",
        f"- stopped_at: `{payload.get('stopped_at', '')}`",
        f"- url: `{payload.get('url', '')}`",
        f"- event_count: `{payload.get('event_count', 0)}`",
        f"- problem_event_count: `{len(problem_events)}`",
        "",
        "## Problems",
        "",
    ]
    if problem_events:
        for event in problem_events[:40]:
            lines.append(f"- `{event.get('at', '')}` `{event.get('name', '')}` {_diagnostic_detail_text(event.get('detail'))}")
    else:
        lines.append("- No explicit error or failed action was captured.")
    lines.extend(["", "## Timeline", ""])
    for event in events[:200]:
        lines.append(f"- `{event.get('at', '')}` `{event.get('name', '')}` {_diagnostic_detail_text(event.get('detail'))}")
    lines.append("")
    return "\n".join(lines)


def _diagnostic_event_is_problem(event: dict[str, Any]) -> bool:
    name = str(event.get("name", "")).lower()
    detail = event.get("detail", {})
    detail_text = _diagnostic_detail_text(detail).lower()
    problem_markers = ["error", "fail", "failed", "exception", "rejection", "timeout", "报错", "失败"]
    return any(marker in name or marker in detail_text for marker in problem_markers)


def _diagnostic_detail_text(detail: object) -> str:
    if isinstance(detail, dict):
        compact = {
            key: value for key, value in detail.items()
            if key in {"status", "output", "message", "path", "url", "method", "http_status", "detail"}
        }
        if compact:
            return json.dumps(compact, ensure_ascii=False, default=str)
    return json.dumps(detail, ensure_ascii=False, default=str)


def _matrix_preview_payload(result: object) -> dict[str, object]:
    return {
        "name": result.name,
        "description": result.description,
        "source_config": str(result.source_config),
        "dataset_config": str(result.dataset_config),
        "fixed": result.fixed,
        "grid": result.grid,
        "task_specific_overrides": result.task_specific_overrides,
        "total_combinations": result.total_combinations,
        "formula": result.formula,
    }


def _import_dataset_files(root: Path, files: list[ImportFilePayload]) -> dict[str, object]:
    import_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    import_dir = root / "imports" / "dataset_uploads" / import_id
    import_dir.mkdir(parents=True, exist_ok=False)
    rows: list[dict[str, object]] = []
    detected_config: Path | None = None
    counts: Counter[str] = Counter()
    for item in files:
        filename = _safe_filename(item.name)
        path = import_dir / filename
        try:
            content = base64.b64decode(item.content_base64, validate=True)
        except binascii.Error as exc:
            raise ValueError(f"Invalid base64 content for {item.name}") from exc
        path.write_bytes(content)
        kind, preview = _classify_imported_file(path)
        counts[kind] += 1
        if kind == "dataset_config" and detected_config is None:
            detected_config = path
        rows.append(
            {
                "name": filename,
                "path": str(path),
                "kind": kind,
                "size": len(content),
                "mime_type": item.mime_type,
                "preview": preview,
            }
        )
    generated: dict[str, object] = {}
    if detected_config is None:
        generated = _auto_prepare_dataset_config(import_dir, rows)
        if generated.get("dataset_config"):
            detected_config = Path(str(generated["dataset_config"]))

    manifest = {
        "import_id": import_id,
        "import_dir": str(import_dir),
        "dataset_config": _path_or_none(detected_config),
        "generated": generated,
        "files": rows,
        "counts": dict(sorted(counts.items())),
    }
    (import_dir / "import_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def _import_demo_dataset(root: Path) -> dict[str, object]:
    demo_dir = _project_demo_dir(root)
    files = [
        demo_dir / "01_光谱矩阵_UV3600iPlus_CNN154.csv",
        demo_dir / "02_监督标签_酸碱滴定正式口径.csv",
    ]
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Demo dataset files not found: {missing}")
    payload = [
        ImportFilePayload(
            name=path.name,
            content_base64=base64.b64encode(path.read_bytes()).decode("ascii"),
            size=path.stat().st_size,
            mime_type="text/csv",
        )
        for path in files
    ]
    return _import_dataset_files(root, payload)


def _project_demo_dir(root: Path) -> Path:
    cwd_demo_dir = root / "演示数据集"
    if cwd_demo_dir.exists():
        return cwd_demo_dir
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "演示数据集"
        if candidate.exists():
            return candidate
    return cwd_demo_dir


def _safe_filename(name: str) -> str:
    clean = Path(name).name.strip().replace("/", "_").replace("\\", "_")
    if not clean or clean in {".", ".."}:
        return f"uploaded_{uuid.uuid4().hex[:8]}"
    return clean


def _classify_imported_file(path: Path) -> tuple[str, dict[str, object]]:
    suffix = path.suffix.lower()
    preview: dict[str, object] = {}
    if suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            keys = sorted(payload.keys()) if isinstance(payload, dict) else []
            preview["keys"] = keys[:12]
            if isinstance(payload, dict) and {"format", "spectra_matrix", "labels"}.issubset(payload.keys()):
                return "dataset_config", preview
            if isinstance(payload, dict) and {"dataset_config", "grid"}.intersection(payload.keys()):
                return "matrix_config", preview
        except (json.JSONDecodeError, UnicodeDecodeError):
            preview["error"] = "json_preview_failed"
        return "json", preview
    if suffix == ".npz":
        preview.update(_npz_preview(path))
        return "spectra_matrix", preview
    if suffix == ".csv":
        preview.update(_csv_preview(path))
        columns = _csv_header(path)
        lower_columns = {column.lower() for column in columns}
        lower_name = path.name.lower()
        wavelength_columns = _detect_wavelength_columns(columns)
        if "window_id" in lower_columns and (
            {"start_nm", "end_nm"}.issubset(lower_columns) or "intervals_nm" in lower_columns
        ):
            return "band_windows", preview
        if "cv_fold" in lower_columns or "fold" in lower_columns or "cv" in lower_name:
            return "cv_folds", preview
        if "split" in lower_columns or "split" in lower_name:
            return "split", preview
        if len(wavelength_columns) >= 3 and "label" not in lower_name and "supervision" not in lower_name:
            preview["wavelength_columns"] = len(wavelength_columns)
            return "spectra_csv", preview
        if "label" in lower_name or "supervision" in lower_name:
            return "labels", preview
        if _target_columns_from_fieldnames(columns):
            return "labels", preview
        if "split" in lower_name:
            return "split", preview
        if "fold" in lower_name or "cv" in lower_name:
            return "cv_folds", preview
        if "window" in lower_name or "band" in lower_name:
            return "band_windows", preview
        return "csv", preview
    return "other", preview


def _csv_preview(path: Path) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return {}
    lines = [line for line in text.splitlines() if line.strip()]
    header = lines[0].split(",") if lines else []
    return {"columns": header[:12], "column_count": len(header), "rows_previewed": max(0, min(len(lines) - 1, 5))}


def _csv_header(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            return [str(column) for column in next(reader, [])]
    except OSError:
        return []


def _auto_prepare_dataset_config(import_dir: Path, rows: list[dict[str, object]]) -> dict[str, object]:
    spectra_npz = _first_imported_path(rows, "spectra_matrix")
    spectra_csv = _first_imported_path(rows, "spectra_csv")
    labels_path = _first_imported_path(rows, "labels")
    split_path = _first_imported_path(rows, "split")
    cv_path = _first_imported_path(rows, "cv_folds")
    windows_path = _first_imported_path(rows, "band_windows")
    if spectra_npz is None and spectra_csv is None:
        return {"status": "waiting_for_spectra", "message": "Drop a spectral matrix CSV or NPZ file."}
    if labels_path is None and spectra_csv is None:
        return {"status": "waiting_for_labels", "message": "Drop a supervision/label CSV file."}

    try:
        dataset = _prepare_auto_dataset_package(
            import_dir=import_dir,
            spectra_npz=spectra_npz,
            spectra_csv=spectra_csv,
            labels_path=labels_path,
            split_path=split_path,
            cv_path=cv_path,
            windows_path=windows_path,
        )
    except Exception as exc:
        return {"status": "needs_review", "message": f"{type(exc).__name__}: {exc}"}
    return dataset


def _prepare_auto_dataset_package(
    import_dir: Path,
    spectra_npz: Path | None,
    spectra_csv: Path | None,
    labels_path: Path | None,
    split_path: Path | None,
    cv_path: Path | None,
    windows_path: Path | None,
) -> dict[str, object]:
    if spectra_csv is not None:
        spectra = _load_spectra_csv(spectra_csv)
        spectra_matrix = import_dir / "spectra_matrix.auto.npz"
        _write_spectra_npz(spectra_matrix, spectra)
        source_kind = "spectra_csv"
    elif spectra_npz is not None:
        spectra = _load_spectra_npz(spectra_npz)
        spectra_matrix = spectra_npz
        source_kind = "spectra_matrix"
    else:  # pragma: no cover - protected by caller
        raise ValueError("Missing spectral matrix")

    label_rows = _aligned_label_rows(spectra, labels_path)
    targets = _infer_targets(label_rows.fieldnames)
    labels_out = import_dir / "labels.auto.csv"
    _write_csv(labels_out, label_rows.fieldnames, label_rows.rows)

    split_out = split_path or import_dir / "split.auto.csv"
    cv_out = cv_path or import_dir / "cv_folds.auto.csv"
    windows_out = windows_path or import_dir / "band_windows.auto.csv"
    generated_files: list[str] = [str(labels_out)]
    auto_notes: list[str] = []
    if split_path is None:
        _write_auto_split(split_out, spectra)
        generated_files.append(str(split_out))
        auto_notes.append("Generated an internal all-development split.")
    if cv_path is None:
        _write_auto_cv_folds(cv_out, spectra)
        generated_files.append(str(cv_out))
        auto_notes.append("Generated internal deterministic 5-fold assignments.")
    if windows_path is None:
        _write_auto_windows(windows_out, spectra.wavelengths)
        generated_files.append(str(windows_out))
        auto_notes.append("Generated one internal full-spectrum window.")

    config = {
        "name": "auto_import_dataset",
        "format": "npz_plus_labels",
        "paths_relative_to_this_file": True,
        "spectra_matrix": _relative_path(spectra_matrix, import_dir),
        "labels": _relative_path(labels_out, import_dir),
        "split": _relative_path(split_out, import_dir),
        "cv_folds": _relative_path(cv_out, import_dir),
        "band_windows": _relative_path(windows_out, import_dir),
        "identity": {"row_key": spectra.row_key, "group_key": spectra.group_key},
        "targets": targets,
        "split_policy": {
            "split_column": "split",
            "development_value": "dev",
            "locked_test_value": "test",
            "cv_fold_column": "cv_fold",
        },
        "import": {
            "source_kind": source_kind,
            "source_spectra": str(spectra_csv or spectra_npz),
            "source_labels": str(labels_path) if labels_path else str(spectra_csv),
            "generated_by": "workbench_csv_import",
        },
    }
    config_path = import_dir / "dataset_config.auto.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    generated_files.append(str(config_path))
    return {
        "status": "ready",
        "dataset_config": str(config_path),
        "source_kind": source_kind,
        "samples": len(spectra.sample_ids),
        "wavelengths": len(spectra.wavelengths),
        "targets": targets,
        "generated_files": generated_files,
        "auto_notes": auto_notes,
        "warnings": [],
    }


class _SpectraPackage:
    def __init__(
        self,
        sample_ids: list[str],
        group_keys: list[str],
        wavelengths: list[float],
        x: list[list[float]],
        row_key: str,
        group_key: str,
        source_rows: list[dict[str, str]] | None = None,
    ) -> None:
        self.sample_ids = sample_ids
        self.group_keys = group_keys
        self.wavelengths = wavelengths
        self.x = x
        self.row_key = row_key
        self.group_key = group_key
        self.source_rows = source_rows or []


class _CsvTable:
    def __init__(self, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
        self.fieldnames = fieldnames
        self.rows = rows


_WL_NUMERIC_RE = re.compile(r"^\d+(?:\.\d+)?$")
_WL_PREFIX_RE = re.compile(r"^(?:wl|wavelength|nm)[_-]?(\d+(?:[_.]\d+)?)$", re.IGNORECASE)


def _detect_wavelength_columns(columns: list[str]) -> list[tuple[str, float]]:
    detected: list[tuple[str, float]] = []
    for column in columns:
        value = _parse_wavelength_column(column)
        if value is not None:
            detected.append((column, value))
    return sorted(detected, key=lambda item: item[1])


def _parse_wavelength_column(column: str) -> float | None:
    clean = str(column).strip()
    if _WL_NUMERIC_RE.match(clean):
        return float(clean)
    match = _WL_PREFIX_RE.match(clean)
    if match:
        return float(match.group(1).replace("_", "."))
    return None


def _load_spectra_csv(path: Path) -> _SpectraPackage:
    table = _read_csv_table(path)
    wavelength_columns = _detect_wavelength_columns(table.fieldnames)
    if len(wavelength_columns) < 3:
        raise ValueError("Could not detect enough wavelength columns in spectral CSV")
    row_key = _choose_first_column(table.fieldnames, ["sample_id", "sample", "id", "sample_link_code", "linkcode", "link_code"])
    if row_key is None:
        raise ValueError("Spectral CSV must include sample_id or sample_link_code/linkcode")
    group_key = _choose_first_column(table.fieldnames, ["sample_link_code", "linkcode", "link_code"]) or row_key

    sample_ids: list[str] = []
    group_keys: list[str] = []
    matrix: list[list[float]] = []
    for row_number, row in enumerate(table.rows, start=2):
        sample_id = row.get(row_key, "").strip()
        group_value = row.get(group_key, sample_id).strip() or sample_id
        if not sample_id:
            raise ValueError(f"Missing {row_key} at {path}:{row_number}")
        values: list[float] = []
        for column, _value in wavelength_columns:
            raw = row.get(column, "").strip()
            if raw == "":
                raise ValueError(f"Missing wavelength value {column} at {path}:{row_number}")
            values.append(float(raw))
        sample_ids.append(sample_id)
        group_keys.append(group_value)
        matrix.append(values)
    _reject_duplicate_strings(sample_ids, f"{path}:{row_key}")
    return _SpectraPackage(
        sample_ids=sample_ids,
        group_keys=group_keys,
        wavelengths=[value for _column, value in wavelength_columns],
        x=matrix,
        row_key=row_key,
        group_key=group_key,
        source_rows=table.rows,
    )


def _load_spectra_npz(path: Path) -> _SpectraPackage:
    try:
        import numpy as np
    except ModuleNotFoundError as exc:
        raise RuntimeError("NPZ import requires numpy") from exc
    with np.load(path, allow_pickle=False) as data:
        if not {"x", "wavelengths", "sample_ids"}.issubset(data.files):
            raise ValueError("NPZ must contain x, wavelengths, and sample_ids arrays")
        x = data["x"]
        wavelengths = data["wavelengths"]
        sample_ids = [str(value) for value in data["sample_ids"].tolist()]
        if x.ndim != 2 or wavelengths.ndim != 1:
            raise ValueError("NPZ x must be 2D and wavelengths must be 1D")
        if x.shape[0] != len(sample_ids) or x.shape[1] != len(wavelengths):
            raise ValueError("NPZ sample_ids/wavelengths do not match x shape")
    _reject_duplicate_strings(sample_ids, f"{path}:sample_ids")
    return _SpectraPackage(
        sample_ids=sample_ids,
        group_keys=sample_ids,
        wavelengths=[float(value) for value in wavelengths.tolist()],
        x=x.tolist(),
        row_key="sample_id",
        group_key="sample_link_code",
    )


def _write_spectra_npz(path: Path, spectra: _SpectraPackage) -> None:
    try:
        import numpy as np
    except ModuleNotFoundError as exc:
        raise RuntimeError("CSV spectral import requires numpy") from exc
    np.savez_compressed(
        path,
        x=np.array(spectra.x, dtype=np.float32),
        wavelengths=np.array(spectra.wavelengths, dtype=np.float32),
        sample_ids=np.array(spectra.sample_ids),
    )


def _aligned_label_rows(spectra: _SpectraPackage, labels_path: Path | None) -> _CsvTable:
    if labels_path is None:
        if not spectra.source_rows:
            raise ValueError("A supervision/label CSV is required for NPZ spectra imports")
        table = _CsvTable(fieldnames=list(spectra.source_rows[0].keys()), rows=spectra.source_rows)
    else:
        table = _read_csv_table(labels_path)

    target_columns = _target_columns_from_fieldnames(table.fieldnames)
    if not target_columns:
        raise ValueError("Could not detect target columns in supervision CSV")

    join = _choose_label_join(table, spectra)
    indexed = _index_label_rows(table.rows, join["label_column"])
    output_fields = _label_output_fields(spectra, table.fieldnames, target_columns)
    output_rows: list[dict[str, str]] = []
    missing: list[str] = []
    for sample_id, group_value in zip(spectra.sample_ids, spectra.group_keys):
        join_value = sample_id if join["spectra_column"] == spectra.row_key else group_value
        source = indexed.get(join_value)
        if source is None:
            missing.append(join_value)
            continue
        row = {field: source.get(field, "") for field in output_fields}
        row[spectra.row_key] = sample_id
        row[spectra.group_key] = group_value
        output_rows.append(row)
    if missing:
        raise ValueError(f"Supervision rows missing for {len(missing)} spectral samples: {missing[:5]}")
    return _CsvTable(fieldnames=output_fields, rows=output_rows)


def _choose_label_join(table: _CsvTable, spectra: _SpectraPackage) -> dict[str, str]:
    sample_values = set(spectra.sample_ids)
    group_values = set(spectra.group_keys)
    candidates = [spectra.row_key, spectra.group_key, "sample_id", "sample_link_code", "linkcode", "link_code"]
    for column in candidates:
        if column not in table.fieldnames:
            continue
        values = {row.get(column, "").strip() for row in table.rows}
        if values & sample_values:
            return {"label_column": column, "spectra_column": spectra.row_key}
        if values & group_values:
            return {"label_column": column, "spectra_column": spectra.group_key}
    raise ValueError("Could not link spectral samples with supervision CSV; check sample_id/sample_link_code")


def _label_output_fields(spectra: _SpectraPackage, source_fields: list[str], target_columns: list[str]) -> list[str]:
    fields: list[str] = []
    for field in [spectra.row_key, spectra.group_key]:
        if field not in fields:
            fields.append(field)
    for field in source_fields:
        if field not in fields:
            fields.append(field)
    for field in target_columns:
        if field not in fields:
            fields.append(field)
    return fields


def _target_columns_from_fieldnames(fieldnames: list[str]) -> list[str]:
    preferred = [
        "ppm_mg_kg",
        "target",
        "y",
        "high_risk_gt500_label",
        "three_class_label",
        "tri_class_label",
        "label",
        "class_label",
    ]
    return [column for column in preferred if column in fieldnames]


def _infer_targets(fieldnames: list[str]) -> dict[str, object]:
    targets: dict[str, object] = {}
    regression = _choose_first_column(fieldnames, ["ppm_mg_kg", "target", "y"])
    binary = _choose_first_column(fieldnames, ["high_risk_gt500_label", "binary_label", "sulfur_fumigated_label"])
    tri_class = _choose_first_column(fieldnames, ["three_class_label", "tri_class_label", "ppm3_label", "class_label", "label"])
    if regression:
        targets["regression"] = {"column": regression, "default_metric": "val_rmse", "higher_is_better": False}
    if binary:
        targets["binary"] = {"column": binary, "default_metric": "val_balanced_accuracy", "higher_is_better": True}
    elif regression:
        targets["binary"] = {
            "mode": "derive_from_numeric",
            "source_column": regression,
            "boundary": "left_closed_right_open",
            "bins": [
                {"label": 0, "name": "low", "min": None, "max": 500},
                {"label": 1, "name": "high", "min": 500, "max": None},
            ],
            "default_metric": "val_balanced_accuracy",
            "higher_is_better": True,
        }
    if tri_class:
        targets["tri_class"] = {"column": tri_class, "default_metric": "val_balanced_accuracy", "higher_is_better": True}
    elif regression:
        targets["tri_class"] = {
            "mode": "derive_from_numeric",
            "source_column": regression,
            "boundary": "left_closed_right_open",
            "bins": [
                {"label": 0, "name": "low", "min": None, "max": 500},
                {"label": 1, "name": "medium", "min": 500, "max": 1000},
                {"label": 2, "name": "high", "min": 1000, "max": None},
            ],
            "default_metric": "val_balanced_accuracy",
            "higher_is_better": True,
        }
    if not targets:
        raise ValueError("No supported target column found")
    return targets


def _write_auto_split(path: Path, spectra: _SpectraPackage) -> None:
    rows = [
        {spectra.row_key: sample_id, spectra.group_key: group_key, "split": "dev"}
        for sample_id, group_key in zip(spectra.sample_ids, spectra.group_keys)
    ]
    _write_csv(path, [spectra.row_key, spectra.group_key, "split"], rows)


def _write_auto_cv_folds(path: Path, spectra: _SpectraPackage) -> None:
    rows = [
        {spectra.row_key: sample_id, spectra.group_key: group_key, "cv_fold": str((index % 5) + 1)}
        for index, (sample_id, group_key) in enumerate(zip(spectra.sample_ids, spectra.group_keys))
    ]
    _write_csv(path, [spectra.row_key, spectra.group_key, "cv_fold"], rows)


def _write_auto_windows(path: Path, wavelengths: list[float]) -> None:
    start_nm = min(wavelengths)
    end_nm = max(wavelengths)
    _write_csv(
        path,
        ["window_id", "start_nm", "end_nm", "intervals_nm", "description"],
        [
            {
                "window_id": "WFULL_500_2500",
                "start_nm": str(start_nm),
                "end_nm": str(end_nm),
                "intervals_nm": f"{start_nm}-{end_nm}",
                "description": "Full spectral window generated from imported spectra",
            }
        ],
    )


def _read_csv_table(path: Path) -> _CsvTable:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not fieldnames:
        raise ValueError(f"CSV has no header: {path}")
    if not rows:
        raise ValueError(f"CSV has no rows: {path}")
    return _CsvTable(fieldnames=fieldnames, rows=rows)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _first_imported_path(rows: list[dict[str, object]], kind: str) -> Path | None:
    for row in rows:
        if row.get("kind") == kind and row.get("path"):
            return Path(str(row["path"]))
    return None


def _choose_first_column(fieldnames: list[str], candidates: list[str]) -> str | None:
    lower_to_name = {name.lower(): name for name in fieldnames}
    for candidate in candidates:
        if candidate.lower() in lower_to_name:
            return lower_to_name[candidate.lower()]
    return None


def _index_label_rows(rows: list[dict[str, str]], key_column: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get(key_column, "").strip()
        if key and key not in indexed:
            indexed[key] = row
    return indexed


def _reject_duplicate_strings(values: list[str], label: str) -> None:
    duplicates = [value for value, count in Counter(values).items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate values in {label}: {duplicates}")


def _relative_path(path: Path, base_dir: Path) -> str:
    try:
        return str(path.relative_to(base_dir))
    except ValueError:
        return str(path)


def _npz_preview(path: Path) -> dict[str, object]:
    try:
        import numpy as np
    except Exception:
        return {}
    try:
        with np.load(path, allow_pickle=False) as data:
            arrays = {}
            for key in data.files[:8]:
                arrays[key] = list(data[key].shape)
            return {"arrays": arrays}
    except Exception:
        return {"error": "npz_preview_failed"}


def _model_payload(model: BaseModel) -> dict[str, object]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _queue_result_payload(result) -> dict[str, object]:
    return {
        "tasks_dir": str(result.tasks_dir),
        "selected": result.selected,
        "executed": result.executed,
        "skipped": result.skipped,
        "succeeded": result.succeeded,
        "failed": result.failed,
        "dry_run": result.dry_run,
        "cancelled": result.cancelled,
        "task_ids": result.task_ids,
    }


def _save_project_file(request: ProjectSaveRequest) -> dict[str, object]:
    project = dict(request.project or {})
    path = _project_file_path(request.path, project, request.filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    saved_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    project["project_file"] = str(path)
    project["updated_at"] = saved_at
    envelope = {
        "app": "SpectraMatrix",
        "schema_version": 1,
        "format": "spectramatrix_project",
        "saved_at": saved_at,
        "project": project,
    }
    path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"status": "saved", "path": str(path), "project": project}


def _open_project_file(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _open_project_payload(payload, fallback_path=str(path), status="opened")


def _import_project_file(file: ImportFilePayload) -> dict[str, object]:
    if not file.name.endswith(".spectramatrix.json"):
        raise ValueError("Please choose a .spectramatrix.json project file.")
    try:
        raw = base64.b64decode(file.content_base64.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as exc:
        raise ValueError(f"Invalid project file encoding: {file.name}") from exc
    payload = json.loads(raw.decode("utf-8-sig"))
    return _open_project_payload(payload, fallback_path=file.name, status="imported")


def _open_project_payload(payload: Any, fallback_path: str, status: str) -> dict[str, object]:
    if not isinstance(payload, dict) or payload.get("format") != "spectramatrix_project":
        raise ValueError("Not a SpectraMatrix project file.")
    project = payload.get("project")
    if not isinstance(project, dict):
        raise ValueError("Project file is missing project payload.")
    project_path = str(project.get("project_file") or fallback_path)
    return {
        "status": status,
        "path": project_path,
        "schema_version": payload.get("schema_version", 1),
        "saved_at": payload.get("saved_at", ""),
        "project": project,
    }


def _project_file_path(path_text: str | None, project: dict[str, Any], filename: str | None = None) -> Path:
    if filename:
        path = Path.cwd() / "projects" / _safe_project_filename(filename)
    elif path_text:
        path = Path(path_text).expanduser()
    elif project.get("project_file"):
        path = Path(str(project["project_file"])).expanduser()
    elif project.get("matrix_dir"):
        path = Path(str(project["matrix_dir"])).expanduser() / "SpectraMatrix_Project.spectramatrix.json"
    else:
        path = Path.cwd() / "projects" / "autosave.spectramatrix.json"
    if path.suffix != ".json" or not path.name.endswith(".spectramatrix.json"):
        if path.exists() and path.is_dir():
            path = path / "SpectraMatrix_Project.spectramatrix.json"
        elif path.suffix:
            path = path.with_name(f"{path.stem}.spectramatrix.json")
        else:
            path = path.with_suffix(".spectramatrix.json")
    return path.resolve()


def _safe_project_filename(name: str) -> str:
    raw = Path(name).name.strip()
    for suffix in [".spectramatrix.json", ".json"]:
        if raw.lower().endswith(suffix):
            raw = raw[: -len(suffix)]
            break
    safe = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in raw).strip("._-")
    if not safe:
        safe = f"SpectraMatrix_Project_{time.strftime('%Y%m%d_%H%M%S')}"
    return f"{safe}.spectramatrix.json"


def _get_queue_job(app: FastAPI, job_id: str) -> dict[str, object]:
    with app.state.queue_jobs_lock:
        if job_id not in app.state.queue_jobs:
            raise KeyError(job_id)
        return dict(app.state.queue_jobs[job_id])


def _set_queue_job(app: FastAPI, job_id: str, payload: dict[str, object]) -> None:
    with app.state.queue_jobs_lock:
        app.state.queue_jobs[job_id] = payload


def _update_queue_job(app: FastAPI, job_id: str, **changes: object) -> None:
    with app.state.queue_jobs_lock:
        job = dict(app.state.queue_jobs[job_id])
        job.update(changes)
        job["updated_at"] = time.time()
        app.state.queue_jobs[job_id] = job


def _run_queue_job(app: FastAPI, job_id: str, payload: dict[str, object]) -> None:
    def should_stop() -> bool:
        with app.state.queue_jobs_lock:
            job = app.state.queue_jobs.get(job_id, {})
            return bool(job.get("cancel_requested", False))

    try:
        _update_queue_job(app, job_id, status="running", cancel_requested=False)
        result = run_queue(
            tasks_dir=Path(str(payload["tasks"])).resolve(),
            max_tasks=payload.get("max_tasks"),
            rerun_failed=bool(payload.get("rerun_failed", False)),
            dry_run=bool(payload.get("dry_run", False)),
            should_stop=should_stop,
        )
        final_status = "cancelled" if result.cancelled else "succeeded"
        _update_queue_job(app, job_id, status=final_status, result=_queue_result_payload(result), error=None)
    except Exception as exc:  # pragma: no cover - failure payload is covered through API behavior
        _update_queue_job(app, job_id, status="failed", result=None, error=f"{type(exc).__name__}: {exc}")


def _list_task_rows(tasks_dir: Path) -> list[dict[str, str]]:
    if not tasks_dir.exists():
        raise FileNotFoundError(tasks_dir)
    rows: list[dict[str, str]] = []
    for task_dir in sorted(path for path in tasks_dir.iterdir() if path.is_dir()):
        manifest = _read_json_if_exists(task_dir / "manifest.json")
        status_payload = _read_json_if_exists(task_dir / "status.json")
        summary = _read_json_if_exists(task_dir / "summary.json")
        status = str(summary.get("status") or status_payload.get("status") or manifest.get("status") or "unknown")
        rows.append(
            {
                "task_id": str(manifest.get("task_id") or summary.get("task_id") or task_dir.name),
                "task_dir": str(task_dir),
                "status": status,
                "task": str(manifest.get("task", "")),
                "cv_fold": str(manifest.get("cv_fold", "")),
                "window_id": str(manifest.get("window_id", "")),
                "preprocess_id": str(manifest.get("preprocess_id", "")),
                "model_id": str(manifest.get("model_id", "")),
                "pooling_id": str(manifest.get("pooling_id", "")),
                "activation": str(summary.get("activation") or manifest.get("activation") or manifest.get("activation_id", "")),
                "loss_id": str(manifest.get("loss_id", "")),
                "metric_name": str(summary.get("metric_name", "")),
                "metric_value": str(summary.get("metric_value", "")),
                "checkpoint": str(summary.get("checkpoint", "")),
            }
        )
    return rows


def _read_json_if_exists(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _task_log_path(task_dir: Path, log_name: str) -> Path:
    allowed = {
        "queue_stdout": task_dir / "logs" / "queue_stdout.log",
        "queue_stderr": task_dir / "logs" / "queue_stderr.log",
        "status": task_dir / "status.json",
        "summary": task_dir / "summary.json",
        "manifest": task_dir / "manifest.json",
    }
    return allowed[log_name]


def _model_outputs_summary(request: ModelOutputsRequest) -> dict[str, object]:
    registry_path = Path(str(request.registry or "")).expanduser().resolve() if request.registry else None
    if registry_path is None and request.tasks:
        registry_path = Path(request.tasks).expanduser().resolve().parent / "run_registry.csv"
    if registry_path is None:
        raise ValueError("registry or tasks is required")
    rows = _read_registry_rows(registry_path)
    eligible = [row for row in rows if _row_has_metric(row, request.metric)]
    if not eligible:
        raise ValueError("No succeeded model rows with numeric metrics")
    metric_name = request.metric or str(eligible[0].get("metric_name", ""))
    direction = _metric_direction(metric_name, request.direction)
    ranked_all = sorted(
        [row for row in eligible if row.get("metric_name") == metric_name],
        key=lambda row: float(row.get("metric_value", "nan")),
        reverse=direction == "max",
    )
    if not ranked_all:
        raise ValueError(f"No succeeded model rows for metric: {metric_name}")
    authenticity = [_model_result_authenticity(row) for row in ranked_all]
    ranked = [row for row, check in zip(ranked_all, authenticity) if check["is_real"]]
    excluded = [
        {
            "task_id": row.get("task_id", ""),
            "reasons": check["reasons"],
        }
        for row, check in zip(ranked_all, authenticity)
        if not check["is_real"]
    ]
    if not ranked:
        raise ValueError(
            "No verifiable real training results in this registry. "
            "The result rows look like demo fixtures or incomplete runs."
        )
    selected = ranked[0]
    if request.task_id:
        matches = [row for row in ranked if row.get("task_id") == request.task_id]
        if not matches:
            raise ValueError(f"Task is not available in this registry: {request.task_id}")
        selected = matches[0]
    return {
        "registry": str(registry_path),
        "metric": metric_name,
        "direction": direction,
        "input_rows": len(rows),
        "eligible_rows": len(ranked),
        "excluded_rows": excluded,
        "best": selected,
        "selected_task_id": selected.get("task_id", ""),
        "models": [_model_option_payload(row, index, direction) for index, row in enumerate(ranked, start=1)],
        "prediction_summary": _prediction_summary(Path(str(selected.get("task_dir", ""))) / "predictions.csv"),
    }


def _model_result_authenticity(row: dict[str, str]) -> dict[str, object]:
    reasons: list[str] = []
    task_dir = Path(str(row.get("task_dir", ""))).expanduser()
    if not task_dir.exists():
        reasons.append("task directory is missing")
    predictions = task_dir / "predictions.csv"
    if not predictions.exists():
        reasons.append("predictions.csv is missing")
    checkpoint_value = str(row.get("checkpoint", "")).strip()
    checkpoint = Path(checkpoint_value).expanduser() if checkpoint_value else task_dir / "checkpoints" / "best.pt"
    if not checkpoint.exists():
        reasons.append("checkpoint is missing")
    else:
        try:
            checkpoint_size = checkpoint.stat().st_size
        except OSError:
            checkpoint_size = 0
        if checkpoint_size < 1024:
            reasons.append("checkpoint is too small to be a trained model weight file")
        try:
            head = checkpoint.read_bytes()[:512].lower()
        except OSError:
            head = b""
        if b"placeholder" in head or b"demo fixture" in head:
            reasons.append("checkpoint is a placeholder")
    stdout_path = task_dir / "logs" / "queue_stdout.log"
    if stdout_path.exists():
        try:
            stdout = stdout_path.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            stdout = ""
        if "demo fixture" in stdout or "marked succeeded for ui walkthrough" in stdout:
            reasons.append("queue log says this is a demo fixture")
    if str(row.get("dataset_hash", "")).lower() in {"demo-good-route", "demo_fixture"}:
        reasons.append("dataset hash is marked as demo fixture")
    return {"is_real": not reasons, "reasons": reasons}


def _model_option_payload(row: dict[str, str], rank: int, direction: str) -> dict[str, object]:
    return {
        "rank": rank,
        "task_id": row.get("task_id", ""),
        "task": row.get("task", ""),
        "window_id": row.get("window_id", ""),
        "preprocess_id": row.get("preprocess_id", ""),
        "model_id": row.get("model_id", ""),
        "pooling_id": row.get("pooling_id", ""),
        "activation": row.get("activation", ""),
        "kernel_size": row.get("kernel_size", ""),
        "dropout": row.get("dropout", ""),
        "augmentation_id": row.get("augmentation_id", ""),
        "augmentation_method": row.get("augmentation_method", ""),
        "augmentation_multiplier": row.get("augmentation_multiplier", ""),
        "augmentation_multiplier_label": row.get("augmentation_multiplier_label", ""),
        "learning_rate": row.get("learning_rate", ""),
        "weight_decay": row.get("weight_decay", ""),
        "batch_size": row.get("batch_size", ""),
        "epochs": row.get("epochs", ""),
        "seed": row.get("seed", ""),
        "loss_id": row.get("loss_id", ""),
        "metric_name": row.get("metric_name", ""),
        "metric_value": row.get("metric_value", ""),
        "direction": direction,
    }


def _read_registry_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _row_has_metric(row: dict[str, str], metric_name: str | None) -> bool:
    if row.get("status") != "succeeded":
        return False
    if metric_name and row.get("metric_name") != metric_name:
        return False
    try:
        value = float(row.get("metric_value", ""))
    except ValueError:
        return False
    return math.isfinite(value) and bool(row.get("metric_name"))


def _metric_direction(metric_name: str, direction: str) -> str:
    if direction in {"min", "max"}:
        return direction
    lowered = metric_name.lower()
    if any(token in lowered for token in ["rmse", "mae", "mse", "loss", "error"]):
        return "min"
    return "max"


def _prediction_summary(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"kind": "none", "path": str(path), "points": []}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    numeric: list[tuple[float, float]] = []
    for row in rows:
        try:
            numeric.append((float(row.get("y_true", "")), float(row.get("y_pred", ""))))
        except ValueError:
            numeric = []
            break
    if numeric:
        y_true = [item[0] for item in numeric]
        mean_true = sum(y_true) / len(y_true)
        ss_res = sum((truth - pred) ** 2 for truth, pred in numeric)
        ss_tot = sum((truth - mean_true) ** 2 for truth in y_true)
        rmse = math.sqrt(ss_res / len(numeric))
        mae = sum(abs(truth - pred) for truth, pred in numeric) / len(numeric)
        r2 = 1.0 - ss_res / ss_tot if ss_tot else None
        return {
            "kind": "regression",
            "path": str(path),
            "n": len(numeric),
            "r2": r2,
            "rmse": rmse,
            "mae": mae,
            "points": [{"true": truth, "pred": pred} for truth, pred in numeric[:80]],
        }
    correct = 0
    counts: Counter[str] = Counter()
    for row in rows:
        truth = str(row.get("y_true", ""))
        pred = str(row.get("y_pred", ""))
        correct += int(truth == pred)
        counts[f"{truth} -> {pred}"] += 1
    return {
        "kind": "classification",
        "path": str(path),
        "n": len(rows),
        "accuracy": correct / len(rows) if rows else None,
        "confusion": dict(sorted(counts.items())),
        "points": [{"true": row.get("y_true", ""), "pred": row.get("y_pred", "")} for row in rows[:80]],
    }


def _bad_request(exc: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=f"{type(exc).__name__}: {exc}")


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("spectral_core.api.app:create_app", factory=True, host="127.0.0.1", port=8765)


if __name__ == "__main__":
    main()
