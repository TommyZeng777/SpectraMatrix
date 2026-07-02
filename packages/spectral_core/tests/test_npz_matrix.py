import json
import tempfile
import unittest
from pathlib import Path

from spectral_core.matrix import apply_full_factorial_design


class NpzMatrixDesignTests(unittest.TestCase):
    def test_full_factorial_without_cv_sets_single_internal_fold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "matrix.json"
            config.write_text(
                json.dumps(
                    {
                        "name": "ui_design",
                        "dataset_config": "dataset.json",
                        "fixed": {
                            "task": "binary",
                            "window_id": "W1",
                            "model_id": "cnn3",
                        },
                        "grid": {
                            "cv_fold": [1, 2],
                            "activation_id": ["relu", "gelu"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = apply_full_factorial_design(
                base_config_path=config,
                factors=[{"key": "activation_id", "values": ["relu", "gelu"]}],
                output_dir=root / "generated",
            )

            generated = json.loads(result.config_path.read_text(encoding="utf-8"))
            self.assertEqual(generated["fixed"]["cv_fold"], 1)
            self.assertNotIn("cv_fold", generated["grid"])
            self.assertEqual(result.preview.total_combinations, 2)
            self.assertEqual(result.preview.formula, "activation_id(2)")

    def test_full_factorial_fixed_override_updates_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "matrix.json"
            config.write_text(
                json.dumps(
                    {
                        "name": "ui_design",
                        "dataset_config": "dataset.json",
                        "fixed": {
                            "task": "binary",
                            "window_id": "W1",
                            "model_id": "cnn3",
                        },
                        "grid": {
                            "activation_id": ["relu", "gelu"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = apply_full_factorial_design(
                base_config_path=config,
                factors=[{"key": "activation_id", "values": ["relu", "gelu"]}],
                output_dir=root / "generated",
                fixed_overrides={"task": "ppm"},
            )

            generated = json.loads(result.config_path.read_text(encoding="utf-8"))
            self.assertEqual(generated["fixed"]["task"], "ppm")
            self.assertNotIn("task", generated["grid"])
            self.assertEqual(result.preview.fixed["task"], "ppm")
            self.assertEqual(result.preview.total_combinations, 2)

    def test_reapplying_full_factorial_preserves_required_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "matrix.json"
            config.write_text(
                json.dumps(
                    {
                        "name": "ui_design_full_factorial",
                        "dataset_config": "dataset.json",
                        "fixed": {
                            "channels": [16, 32],
                            "kernel_size": 5,
                        },
                        "grid": {
                            "task": ["ppm", "binary"],
                            "cv_fold": [5],
                            "window_id": ["W1", "W2"],
                            "activation_id": ["relu", "gelu"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = apply_full_factorial_design(
                base_config_path=config,
                factors=[{"key": "activation_id", "values": ["relu"]}],
                output_dir=root / "generated",
                fixed_overrides={"task": "ppm"},
            )

            generated = json.loads(result.config_path.read_text(encoding="utf-8"))
            self.assertEqual(generated["name"], "ui_design_full_factorial")
            self.assertEqual(generated["fixed"]["window_id"], "W1")
            self.assertNotIn("window_id", generated["grid"])
            self.assertEqual(result.preview.total_combinations, 1)

    def test_full_factorial_fixed_dataset_config_overrides_template_dataset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template_dataset = root / "template_dataset.json"
            imported_dataset = root / "imported_dataset.json"
            for path in [template_dataset, imported_dataset]:
                path.write_text("{}", encoding="utf-8")
            config = root / "matrix.json"
            config.write_text(
                json.dumps(
                    {
                        "name": "ui_design",
                        "dataset_config": str(template_dataset),
                        "fixed": {
                            "task": "binary",
                            "window_id": "W1",
                            "model_id": "cnn3",
                        },
                        "grid": {
                            "activation_id": ["relu"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = apply_full_factorial_design(
                base_config_path=config,
                factors=[{"key": "activation_id", "values": ["relu"]}],
                output_dir=root / "generated",
                fixed_overrides={"dataset_config": str(imported_dataset)},
            )

            generated = json.loads(result.config_path.read_text(encoding="utf-8"))
            self.assertEqual(Path(generated["dataset_config"]), imported_dataset)
            self.assertEqual(result.preview.dataset_config, imported_dataset)

    def test_full_factorial_auto_windows_generate_dataset_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "dataset.json"
            windows = root / "band_windows.csv"
            windows.write_text(
                "window_id,start_nm,end_nm\nWFULL_500_2500,500,2500\n",
                encoding="utf-8",
            )
            dataset.write_text(
                json.dumps(
                    {
                        "format": "npz_plus_labels",
                        "paths_relative_to_this_file": True,
                        "spectra_matrix": "x.npz",
                        "labels": "labels.csv",
                        "split": "split.csv",
                        "cv_folds": "cv.csv",
                        "band_windows": "band_windows.csv",
                    }
                ),
                encoding="utf-8",
            )
            config = root / "matrix.json"
            config.write_text(
                json.dumps(
                    {
                        "name": "ui_design",
                        "dataset_config": str(dataset),
                        "fixed": {
                            "task": "binary",
                            "cv_fold": 1,
                            "window_id": "WFULL_500_2500",
                            "model_id": "cnn3",
                        },
                        "grid": {
                            "activation_id": ["relu"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = apply_full_factorial_design(
                base_config_path=config,
                factors=[
                    {"key": "window_id", "values": ["AUTO5_1", "AUTO5_5"]},
                    {"key": "activation_id", "values": ["relu"]},
                ],
                output_dir=root / "generated",
            )

            generated = json.loads(result.config_path.read_text(encoding="utf-8"))
            generated_dataset = Path(generated["dataset_config"])
            self.assertTrue(generated_dataset.exists())
            generated_dataset_data = json.loads(generated_dataset.read_text(encoding="utf-8"))
            generated_windows = Path(generated_dataset_data["band_windows"])
            self.assertTrue(generated_windows.exists())
            text = generated_windows.read_text(encoding="utf-8-sig")
            self.assertIn("AUTO5_1", text)
            self.assertIn("AUTO5_5", text)
            self.assertEqual(result.preview.total_combinations, 2)

    def test_full_factorial_adds_full_window_alias_for_legacy_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "dataset.json"
            windows = root / "band_windows.csv"
            windows.write_text(
                "window_id,start_nm,end_nm\nW_FULL,500,2500\n",
                encoding="utf-8",
            )
            dataset.write_text(
                json.dumps(
                    {
                        "format": "npz_plus_labels",
                        "paths_relative_to_this_file": True,
                        "spectra_matrix": "x.npz",
                        "labels": "labels.csv",
                        "split": "split.csv",
                        "cv_folds": "cv.csv",
                        "band_windows": "band_windows.csv",
                    }
                ),
                encoding="utf-8",
            )
            config = root / "matrix.json"
            config.write_text(
                json.dumps(
                    {
                        "name": "ui_design",
                        "dataset_config": str(dataset),
                        "fixed": {
                            "task": "binary",
                            "cv_fold": 1,
                            "window_id": "WFULL_500_2500",
                            "model_id": "cnn3",
                        },
                        "grid": {
                            "activation_id": ["relu"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = apply_full_factorial_design(
                base_config_path=config,
                factors=[{"key": "activation_id", "values": ["relu"]}],
                output_dir=root / "generated",
            )

            generated = json.loads(result.config_path.read_text(encoding="utf-8"))
            generated_dataset = Path(generated["dataset_config"])
            generated_dataset_data = json.loads(generated_dataset.read_text(encoding="utf-8"))
            generated_windows = Path(generated_dataset_data["band_windows"])
            text = generated_windows.read_text(encoding="utf-8-sig")
            self.assertIn("W_FULL", text)
            self.assertIn("WFULL_500_2500", text)
            self.assertEqual(result.preview.dataset_config, generated_dataset)


if __name__ == "__main__":
    unittest.main()
