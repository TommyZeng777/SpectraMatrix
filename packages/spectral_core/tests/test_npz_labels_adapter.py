import importlib.util
import csv
import json
import py_compile
import sys
import tempfile
import unittest
from pathlib import Path

from spectral_core.adapters import create_npz_cnn1d_task, inspect_npz_plus_labels_config
from spectral_core.matrix import create_npz_cnn1d_matrix


HAS_NUMPY = importlib.util.find_spec("numpy") is not None


@unittest.skipUnless(HAS_NUMPY, "numpy is not installed")
class NpzLabelsAdapterTests(unittest.TestCase):
    def test_inspects_npz_plus_labels_config(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            np.savez_compressed(
                data_dir / "spectra.npz",
                x=np.zeros((3, 4), dtype=np.float32),
                wavelengths=np.array([500, 501, 502, 503], dtype=np.float32),
                sample_ids=np.array(["S1", "S2", "S3"]),
            )
            _write_text(
                data_dir / "labels.csv",
                "sample_id,sample_link_code,ppm_mg_kg,high_risk_gt500_label,three_class_label\n"
                "S1,G1,10,0,0\n"
                "S2,G2,600,1,1\n"
                "S3,G3,1200,1,2\n",
            )
            _write_text(
                data_dir / "split.csv",
                "sample_id,sample_link_code,split\n"
                "S1,G1,dev\n"
                "S2,G2,dev\n"
                "S3,G3,test\n",
            )
            _write_text(
                data_dir / "cv.csv",
                "sample_id,sample_link_code,cv_fold\n"
                "S1,G1,1\n"
                "S2,G2,2\n",
            )
            _write_text(data_dir / "windows.csv", "window_id,start_nm,end_nm\nW1,500,503\n")
            config_path = _write_config(root, data_dir)

            result = inspect_npz_plus_labels_config(config_path, root / "inspect")

            self.assertEqual(result.status, "ok")
            self.assertEqual(result.sample_count, 3)
            self.assertEqual(result.wavelength_count, 4)
            self.assertEqual(result.split_counts, {"dev": 2, "test": 1})
            self.assertEqual(result.cv_fold_counts, {"1": 1, "2": 1})
            self.assertTrue((root / "inspect" / "dataset_inspection.json").exists())
            manifest = json.loads((root / "inspect" / "dataset_inspection.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["target_columns"]["regression"], "ppm_mg_kg")

    def test_rejects_cv_ids_that_do_not_match_development_split(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            np.savez_compressed(
                data_dir / "spectra.npz",
                x=np.zeros((3, 2), dtype=np.float32),
                wavelengths=np.array([500, 501], dtype=np.float32),
                sample_ids=np.array(["S1", "S2", "S3"]),
            )
            _write_text(
                data_dir / "labels.csv",
                "sample_id,sample_link_code,ppm_mg_kg\n"
                "S1,G1,10\n"
                "S2,G2,20\n"
                "S3,G3,30\n",
            )
            _write_text(
                data_dir / "split.csv",
                "sample_id,sample_link_code,split\n"
                "S1,G1,dev\n"
                "S2,G2,dev\n"
                "S3,G3,test\n",
            )
            _write_text(
                data_dir / "cv.csv",
                "sample_id,sample_link_code,cv_fold\n"
                "S1,G1,1\n"
                "S3,G3,2\n",
            )
            _write_text(data_dir / "windows.csv", "window_id,start_nm,end_nm\nW1,500,501\n")
            config_path = _write_config(root, data_dir)

            with self.assertRaisesRegex(ValueError, "cv_folds sample IDs must match development split"):
                inspect_npz_plus_labels_config(config_path)

    def test_creates_portable_npz_cnn1d_task_folder(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            np.savez_compressed(
                data_dir / "spectra.npz",
                x=np.arange(20, dtype=np.float32).reshape(4, 5),
                wavelengths=np.array([500, 501, 502, 503, 504], dtype=np.float32),
                sample_ids=np.array(["S1", "S2", "S3", "S4"]),
            )
            _write_text(
                data_dir / "labels.csv",
                "sample_id,sample_link_code,ppm_mg_kg,high_risk_gt500_label,three_class_label\n"
                "S1,G1,10,0,0\n"
                "S2,G2,20,0,0\n"
                "S3,G3,600,1,1\n"
                "S4,G4,1200,1,2\n",
            )
            _write_text(
                data_dir / "split.csv",
                "sample_id,sample_link_code,split\n"
                "S1,G1,dev\n"
                "S2,G2,dev\n"
                "S3,G3,dev\n"
                "S4,G4,test\n",
            )
            _write_text(
                data_dir / "cv.csv",
                "sample_id,sample_link_code,cv_fold\n"
                "S1,G1,1\n"
                "S2,G2,2\n"
                "S3,G3,2\n",
            )
            _write_text(data_dir / "windows.csv", "window_id,start_nm,end_nm\nW1,501,503\n")
            config_path = _write_config(root, data_dir)

            result = create_npz_cnn1d_task(
                config_path=config_path,
                task_id="smoke_npz_task",
                output_dir=root / "tasks",
                task="binary",
                cv_fold=1,
                window_id="W1",
                augmentation_id="AUG1",
                augmentation_multiplier=2,
                epochs=1,
                batch_size=2,
                seed=7,
            )

            self.assertEqual(result.train_size, 2)
            self.assertEqual(result.val_size, 1)
            self.assertEqual(result.feature_count, 3)
            self.assertTrue((result.task_dir / "train.py").exists())
            self.assertTrue((result.task_dir / "run.sh").exists())
            self.assertTrue((result.task_dir / "task_data.npz").exists())
            run_script = (result.task_dir / "run.sh").read_text(encoding="utf-8")
            self.assertIn(sys.executable, run_script)
            self.assertIn("${PYTHON:-", run_script)
            py_compile.compile(str(result.task_dir / "train.py"), doraise=True)
            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["task"], "binary")
            self.assertEqual(manifest["cv_fold"], 1)
            self.assertEqual(manifest["target_column"], "high_risk_gt500_label")
            self.assertEqual(manifest["augmentation_id"], "AUG1")
            self.assertEqual(manifest["augmentation_method"], "加噪增强")
            self.assertEqual(manifest["augmentation_multiplier"], 2)
            self.assertEqual(manifest["augmentation_multiplier_label"], "2× 训练集扩增")
            self.assertEqual(manifest["augmented_train_size"], 4)
            config = json.loads(result.config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["augmentation"]["augmentation_id"], "AUG1")
            self.assertEqual(config["augmentation"]["method"], "加噪增强")
            self.assertEqual(config["augmentation"]["multiplier"], 2)
            self.assertEqual(config["augmentation"]["multiplier_label"], "2× 训练集扩增")
            self.assertEqual(config["augmentation"]["apply_to"], "training_only")
            task_data = np.load(result.data_path, allow_pickle=False)
            self.assertEqual(task_data["x_train"].shape, (2, 3))
            self.assertEqual(task_data["x_val"].shape, (1, 3))

            (result.task_dir / "logs").mkdir()
            (result.task_dir / "logs" / "error.log").write_text("stale failure", encoding="utf-8")
            (result.task_dir / "summary.json").write_text("stale summary", encoding="utf-8")

            create_npz_cnn1d_task(
                config_path=config_path,
                task_id="smoke_npz_task",
                output_dir=root / "tasks",
                task="binary",
                cv_fold=1,
                window_id="W1",
                epochs=1,
                batch_size=2,
                seed=7,
            )

            self.assertFalse((result.task_dir / "logs" / "error.log").exists())
            self.assertFalse((result.task_dir / "summary.json").exists())

    def test_creates_tri_class_task_from_configured_numeric_bins(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            np.savez_compressed(
                data_dir / "spectra.npz",
                x=np.arange(20, dtype=np.float32).reshape(4, 5),
                wavelengths=np.array([500, 501, 502, 503, 504], dtype=np.float32),
                sample_ids=np.array(["S1", "S2", "S3", "S4"]),
            )
            _write_text(
                data_dir / "labels.csv",
                "sample_id,sample_link_code,ppm_mg_kg,high_risk_gt500_label,three_class_label\n"
                "S1,G1,0,0,0\n"
                "S2,G2,500,0,0\n"
                "S3,G3,1000,1,1\n"
                "S4,G4,1200,1,2\n",
            )
            _write_text(
                data_dir / "split.csv",
                "sample_id,sample_link_code,split\n"
                "S1,G1,dev\n"
                "S2,G2,dev\n"
                "S3,G3,dev\n"
                "S4,G4,test\n",
            )
            _write_text(
                data_dir / "cv.csv",
                "sample_id,sample_link_code,cv_fold\n"
                "S1,G1,1\n"
                "S2,G2,2\n"
                "S3,G3,2\n",
            )
            _write_text(data_dir / "windows.csv", "window_id,start_nm,end_nm\nW1,501,503\n")
            config_path = _write_config(root, data_dir)
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["targets"]["tri_class"] = {
                "mode": "derive_from_numeric",
                "source_column": "ppm_mg_kg",
                "boundary": "left_closed_right_open",
                "bins": [
                    {"label": 0, "name": "low", "min": 0, "max": 500},
                    {"label": 1, "name": "mid", "min": 500, "max": 1000},
                    {"label": 2, "name": "high", "min": 1000, "max": None},
                ],
                "default_metric": "val_macro_f1",
                "higher_is_better": True,
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")

            result = create_npz_cnn1d_task(
                config_path=config_path,
                task_id="tri_bins_task",
                output_dir=root / "tasks",
                task="tri_class",
                cv_fold=1,
                window_id="W1",
                epochs=1,
            )

            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            task_data = np.load(result.data_path, allow_pickle=False)
            self.assertEqual(manifest["target_column"], "ppm_mg_kg")
            self.assertEqual(manifest["target_policy"]["mode"], "derive_from_numeric")
            self.assertEqual(task_data["label_names"].tolist(), ["low", "mid", "high"])
            self.assertEqual(task_data["y_train"].tolist(), [1, 2])
            self.assertEqual(task_data["y_val"].tolist(), [0])

    def test_rejects_non_contiguous_derived_class_labels(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            np.savez_compressed(
                data_dir / "spectra.npz",
                x=np.arange(20, dtype=np.float32).reshape(4, 5),
                wavelengths=np.array([500, 501, 502, 503, 504], dtype=np.float32),
                sample_ids=np.array(["S1", "S2", "S3", "S4"]),
            )
            _write_text(
                data_dir / "labels.csv",
                "sample_id,sample_link_code,ppm_mg_kg,high_risk_gt500_label,three_class_label\n"
                "S1,G1,0,0,0\n"
                "S2,G2,500,0,0\n"
                "S3,G3,1000,1,1\n"
                "S4,G4,1200,1,2\n",
            )
            _write_text(
                data_dir / "split.csv",
                "sample_id,sample_link_code,split\n"
                "S1,G1,dev\n"
                "S2,G2,dev\n"
                "S3,G3,dev\n"
                "S4,G4,test\n",
            )
            _write_text(
                data_dir / "cv.csv",
                "sample_id,sample_link_code,cv_fold\n"
                "S1,G1,1\n"
                "S2,G2,2\n"
                "S3,G3,2\n",
            )
            _write_text(data_dir / "windows.csv", "window_id,start_nm,end_nm\nW1,501,503\n")
            config_path = _write_config(root, data_dir)
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["targets"]["tri_class"] = {
                "mode": "derive_from_numeric",
                "source_column": "ppm_mg_kg",
                "bins": [
                    {"label": 0, "name": "low", "min": 0, "max": 500},
                    {"label": 2, "name": "mid", "min": 500, "max": 1000},
                    {"label": 3, "name": "high", "min": 1000, "max": None},
                ],
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Derived class labels must be contiguous"):
                inspect_npz_plus_labels_config(config_path)

    def test_creates_npz_cnn1d_matrix(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            np.savez_compressed(
                data_dir / "spectra.npz",
                x=np.arange(20, dtype=np.float32).reshape(4, 5),
                wavelengths=np.array([500, 501, 502, 503, 504], dtype=np.float32),
                sample_ids=np.array(["S1", "S2", "S3", "S4"]),
            )
            _write_text(
                data_dir / "labels.csv",
                "sample_id,sample_link_code,ppm_mg_kg,high_risk_gt500_label,three_class_label\n"
                "S1,G1,10,0,0\n"
                "S2,G2,20,0,0\n"
                "S3,G3,600,1,1\n"
                "S4,G4,1200,1,2\n",
            )
            _write_text(
                data_dir / "split.csv",
                "sample_id,sample_link_code,split\n"
                "S1,G1,dev\n"
                "S2,G2,dev\n"
                "S3,G3,dev\n"
                "S4,G4,test\n",
            )
            _write_text(
                data_dir / "cv.csv",
                "sample_id,sample_link_code,cv_fold\n"
                "S1,G1,1\n"
                "S2,G2,2\n"
                "S3,G3,2\n",
            )
            _write_text(data_dir / "windows.csv", "window_id,start_nm,end_nm\nW1,501,503\n")
            dataset_config = _write_config(root, data_dir)
            matrix_config = root / "matrix.json"
            matrix_config.write_text(
                json.dumps(
                    {
                        "name": "npz_matrix_test",
                        "dataset_config": str(dataset_config),
                        "fixed": {
                            "task": "binary",
                            "window_id": "W1",
                            "preprocess_id": "raw_standard",
                            "model_id": "cnn3",
                            "pooling_id": "POOL0",
                            "epochs": 1,
                        },
                        "grid": {
                            "cv_fold": [1, 2],
                            "activation_id": ["relu", "gelu"],
                            "augmentation_id": ["AUG0", "AUG1"],
                            "augmentation_multiplier": [1, 2],
                            "seed": [7],
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = create_npz_cnn1d_matrix(matrix_config, root / "matrix_out")

            self.assertEqual(result.task_count, 16)
            self.assertTrue((result.tasks_dir / "npz_matrix_test_task_000001" / "task_data.npz").exists())
            py_compile.compile(str(result.tasks_dir / "npz_matrix_test_task_000001" / "train.py"), doraise=True)
            with result.task_index_path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 16)
            self.assertEqual(rows[0]["activation_id"], "relu")
            self.assertEqual(rows[0]["augmentation_id"], "AUG0")
            self.assertEqual(rows[0]["augmentation_method"], "不使用数据增强")
            self.assertEqual(rows[0]["augmentation_multiplier_label"], "不扩增")
            self.assertEqual(rows[2]["augmentation_id"], "AUG1")
            self.assertEqual(rows[2]["augmentation_method"], "加噪增强")
            self.assertEqual(rows[2]["augmentation_multiplier_label"], "1× 训练集扩增")
            self.assertEqual(rows[0]["feature_count"], "3")


def _write_config(root: Path, data_dir: Path) -> Path:
    config = {
        "format": "npz_plus_labels",
        "paths_relative_to_this_file": True,
        "spectra_matrix": str(data_dir.relative_to(root) / "spectra.npz"),
        "labels": str(data_dir.relative_to(root) / "labels.csv"),
        "split": str(data_dir.relative_to(root) / "split.csv"),
        "cv_folds": str(data_dir.relative_to(root) / "cv.csv"),
        "band_windows": str(data_dir.relative_to(root) / "windows.csv"),
        "identity": {"row_key": "sample_id", "group_key": "sample_link_code"},
        "targets": {
            "regression": {"column": "ppm_mg_kg"},
            "binary": {"column": "high_risk_gt500_label", "default_metric": "val_accuracy", "higher_is_better": True},
            "tri_class": {"column": "three_class_label", "default_metric": "val_accuracy", "higher_is_better": True},
        },
        "split_policy": {
            "split_column": "split",
            "development_value": "dev",
            "locked_test_value": "test",
            "cv_fold_column": "cv_fold",
        },
    }
    path = root / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
