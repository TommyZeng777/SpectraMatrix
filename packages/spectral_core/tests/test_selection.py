import csv
import tempfile
import unittest
from pathlib import Path

from spectral_core.selection import select_candidates


class SelectionTests(unittest.TestCase):
    def test_select_candidates_filters_failed_and_ranks_max_metric(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "run_registry.csv"
            _write_registry(
                registry,
                [
                    {"task_id": "a", "status": "succeeded", "metric_name": "val_score", "metric_value": "0.70"},
                    {"task_id": "b", "status": "failed", "metric_name": "", "metric_value": ""},
                    {"task_id": "c", "status": "succeeded", "metric_name": "val_score", "metric_value": "0.91"},
                    {"task_id": "d", "status": "succeeded", "metric_name": "val_score", "metric_value": "0.82"},
                ],
            )

            result = select_candidates(registry, root / "out", metric_name="val_score", top=2)

            self.assertEqual(result.selected_rows, 2)
            rows = _read_csv(result.candidates_path)
            self.assertEqual([row["task_id"] for row in rows], ["c", "d"])
            self.assertTrue(result.report_path.exists())

    def test_select_candidates_auto_min_for_rmse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "run_registry.csv"
            _write_registry(
                registry,
                [
                    {"task_id": "a", "status": "succeeded", "metric_name": "val_rmse", "metric_value": "2.5"},
                    {"task_id": "b", "status": "succeeded", "metric_name": "val_rmse", "metric_value": "1.2"},
                ],
            )

            result = select_candidates(registry, root / "out", metric_name="val_rmse", top=1)

            self.assertEqual(result.direction, "min")
            rows = _read_csv(result.candidates_path)
            self.assertEqual(rows[0]["task_id"], "b")


def _write_registry(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "task_id",
        "task_type",
        "task_dir",
        "status",
        "dataset_hash",
        "architecture",
        "activation",
        "normalization",
        "metric_name",
        "metric_value",
        "checkpoint",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output = {field: row.get(field, "") for field in fieldnames}
            writer.writerow(output)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    unittest.main()

