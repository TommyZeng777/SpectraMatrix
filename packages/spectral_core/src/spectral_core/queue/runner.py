from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class QueueResult:
    tasks_dir: Path
    selected: int
    executed: int
    skipped: int
    succeeded: int
    failed: int
    dry_run: bool
    task_ids: list[str] = field(default_factory=list)
    cancelled: bool = False


def run_queue(
    tasks_dir: Path,
    max_tasks: int | None = None,
    rerun_failed: bool = False,
    dry_run: bool = False,
    should_stop: Callable[[], bool] | None = None,
) -> QueueResult:
    if not tasks_dir.exists():
        raise FileNotFoundError(tasks_dir)
    task_dirs = sorted(path for path in tasks_dir.iterdir() if path.is_dir())
    selected: list[Path] = []
    skipped = 0
    for task_dir in task_dirs:
        status = _status(task_dir)
        if status == "succeeded":
            skipped += 1
            continue
        if status == "failed" and not rerun_failed:
            skipped += 1
            continue
        selected.append(task_dir)
        if max_tasks is not None and len(selected) >= max_tasks:
            break

    if dry_run:
        return QueueResult(
            tasks_dir=tasks_dir,
            selected=len(selected),
            executed=0,
            skipped=skipped,
            succeeded=0,
            failed=0,
            dry_run=True,
            task_ids=[path.name for path in selected],
        )

    executed = 0
    succeeded = 0
    failed = 0
    cancelled = False
    for task_dir in selected:
        if should_stop and should_stop():
            cancelled = True
            break
        executed += 1
        result = _run_task(task_dir, should_stop=should_stop)
        if result == -15:
            cancelled = True
            break
        if result == 0:
            succeeded += 1
        else:
            failed += 1

    return QueueResult(
        tasks_dir=tasks_dir,
        selected=len(selected),
        executed=executed,
        skipped=skipped,
        succeeded=succeeded,
        failed=failed,
        dry_run=False,
        task_ids=[path.name for path in selected],
        cancelled=cancelled,
    )


def _status(task_dir: Path) -> str:
    status_path = task_dir / "status.json"
    if not status_path.exists():
        return "pending"
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "unknown"
    return str(payload.get("status", "unknown"))


def _run_task(task_dir: Path, should_stop: Callable[[], bool] | None = None) -> int:
    task_dir = task_dir.resolve()
    run_script = task_dir / "run.sh"
    if not run_script.exists():
        _write_status(task_dir, {"status": "failed", "error": "Missing run.sh"})
        return 1
    logs_dir = task_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    _write_status(task_dir, {"status": "running", "started_at": time.time()})
    with (logs_dir / "queue_stdout.log").open("w", encoding="utf-8") as stdout_handle:
        with (logs_dir / "queue_stderr.log").open("w", encoding="utf-8") as stderr_handle:
            process = subprocess.Popen(
                [str(run_script)],
                cwd=task_dir,
                stdout=stdout_handle,
                stderr=stderr_handle,
            )
            while process.poll() is None:
                if should_stop and should_stop():
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                    _write_status(
                        task_dir,
                        {
                            "status": "cancelled",
                            "finished_at": time.time(),
                            "message": "Stopped by user request.",
                        },
                    )
                    return -15
                time.sleep(0.25)
            returncode = int(process.returncode or 0)
    if returncode != 0 and _status(task_dir) not in {"failed", "succeeded", "cancelled"}:
        _write_status(
            task_dir,
            {
                "status": "failed",
                "returncode": returncode,
                "finished_at": time.time(),
            },
        )
    return returncode


def _write_status(task_dir: Path, payload: dict) -> None:
    (task_dir / "status.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
