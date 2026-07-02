import csv
import tempfile
import unittest
from pathlib import Path

from spectral_core.reports import aggregate_matrix_results


class MatrixAggregateTests(unittest.TestCase):
    def test_aggregate_matrix_results_groups_and_ranks_max_metric(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "run_registry.csv"
            _write_registry(
                registry,
                [
                    {"task_id": "a", "status": "succeeded", "window_id": "W1", "activation": "relu", "metric_name": "val_score", "metric_value": "0.5", "cv_fold": "1"},
                    {"task_id": "b", "status": "succeeded", "window_id": "W1", "activation": "relu", "metric_name": "val_score", "metric_value": "0.7", "cv_fold": "2"},
                    {"task_id": "c", "status": "succeeded", "window_id": "W2", "activation": "gelu", "metric_name": "val_score", "metric_value": "0.9", "cv_fold": "1"},
                    {"task_id": "d", "status": "failed", "window_id": "W2", "activation": "gelu", "metric_name": "val_score", "metric_value": "1.0", "cv_fold": "2"},
                ],
            )

            result = aggregate_matrix_results(registry, root / "out", metric_name="val_score", group_by=["window_id", "activation"])

            self.assertEqual(result.eligible_rows, 3)
            self.assertEqual(result.group_count, 2)
            rows = _read_csv(result.summary_path)
            self.assertEqual(rows[0]["window_id"], "W2")
            self.assertEqual(rows[0]["mean"], "0.9")
            self.assertEqual(rows[1]["window_id"], "W1")
            self.assertEqual(rows[1]["mean"], "0.6")
            self.assertTrue(result.report_path.exists())

    def test_aggregate_matrix_results_auto_min_for_rmse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "run_registry.csv"
            _write_registry(
                registry,
                [
                    {"task_id": "a", "status": "succeeded", "window_id": "W1", "activation": "relu", "metric_name": "val_rmse", "metric_value": "2.0"},
                    {"task_id": "b", "status": "succeeded", "window_id": "W2", "activation": "relu", "metric_name": "val_rmse", "metric_value": "1.0"},
                ],
            )

            result = aggregate_matrix_results(registry, root / "out", metric_name="val_rmse", group_by=["window_id"])

            rows = _read_csv(result.summary_path)
            self.assertEqual(result.direction, "min")
            self.assertEqual(rows[0]["window_id"], "W2")


def _write_registry(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "task_id",
        "task_type",
        "task_dir",
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
        "train_size",
        "val_size",
        "feature_count",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    unittest.main()
