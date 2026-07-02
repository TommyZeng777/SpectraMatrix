import subprocess
import tempfile
import unittest
import json
from pathlib import Path

from spectral_core.binding import bind_spectrum_supervision
from spectral_core.scan import scan_runs
from spectral_core.tasks import create_cnn1d_task, create_dummy_task


class TasksScanTests(unittest.TestCase):
    def test_dummy_task_runs_and_scan_collects_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spectra = root / "spectra.csv"
            supervision = root / "supervision.csv"
            spectra.write_text(
                "linkcode,w1,w2\n"
                "S1,0.1,0.2\n"
                "S2,0.3,0.4\n",
                encoding="utf-8",
            )
            supervision.write_text(
                "linkcode,target\n"
                "S1,10\n"
                "S2,20\n",
                encoding="utf-8",
            )
            frozen = root / "frozen"
            bind_spectrum_supervision(spectra, supervision, "linkcode", "target", frozen)

            tasks_dir = root / "tasks"
            task = create_dummy_task(frozen, "task_000001", tasks_dir, metric_value=0.91)
            subprocess.run(["python3", str(task.train_script)], cwd=task.task_dir, check=True)
            result = scan_runs(tasks_dir, root / "results")

            self.assertEqual(result.scanned, 1)
            self.assertEqual(result.succeeded, 1)
            registry = result.registry_path.read_text(encoding="utf-8")
            self.assertIn("task_000001", registry)
            self.assertIn("0.91", registry)

    def test_cnn1d_task_exports_portable_training_files(self):
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

            task = create_cnn1d_task(
                dataset_dir=frozen,
                task_id="task_cnn1d_000001",
                output_dir=root / "tasks",
                target_column="label",
                task_kind="classification",
                activation="gelu",
                normalization="layer_norm",
                channels=[8],
                epochs=1,
            )
            config = json.loads(task.config_path.read_text(encoding="utf-8"))

            self.assertTrue(task.train_script.exists())
            self.assertTrue(task.run_script.exists())
            self.assertEqual(config["model"]["activation"], "gelu")
            self.assertEqual(config["model"]["normalization"], "layer_norm")
            self.assertEqual(config["model"]["channels"], [8])
            self.assertIn("torch", (task.task_dir / "requirements.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
