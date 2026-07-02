from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Cnn1DTaskResult:
    task_dir: Path
    task_id: str
    run_script: Path
    train_script: Path
    config_path: Path
    manifest_path: Path


def create_cnn1d_task(
    dataset_dir: Path,
    task_id: str,
    output_dir: Path,
    target_column: str,
    task_kind: str,
    feature_prefix: str = "w",
    activation: str = "relu",
    normalization: str = "batch_norm",
    channels: list[int] | None = None,
    kernel_size: int = 5,
    dropout: float = 0.2,
    learning_rate: float = 0.001,
    batch_size: int = 16,
    epochs: int = 20,
    seed: int = 42,
) -> Cnn1DTaskResult:
    dataset_manifest_path = dataset_dir / "dataset_manifest.json"
    joined_path = dataset_dir / "joined_dataset.csv"
    if not dataset_manifest_path.exists():
        raise FileNotFoundError(f"Missing dataset manifest: {dataset_manifest_path}")
    if not joined_path.exists():
        raise FileNotFoundError(f"Missing joined dataset: {joined_path}")
    if task_kind not in {"classification", "regression"}:
        raise ValueError(f"Unsupported task_kind: {task_kind}")

    dataset_manifest = json.loads(dataset_manifest_path.read_text(encoding="utf-8"))
    task_dir = output_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    channels = channels or [16, 32, 64]

    config = {
        "task_id": task_id,
        "task_type": "cnn1d_training",
        "dataset_dir": str(dataset_dir.resolve()),
        "joined_dataset": str(joined_path.resolve()),
        "dataset_hash": dataset_manifest["dataset_hash"],
        "target_column": target_column,
        "task_kind": task_kind,
        "feature_prefix": feature_prefix,
        "model": {
            "architecture": "cnn1d_basic",
            "activation": activation,
            "normalization": normalization,
            "channels": channels,
            "kernel_size": kernel_size,
            "dropout": dropout,
        },
        "trainer": {
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "epochs": epochs,
            "seed": seed,
            "validation_fraction": 0.25,
        },
    }
    config_path = task_dir / "config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "task_id": task_id,
        "task_type": "cnn1d_training",
        "dataset_hash": dataset_manifest["dataset_hash"],
        "dataset_dir": str(dataset_dir.resolve()),
        "target_column": target_column,
        "task_kind": task_kind,
        "architecture": "cnn1d_basic",
        "activation": activation,
        "normalization": normalization,
        "channels": channels,
        "kernel_size": kernel_size,
        "dropout": dropout,
        "status": "pending",
    }
    manifest_path = task_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (task_dir / "status.json").write_text(json.dumps({"status": "pending"}, indent=2) + "\n", encoding="utf-8")
    train_script = task_dir / "train.py"
    train_script.write_text(_cnn1d_train_source(), encoding="utf-8")
    run_script = task_dir / "run.sh"
    run_script.write_text("#!/usr/bin/env bash\nset -euo pipefail\n\"${PYTHON:-python3}\" train.py\n", encoding="utf-8")
    os.chmod(run_script, 0o755)
    (task_dir / "requirements.txt").write_text(
        "torch\nnumpy\n",
        encoding="utf-8",
    )
    return Cnn1DTaskResult(
        task_dir=task_dir,
        task_id=task_id,
        run_script=run_script,
        train_script=train_script,
        config_path=config_path,
        manifest_path=manifest_path,
    )


