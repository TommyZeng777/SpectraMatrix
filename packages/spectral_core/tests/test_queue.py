import json
import tempfile
import unittest
from pathlib import Path

from spectral_core.queue import run_queue


class QueueTests(unittest.TestCase):
    def test_run_queue_executes_pending_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = _make_task(Path(tmp), "task_000001", "pending", 0)

            result = run_queue(Path(tmp))

            self.assertEqual(result.executed, 1)
            self.assertEqual(result.succeeded, 1)
            status = json.loads((task / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["status"], "succeeded")
            self.assertTrue((task / "logs" / "queue_stdout.log").exists())

    def test_run_queue_skips_succeeded_and_failed_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_task(root, "task_done", "succeeded", 0)
            _make_task(root, "task_failed", "failed", 0)

            result = run_queue(root)

            self.assertEqual(result.executed, 0)
            self.assertEqual(result.skipped, 2)

    def test_run_queue_can_rerun_failed_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = _make_task(root, "task_failed", "failed", 0)

            result = run_queue(root, rerun_failed=True)

            self.assertEqual(result.executed, 1)
            self.assertEqual(result.succeeded, 1)
            status = json.loads((task / "status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["status"], "succeeded")


def _make_task(root: Path, name: str, status: str, exit_code: int) -> Path:
    task = root / name
    task.mkdir()
    (task / "manifest.json").write_text(
        json.dumps({"task_id": name, "task_type": "test"}, indent=2) + "\n",
        encoding="utf-8",
    )
    (task / "status.json").write_text(json.dumps({"status": status}, indent=2) + "\n", encoding="utf-8")
    script = task / "run.sh"
    script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"python3 - <<'PY'\n"
        "import json\n"
        "from pathlib import Path\n"
        "Path('status.json').write_text(json.dumps({'status': 'succeeded'}, indent=2) + '\\n')\n"
        "PY\n"
        f"exit {exit_code}\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return task


if __name__ == "__main__":
    unittest.main()

