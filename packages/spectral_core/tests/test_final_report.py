import csv
import json
import tempfile
import unittest
from pathlib import Path

from spectral_core.reports import generate_final_report


class FinalReportTests(unittest.TestCase):
    def test_generate_final_report_summarizes_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset_manifest = root / "dataset_manifest.json"
            matrix_manifest = root / "matrix_manifest.json"
            registry = root / "run_registry.csv"
            candidates = root / "model_candidates.csv"
            report = root / "report.md"
            dataset_manifest.write_text(
                json.dumps(
                    {
                        "dataset_hash": "abc123",
                        "link_key": "linkcode",
                        "target_column": "so2_ppm",
                        "spectra_rows": 4,
                        "supervision_rows": 4,
                        "joined_rows": 4,
                        "spectra_only_count": 0,
                        "supervision_only_count": 0,
                    }
                ),
                encoding="utf-8",
            )
            matrix_manifest.write_text(
                json.dumps({"name": "m1", "task_count": 2, "tasks_dir": "tasks", "grid_keys": ["activation"]}),
                encoding="utf-8",
            )
            _write_csv(
                registry,
                [
                    {"task_id": "a", "task_type": "cnn1d_training", "status": "succeeded", "metric_name": "val_score", "metric_value": "0.9"},
                    {"task_id": "b", "task_type": "cnn1d_training", "status": "failed", "metric_name": "", "metric_value": ""},
                ],
            )
            _write_csv(
                candidates,
                [
                    {"rank": "1", "task_id": "a", "metric_name": "val_score", "metric_value": "0.9", "checkpoint": "best.pt"},
                ],
            )

            result = generate_final_report(dataset_manifest, registry, candidates, report, matrix_manifest)

            self.assertEqual(result.registry_rows, 2)
            self.assertEqual(result.candidate_rows, 1)
            text = report.read_text(encoding="utf-8")
            self.assertIn("dataset_hash: `abc123`", text)
            self.assertIn("status_counts: `failed=1, succeeded=1`", text)
            self.assertIn("| 1 | a |  |  |  |  |  |  | val_score | 0.9", text)

    def test_generate_final_report_summarizes_npz_dataset_inspection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset_manifest = root / "dataset_inspection.json"
            matrix_manifest = root / "matrix_manifest.json"
            registry = root / "run_registry.csv"
            candidates = root / "model_candidates.csv"
            report = root / "report.md"
            dataset_manifest.write_text(
                json.dumps(
                    {
                        "format": "npz_plus_labels",
                        "shape": {"n_samples": 154, "n_wavelengths": 2001},
                        "identity": {"row_key": "sample_id", "group_key": "sample_link_code"},
                        "split_counts": {"dev": 130, "test": 24},
                        "cv_fold_counts": {"1": 25, "2": 26},
                        "target_columns": {"binary": "high_risk_gt500_label"},
                        "window_count": 16,
                    }
                ),
                encoding="utf-8",
            )
            matrix_manifest.write_text(
                json.dumps({"name": "npz_m1", "task_count": 1, "tasks_dir": "tasks", "grid_keys": ["cv_fold"]}),
                encoding="utf-8",
            )
            _write_csv(
                registry,
                [
                    {
                        "task_id": "npz_a",
                        "task_type": "npz_cnn1d_training",
                        "status": "succeeded",
                        "metric_name": "val_balanced_accuracy",
                        "metric_value": "0.5",
                    },
                ],
            )
            _write_csv(
                candidates,
                [
                    {
                        "rank": "1",
                        "task_id": "npz_a",
                        "metric_name": "val_balanced_accuracy",
                        "metric_value": "0.5",
                        "checkpoint": "best.pt",
                    },
                ],
            )

            generate_final_report(dataset_manifest, registry, candidates, report, matrix_manifest)

            text = report.read_text(encoding="utf-8")
            self.assertIn("format: `npz_plus_labels`", text)
            self.assertIn("samples: 154", text)
            self.assertIn("split_counts: `dev=130, test=24`", text)


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "rank",
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
            writer.writerow({field: row.get(field, "") for field in fieldnames})


if __name__ == "__main__":
    unittest.main()