def _cnn1d_train_source() -> str:
    return r'''from __future__ import annotations

import csv
import json
import math
import random
import time
import traceback
from pathlib import Path


def main() -> int:
    task_dir = Path(__file__).resolve().parent
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except Exception as exc:
        _fail(task_dir, exc)
        return 1

    try:
        config = _read_json(task_dir / "config.json")
        _write_json(task_dir / "status.json", {"status": "running", "started_at": time.time()})
        _set_seed(torch, int(config["trainer"]["seed"]))
        rows = _read_rows(Path(config["joined_dataset"]))
        feature_columns = _feature_columns(rows[0], config["feature_prefix"])
        x_values = [[float(row[column]) for column in feature_columns] for row in rows]
        y_values = [row[config["target_column"]] for row in rows]
        train_indices, val_indices = _split_indices(len(rows), float(config["trainer"]["validation_fraction"]), int(config["trainer"]["seed"]))
        x_train = torch.tensor([x_values[index] for index in train_indices], dtype=torch.float32).unsqueeze(1)
        x_val = torch.tensor([x_values[index] for index in val_indices], dtype=torch.float32).unsqueeze(1)

        if config["task_kind"] == "classification":
            labels = sorted(set(y_values))
            label_to_index = {label: index for index, label in enumerate(labels)}
            y_train = torch.tensor([label_to_index[y_values[index]] for index in train_indices], dtype=torch.long)
            y_val = torch.tensor([label_to_index[y_values[index]] for index in val_indices], dtype=torch.long)
            output_dim = len(labels)
            criterion = nn.CrossEntropyLoss()
            metric_name = "val_accuracy"
        else:
            labels = []
            label_to_index = {}
            y_train = torch.tensor([[float(y_values[index])] for index in train_indices], dtype=torch.float32)
            y_val = torch.tensor([[float(y_values[index])] for index in val_indices], dtype=torch.float32)
            output_dim = 1
            criterion = nn.MSELoss()
            metric_name = "val_rmse"

        CNN1D = _make_cnn1d_class(torch, nn)
        model = CNN1D(
            input_length=len(feature_columns),
            output_dim=output_dim,
            channels=list(config["model"]["channels"]),
            kernel_size=int(config["model"]["kernel_size"]),
            dropout=float(config["model"]["dropout"]),
            activation_name=str(config["model"]["activation"]),
            normalization=str(config["model"]["normalization"]),
        )
        optimizer = torch.optim.Adam(model.parameters(), lr=float(config["trainer"]["learning_rate"]))
        loader = DataLoader(
            TensorDataset(x_train, y_train),
            batch_size=int(config["trainer"]["batch_size"]),
            shuffle=True,
        )
        best_metric = None
        best_state = None
        logs = []
        for epoch in range(1, int(config["trainer"]["epochs"]) + 1):
            model.train()
            total_loss = 0.0
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                output = model(batch_x)
                loss = criterion(output, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += float(loss.item()) * len(batch_x)
            val_metric = _evaluate(torch, model, x_val, y_val, config["task_kind"])
            logs.append({"epoch": epoch, "train_loss": total_loss / len(x_train), metric_name: val_metric})
            if best_metric is None or _is_better(metric_name, val_metric, best_metric):
                best_metric = val_metric
                best_state = {key: value.detach().cpu() for key, value in model.state_dict().items()}

        (task_dir / "logs").mkdir(exist_ok=True)
        (task_dir / "checkpoints").mkdir(exist_ok=True)
        with (task_dir / "metrics.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["epoch", "train_loss", metric_name])
            writer.writeheader()
            writer.writerows(logs)
        checkpoint_path = task_dir / "checkpoints" / "best.pt"
        torch.save(
            {
                "state_dict": best_state,
                "config": config,
                "feature_columns": feature_columns,
                "labels": labels,
                "label_to_index": label_to_index,
                "best_metric": best_metric,
            },
            checkpoint_path,
        )
        predictions_path = _write_predictions(torch, task_dir, model, x_val, y_val, config["task_kind"], labels, [rows[index]["linkcode"] for index in val_indices])
        summary = {
            "task_id": config["task_id"],
            "status": "succeeded",
            "dataset_hash": config["dataset_hash"],
            "metric_name": metric_name,
            "metric_value": best_metric,
            "checkpoint": str(checkpoint_path),
            "predictions": str(predictions_path),
            "n_samples": len(rows),
            "n_features": len(feature_columns),
            "architecture": config["model"]["architecture"],
            "activation": config["model"]["activation"],
            "normalization": config["model"]["normalization"],
        }
        _write_json(task_dir / "summary.json", summary)
        _write_json(task_dir / "status.json", {"status": "succeeded", "finished_at": time.time()})
        return 0
    except Exception as exc:
        _fail(task_dir, exc)
        return 1


def _make_cnn1d_class(torch, nn):
    class ChannelLayerNorm(nn.Module):
        def __init__(self, channels):
            super().__init__()
            self.norm = nn.LayerNorm(channels)

        def forward(self, x):
            return self.norm(x.transpose(1, 2)).transpose(1, 2)

    def activation(name):
        if name == "relu":
            return nn.ReLU()
        if name == "leaky_relu":
            return nn.LeakyReLU()
        if name == "gelu":
            return nn.GELU()
        if name == "silu":
            return nn.SiLU()
        if name == "elu":
            return nn.ELU()
        raise ValueError(f"Unsupported activation: {name}")

    class CNN1D(nn.Module):
        def __init__(self, input_length, output_dim, channels, kernel_size, dropout, activation_name, normalization):
            super().__init__()
            layers = []
            in_channels = 1
            for out_channels in channels:
                padding = kernel_size // 2
                layers.append(nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, padding=padding))
                if normalization == "batch_norm":
                    layers.append(nn.BatchNorm1d(out_channels))
                elif normalization == "layer_norm":
                    layers.append(ChannelLayerNorm(out_channels))
                layers.append(activation(activation_name))
                layers.append(nn.MaxPool1d(kernel_size=2, stride=2))
                in_channels = out_channels
            self.backbone = nn.Sequential(*layers)
            with torch.no_grad():
                dummy = torch.zeros(1, 1, input_length)
                flattened = self.backbone(dummy).reshape(1, -1).shape[1]
            hidden_dim = max(16, min(128, flattened))
            self.head = nn.Sequential(
                nn.Dropout(dropout),
                nn.Linear(flattened, hidden_dim),
                activation(activation_name),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, output_dim),
            )

        def forward(self, x):
            features = self.backbone(x).reshape(x.shape[0], -1)
            return self.head(features)

    return CNN1D


def _read_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _feature_columns(row, prefix):
    columns = [column for column in row if column.startswith(prefix)]
    if not columns:
        raise ValueError(f"No feature columns with prefix: {prefix}")
    return columns


def _split_indices(n_samples, validation_fraction, seed):
    rng = random.Random(seed)
    indices = list(range(n_samples))
    rng.shuffle(indices)
    n_val = max(1, math.ceil(n_samples * validation_fraction))
    return indices[n_val:], indices[:n_val]


def _evaluate(torch, model, x_val, y_val, task_kind):
    model.eval()
    with torch.no_grad():
        output = model(x_val)
        if task_kind == "classification":
            predicted = output.argmax(dim=1)
            return float((predicted == y_val).float().mean().item())
        rmse = torch.sqrt(torch.mean((output - y_val) ** 2))
        return float(rmse.item())


def _is_better(metric_name, value, best):
    if metric_name == "val_rmse":
        return value < best
    return value > best


def _write_predictions(torch, task_dir, model, x_val, y_val, task_kind, labels, sample_ids):
    path = task_dir / "predictions.csv"
    model.eval()
    with torch.no_grad():
        output = model(x_val)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id", "y_true", "y_pred"])
            writer.writeheader()
            if task_kind == "classification":
                predicted = output.argmax(dim=1).tolist()
                truth = y_val.tolist()
                for sample_id, y_true, y_pred in zip(sample_ids, truth, predicted):
                    writer.writerow({"sample_id": sample_id, "y_true": labels[y_true], "y_pred": labels[y_pred]})
            else:
                for sample_id, y_true, y_pred in zip(sample_ids, y_val.reshape(-1).tolist(), output.reshape(-1).tolist()):
                    writer.writerow({"sample_id": sample_id, "y_true": y_true, "y_pred": y_pred})
    return path


def _set_seed(torch, seed):
    random.seed(seed)
    torch.manual_seed(seed)


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fail(task_dir, exc):
    (task_dir / "logs").mkdir(exist_ok=True)
    error = {"status": "failed", "error": repr(exc)}
    _write_json(task_dir / "status.json", error)
    (task_dir / "logs" / "error.log").write_text(traceback.format_exc(), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
'''
