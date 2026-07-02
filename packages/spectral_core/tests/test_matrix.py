import csv
import json
import tempfile
import unittest
from pathlib import Path

from spectral_core.binding import bind_spectrum_supervision
from spectral_core.matrix import create_cnn1d_matrix


class MatrixTests(unittest.TestCase):
    def test_create_cnn1d_matrix_expands_grid_to_task_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spectra = root / "spectra.csv"
            supervision = root / "supervision.csv"
            spectra.write_text(
                "linkcode,w1,w2,w3,w4\n"
                "S1,0.1,0.2,0.3,0.4\n"
                "S2,0.4,0.3,0.2,0.1\n"
                "S3,0.2,0.3,0.4,0.5\n"
                "S4,0.5,0.4,0.3,0.2\n",
                encoding="utf-8",
            )
            supervision.write_text(
                "linkcode,label\n"
                "S1,a\n"
                "S2,b\n"
                "S3,a\n"
                "S4,b\n",
                encoding="utf-8",
            )
            frozen = root / "frozen"
            bind_spectrum_supervision(spectra, supervision, "linkcode", "label", frozen)
            matrix_config = root / "matrix.json"
            matrix_config.write_text(
                json.dumps(
                    {
                        "name": "cnn1d_test",
                        "fixed": {
                            "dataset_dir": str(frozen),
                            "target_column": "label",
                            "task_kind": "classification",
                            "epochs": 1,
                        },
                        "grid": {
                            "activation": ["relu", "gelu"],
                            "normalization": ["batch_norm"],
                            "channels": [[8], [8, 16]],
                            "seed": [1, 2],
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = create_cnn1d_matrix(matrix_config, root / "matrix_out")

            self.assertEqual(result.task_count, 8)
            self.assertTrue((result.tasks_dir / "cnn1d_test_task_000001" / "train.py").exists())
            with result.task_index_path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 8)
            self.assertEqual(rows[0]["activation"], "relu")
            self.assertEqual(rows[-1]["activation"], "gelu")

    def test_matrix_respects_max_tasks_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "matrix.json"
            config.write_text(
                json.dumps(
                    {
                        "fixed": {
                            "dataset_dir": str(root / "missing"),
                            "target_column": "label",
                            "task_kind": "classification",
                        },
                        "grid": {"seed": [1, 2, 3]},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "above max_tasks"):
                create_cnn1d_matrix(config, root / "out", max_tasks=2)


if __name__ == "__main__":
    unittest.main()

