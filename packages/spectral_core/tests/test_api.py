import base64
import csv
import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path


HAS_FASTAPI = importlib.util.find_spec("fastapi") is not None


@unittest.skipUnless(HAS_FASTAPI, "fastapi is not installed")
class ApiTests(unittest.TestCase):
    def test_health(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        client = TestClient(create_app())

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_serves_static_workbench_and_defaults(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        client = TestClient(create_app())

        page = client.get("/")
        defaults = client.get("/api/workbench/defaults")

        self.assertEqual(page.status_code, 200)
        self.assertIn("SpectraMatrix", page.text)
        self.assertEqual(defaults.status_code, 200)
        self.assertIn("dataset_config", defaults.json())

    def test_serves_csv_templates(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        client = TestClient(create_app())

        spectra = client.get("/api/templates/spectra")
        supervision = client.get("/api/templates/supervision")

        self.assertEqual(spectra.status_code, 200)
        self.assertIn("sample_link_code", spectra.text)
        self.assertEqual(supervision.status_code, 200)
        self.assertIn("ppm_mg_kg", supervision.text)

    def test_import_project_file_payload(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        project_path = "/tmp/example/SpectraMatrix_Project.spectramatrix.json"
        envelope = {
            "app": "SpectraMatrix",
            "schema_version": 1,
            "format": "spectramatrix_project",
            "saved_at": "2026-07-02T00:00:00Z",
            "project": {
                "project_file": project_path,
                "dataset_code": "DEMO-DATASET",
                "tasks_dir": "/tmp/example/tasks",
            },
        }
        client = TestClient(create_app())

        response = client.post(
            "/api/project/import-file",
            json={"file": _upload_payload("demo.spectramatrix.json", json.dumps(envelope).encode("utf-8"))},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "imported")
        self.assertEqual(payload["path"], project_path)
        self.assertEqual(payload["project"]["dataset_code"], "DEMO-DATASET")

    def test_save_project_accepts_custom_filename(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            previous_cwd = Path.cwd()
            os.chdir(root)
            try:
                client = TestClient(create_app())
                response = client.post(
                    "/api/project/save",
                    json={
                        "filename": "我的演示工程",
                        "project": {
                            "name": "Demo",
                            "dataset_code": "DEMO-DATASET",
                        },
                    },
                )
            finally:
                os.chdir(previous_cwd)

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            saved_path = Path(payload["path"])
            self.assertEqual(saved_path.name, "我的演示工程.spectramatrix.json")
            self.assertEqual(saved_path.parent, root / "projects")
            envelope = json.loads(saved_path.read_text(encoding="utf-8"))
            self.assertEqual(envelope["format"], "spectramatrix_project")
            self.assertEqual(envelope["project"]["project_file"], str(saved_path))
            self.assertEqual(envelope["project"]["dataset_code"], "DEMO-DATASET")

    def test_scan_select_and_aggregate_file_workflow(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tasks = root / "tasks"
            task_dir = tasks / "task_000001"
            task_dir.mkdir(parents=True)
            _write_json(
                task_dir / "manifest.json",
                {
                    "task_id": "task_000001",
                    "task_type": "npz_cnn1d_training",
                    "dataset_hash": "abc",
                    "task": "tri_class",
                    "cv_fold": 1,
                    "window_id": "W1",
                    "preprocess_id": "raw_standard",
                    "model_id": "cnn3",
                    "pooling_id": "POOL0",
                    "architecture": "cnn1d_npz",
                    "activation": "gelu",
                    "train_size": 10,
                    "val_size": 3,
                    "feature_count": 5,
                },
            )
            _write_json(task_dir / "status.json", {"status": "succeeded"})
            _write_json(
                task_dir / "summary.json",
                {
                    "status": "succeeded",
                    "metric_name": "val_balanced_accuracy",
                    "metric_value": 0.81,
                    "checkpoint": str(task_dir / "checkpoints" / "best.pt"),
                    "activation": "gelu",
                },
            )
            client = TestClient(create_app())

            scan_response = client.post("/api/runs/scan", json={"runs": str(tasks), "out": str(root / "results")})
            self.assertEqual(scan_response.status_code, 200)
            registry = Path(scan_response.json()["registry"])
            self.assertTrue(registry.exists())

            select_response = client.post(
                "/api/candidates/select",
                json={"registry": str(registry), "out": str(root / "candidates"), "metric": "val_balanced_accuracy", "top": 1},
            )
            self.assertEqual(select_response.status_code, 200)
            self.assertEqual(select_response.json()["selected_rows"], 1)

            aggregate_response = client.post(
                "/api/matrix/aggregate",
                json={
                    "registry": str(registry),
                    "out": str(root / "aggregate"),
                    "metric": "val_balanced_accuracy",
                    "group_by": ["window_id", "activation"],
                    "direction": "max",
                },
            )
            self.assertEqual(aggregate_response.status_code, 200)
            self.assertEqual(aggregate_response.json()["group_count"], 1)

    def test_outputs_summary_rejects_placeholder_results(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / "tasks" / "demo_task_000001"
            (task_dir / "checkpoints").mkdir(parents=True)
            (task_dir / "logs").mkdir()
            _write_text(task_dir / "predictions.csv", "y_true,y_pred\n10,10\n20,20\n")
            _write_text(task_dir / "checkpoints" / "best.pt", "placeholder checkpoint")
            _write_text(task_dir / "logs" / "queue_stdout.log", "Demo fixture: task marked succeeded for UI walkthrough.\n")
            registry = root / "run_registry.csv"
            _write_text(
                registry,
                "task_id,task_type,task_dir,status,dataset_hash,task,architecture,activation,metric_name,metric_value,checkpoint\n"
                f"demo_task_000001,npz_cnn1d_training,{task_dir},succeeded,demo-good-route,ppm,cnn1d_npz,relu,val_rmse,1.0,{task_dir / 'checkpoints' / 'best.pt'}\n",
            )
            client = TestClient(create_app())

            response = client.post("/api/outputs/summary", json={"registry": str(registry)})

            self.assertEqual(response.status_code, 400)
            self.assertIn("No verifiable real training results", response.json()["detail"])

    def test_outputs_summary_accepts_verifiable_training_result(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / "tasks" / "real_task_000001"
            (task_dir / "checkpoints").mkdir(parents=True)
            _write_text(task_dir / "predictions.csv", "y_true,y_pred\n10,12\n20,19\n30,29\n")
            (task_dir / "checkpoints" / "best.pt").write_bytes(b"PK\x03\x04" + (b"\0" * 2048))
            registry = root / "run_registry.csv"
            _write_text(
                registry,
                "task_id,task_type,task_dir,status,dataset_hash,task,architecture,activation,metric_name,metric_value,checkpoint\n"
                f"real_task_000001,npz_cnn1d_training,{task_dir},succeeded,realhash,ppm,cnn1d_npz,relu,val_rmse,1.5,{task_dir / 'checkpoints' / 'best.pt'}\n",
            )
            client = TestClient(create_app())

            response = client.post("/api/outputs/summary", json={"registry": str(registry)})

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["selected_task_id"], "real_task_000001")
            self.assertEqual(payload["excluded_rows"], [])
            self.assertEqual(payload["prediction_summary"]["kind"], "regression")

    def test_inspect_dataset_endpoint_writes_manifest(self):
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("numpy is not installed")
        import numpy as np
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

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
            client = TestClient(create_app())

            response = client.post(
                "/api/dataset/inspect",
                json={"config": str(config_path), "out": str(root / "inspect")},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["samples"], 3)
            self.assertTrue((root / "inspect" / "dataset_inspection.json").exists())

    def test_import_dataset_files_detects_config(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = {
                "format": "npz_plus_labels",
                "spectra_matrix": "spectra.npz",
                "labels": "labels.csv",
                "identity": {"row_key": "sample_id", "group_key": "sample_link_code"},
            }
            labels = "sample_id,sample_link_code,ppm_mg_kg\nS1,G1,10\n"
            client = TestClient(create_app())

            with _chdir(root):
                response = client.post(
                    "/api/dataset/import-files",
                    json={
                        "files": [
                            _upload_payload("dataset.json", json.dumps(config).encode("utf-8")),
                            _upload_payload("labels.csv", labels.encode("utf-8")),
                        ]
                    },
                )

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["counts"]["dataset_config"], 1)
            self.assertEqual(payload["counts"]["labels"], 1)
            self.assertTrue(Path(payload["dataset_config"]).exists())
            self.assertTrue((Path(payload["import_dir"]) / "import_manifest.json").exists())

    def test_import_dataset_files_auto_config_from_csv_package(self):
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("numpy is not installed")
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        spectra = (
            "sample_id,sample_link_code,500,501,502,503\n"
            "S1,G1,0.1,0.2,0.3,0.4\n"
            "S2,G2,0.2,0.3,0.4,0.5\n"
            "S3,G3,0.3,0.4,0.5,0.6\n"
            "S4,G4,0.4,0.5,0.6,0.7\n"
        )
        labels = (
            "sample_link_code,ppm_mg_kg\n"
            "G1,10\n"
            "G2,600\n"
            "G3,1200\n"
            "G4,80\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            client = TestClient(create_app())

            with _chdir(root):
                response = client.post(
                    "/api/dataset/import-files",
                    json={
                        "files": [
                            _upload_payload("uv3600_spectra.csv", spectra.encode("utf-8")),
                            _upload_payload("titration.csv", labels.encode("utf-8")),
                        ]
                    },
                )

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["counts"]["spectra_csv"], 1)
            self.assertEqual(payload["counts"]["labels"], 1)
            self.assertEqual(payload["generated"]["status"], "ready")
            self.assertEqual(payload["generated"]["warnings"], [])
            self.assertGreaterEqual(len(payload["generated"]["auto_notes"]), 1)
            self.assertTrue(Path(payload["dataset_config"]).exists())

            inspect_response = client.post(
                "/api/dataset/inspect",
                json={"config": payload["dataset_config"], "out": str(root / "inspect")},
            )
            self.assertEqual(inspect_response.status_code, 200)
            self.assertEqual(inspect_response.json()["samples"], 4)
            self.assertEqual(inspect_response.json()["wavelengths"], 4)
            self.assertIn("tri_class", inspect_response.json()["target_columns"])

    def test_create_npz_matrix_endpoint(self):
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("numpy is not installed")
        import numpy as np
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

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
            _write_json(
                matrix_config,
                {
                    "name": "api_matrix",
                    "dataset_config": str(dataset_config),
                    "fixed": {"task": "binary", "window_id": "W1", "epochs": 1},
                    "grid": {"cv_fold": [1], "activation_id": ["relu", "gelu"]},
                },
            )
            client = TestClient(create_app())

            preview = client.post("/api/matrix/preview", json={"config": str(matrix_config)})
            response = client.post(
                "/api/matrix/create-npz",
                json={"config": str(matrix_config), "out": str(root / "matrix_out"), "max_tasks": 2},
            )

            self.assertEqual(preview.status_code, 200)
            self.assertEqual(preview.json()["total_combinations"], 2)
            self.assertEqual(preview.json()["formula"], "cv_fold(1) × activation_id(2)")
            self.assertEqual(preview.json()["grid"][1]["values"], ["relu", "gelu"])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["task_count"], 2)
            self.assertTrue((root / "matrix_out" / "matrix_manifest.json").exists())
            self.assertTrue((root / "matrix_out" / "tasks" / "api_matrix_task_000001" / "run.sh").exists())

    def test_full_factorial_design_endpoint_writes_generated_config(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            dataset_config = _write_config(root, data_dir)
            matrix_config = root / "base_matrix.json"
            _write_json(
                matrix_config,
                {
                    "name": "base_matrix",
                    "dataset_config": str(dataset_config),
                    "fixed": {"task": "binary", "window_id": "W1", "epochs": 1, "dropout": 0.3},
                    "grid": {"cv_fold": [1], "activation_id": ["relu"]},
                },
            )
            client = TestClient(create_app())

            response = client.post(
                "/api/matrix/full-factorial",
                json={
                    "config": str(matrix_config),
                    "name": "factorial_demo",
                    "out": str(root / "generated_design"),
                    "factors": [
                        {"key": "cv_fold", "values": [1, 2]},
                        {"key": "activation_id", "values": ["relu", "gelu"]},
                        {"key": "dropout", "values": [0.1, 0.2]},
                    ],
                },
            )

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            generated_config = Path(payload["config"])
            self.assertTrue(generated_config.exists())
            generated = json.loads(generated_config.read_text(encoding="utf-8"))
            self.assertEqual(generated["grid"]["cv_fold"], [1, 2])
            self.assertEqual(generated["grid"]["activation_id"], ["relu", "gelu"])
            self.assertEqual(generated["grid"]["dropout"], [0.1, 0.2])
            self.assertNotIn("dropout", generated["fixed"])
            self.assertEqual(payload["preview"]["total_combinations"], 8)
            self.assertEqual(payload["preview"]["formula"], "cv_fold(2) × activation_id(2) × dropout(2)")

    def test_queue_dry_run_endpoint(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / "tasks" / "task_000001"
            task_dir.mkdir(parents=True)
            _write_json(task_dir / "status.json", {"status": "pending"})
            client = TestClient(create_app())

            response = client.post(
                "/api/queue/run",
                json={"tasks": str(root / "tasks"), "max_tasks": 1, "dry_run": True, "rerun_failed": False},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["selected"], 1)
            self.assertEqual(response.json()["executed"], 0)
            self.assertEqual(response.json()["task_ids"], ["task_000001"])

    def test_queue_background_job_dry_run_endpoint(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / "tasks" / "task_000001"
            task_dir.mkdir(parents=True)
            _write_json(task_dir / "status.json", {"status": "pending"})
            client = TestClient(create_app())

            start_response = client.post(
                "/api/queue/start",
                json={"tasks": str(root / "tasks"), "max_tasks": 1, "dry_run": True, "rerun_failed": False},
            )
            self.assertEqual(start_response.status_code, 200)
            job_id = start_response.json()["job_id"]

            job = {}
            for _ in range(20):
                status_response = client.get(f"/api/queue/jobs/{job_id}")
                self.assertEqual(status_response.status_code, 200)
                job = status_response.json()
                if job["status"] in {"succeeded", "failed"}:
                    break
                time.sleep(0.05)

            self.assertEqual(job["status"], "succeeded")
            self.assertEqual(job["result"]["selected"], 1)
            self.assertEqual(job["result"]["executed"], 0)
            self.assertEqual(job["result"]["task_ids"], ["task_000001"])

    def test_task_list_and_log_endpoints(self):
        from fastapi.testclient import TestClient
        from spectral_core.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pending = root / "tasks" / "task_pending"
            succeeded = root / "tasks" / "task_succeeded"
            pending.mkdir(parents=True)
            succeeded.mkdir(parents=True)
            _write_json(
                pending / "manifest.json",
                {
                    "task_id": "task_pending",
                    "task": "binary",
                    "cv_fold": 1,
                    "window_id": "W1",
                    "model_id": "cnn3",
                    "activation_id": "relu",
                },
            )
            _write_json(pending / "status.json", {"status": "pending"})
            _write_json(
                succeeded / "manifest.json",
                {
                    "task_id": "task_succeeded",
                    "task": "tri_class",
                    "cv_fold": 2,
                    "window_id": "WBIPLS_SHORT",
                    "model_id": "cnn3",
                    "activation_id": "gelu",
                },
            )
            _write_json(succeeded / "status.json", {"status": "running"})
            _write_json(
                succeeded / "summary.json",
                {
                    "task_id": "task_succeeded",
                    "status": "succeeded",
                    "metric_name": "val_balanced_accuracy",
                    "metric_value": 0.75,
                    "activation": "gelu",
                },
            )
            (succeeded / "logs").mkdir()
            _write_text(succeeded / "logs" / "queue_stdout.log", "training finished\n")
            client = TestClient(create_app())

            list_response = client.post("/api/tasks/list", json={"tasks": str(root / "tasks")})
            log_response = client.post(
                "/api/tasks/log",
                json={"task_dir": str(succeeded), "log": "queue_stdout", "max_chars": 100},
            )

            self.assertEqual(list_response.status_code, 200)
            self.assertEqual(list_response.json()["total"], 2)
            self.assertEqual(list_response.json()["counts"], {"pending": 1, "succeeded": 1})
            self.assertEqual(list_response.json()["rows"][1]["metric_name"], "val_balanced_accuracy")
            self.assertEqual(log_response.status_code, 200)
            self.assertTrue(log_response.json()["exists"])
            self.assertIn("training finished", log_response.json()["content"])


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
            "binary": {"column": "high_risk_gt500_label"},
            "tri_class": {"column": "three_class_label"},
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


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _upload_payload(name: str, data: bytes) -> dict:
    return {
        "name": name,
        "content_base64": base64.b64encode(data).decode("ascii"),
        "size": len(data),
        "mime_type": "application/octet-stream",
    }


class _chdir:
    def __init__(self, path: Path):
        self.path = path
        self.previous = Path.cwd()

    def __enter__(self):
        import os

        os.chdir(self.path)

    def __exit__(self, exc_type, exc, tb):
        import os

        os.chdir(self.previous)


if __name__ == "__main__":
    unittest.main()
