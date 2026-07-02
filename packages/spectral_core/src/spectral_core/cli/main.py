from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from spectral_core.adapters import create_npz_cnn1d_task, inspect_npz_plus_labels_config
from spectral_core.binding import bind_spectrum_supervision
from spectral_core.data import load_csv_matrix
from spectral_core.matrix import create_cnn1d_matrix, create_npz_cnn1d_matrix
from spectral_core.models import NearestCentroidClassifier
from spectral_core.preprocess import apply_preprocess
from spectral_core.queue import run_queue
from spectral_core.registry import RunManifest, write_manifest, write_registry_row
from spectral_core.reports import aggregate_matrix_results, generate_final_report
from spectral_core.scan import scan_runs
from spectral_core.selection import select_candidates
from spectral_core.schema import ExperimentSpec
from spectral_core.splits import make_holdout_split
from spectral_core.tasks import create_cnn1d_task, create_dummy_task


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spectral")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Run a configured experiment")
    train_parser.add_argument("--config", required=True, help="Path to experiment JSON")

    bind_parser = subparsers.add_parser("bind-data", help="Join spectra and supervision tables")
    bind_parser.add_argument("--spectra", required=True, help="Path to spectrum matrix CSV")
    bind_parser.add_argument("--supervision", required=True, help="Path to supervision CSV")
    bind_parser.add_argument("--link-key", default="linkcode", help="Shared sample key")
    bind_parser.add_argument("--target", required=True, help="Supervision target column")
    bind_parser.add_argument("--out", required=True, help="Frozen dataset output directory")

    inspect_parser = subparsers.add_parser("inspect-dataset-config", help="Inspect a dataset adapter config")
    inspect_parser.add_argument("--config", required=True, help="Path to dataset config JSON")
    inspect_parser.add_argument("--out", default=None, help="Optional output directory for inspection reports")

    npz_task_parser = subparsers.add_parser("create-npz-cnn1d-task", help="Create a portable CNN1D task from an npz_plus_labels config")
    npz_task_parser.add_argument("--config", required=True, help="Path to dataset config JSON")
    npz_task_parser.add_argument("--task-id", default="npz_cnn1d_task_000001", help="Task id")
    npz_task_parser.add_argument("--out", required=True, help="Tasks output directory")
    npz_task_parser.add_argument("--task", required=True, help="Target key or alias from the dataset config")
    npz_task_parser.add_argument("--cv-fold", type=int, required=True)
    npz_task_parser.add_argument("--window-id", required=True)
    npz_task_parser.add_argument("--preprocess-id", default="raw_standard")
    npz_task_parser.add_argument("--model-id", default="cnn3")
    npz_task_parser.add_argument("--pooling-id", default="POOL0")
    npz_task_parser.add_argument("--activation-id", default="relu")
    npz_task_parser.add_argument("--channels", default=None, help="Optional comma-separated CNN channels")
    npz_task_parser.add_argument("--kernel-size", type=int, default=5)
    npz_task_parser.add_argument("--dropout", type=float, default=0.2)
    npz_task_parser.add_argument("--learning-rate", type=float, default=0.001)
    npz_task_parser.add_argument("--weight-decay", type=float, default=0.0)
    npz_task_parser.add_argument("--batch-size", type=int, default=32)
    npz_task_parser.add_argument("--epochs", type=int, default=20)
    npz_task_parser.add_argument("--seed", type=int, default=42)
    npz_task_parser.add_argument("--target-transform", default="linear")
    npz_task_parser.add_argument("--loss-id", default="default")

    task_parser = subparsers.add_parser("create-dummy-task", help="Create a portable smoke task folder")
    task_parser.add_argument("--dataset", required=True, help="Frozen dataset directory")
    task_parser.add_argument("--task-id", default="task_000001", help="Task id")
    task_parser.add_argument("--out", required=True, help="Tasks output directory")
    task_parser.add_argument("--metric-value", type=float, default=0.75, help="Dummy validation metric")

    cnn_task_parser = subparsers.add_parser("create-cnn1d-task", help="Create a portable CNN1D training task")
    cnn_task_parser.add_argument("--dataset", required=True, help="Frozen dataset directory")
    cnn_task_parser.add_argument("--task-id", default="task_000001", help="Task id")
    cnn_task_parser.add_argument("--out", required=True, help="Tasks output directory")
    cnn_task_parser.add_argument("--target", required=True, help="Target column in joined dataset")
    cnn_task_parser.add_argument("--task-kind", choices=["classification", "regression"], required=True)
    cnn_task_parser.add_argument("--feature-prefix", default="w", help="Prefix used to select spectral feature columns")
    cnn_task_parser.add_argument("--activation", default="relu", help="Activation: relu/leaky_relu/gelu/silu/elu")
    cnn_task_parser.add_argument("--normalization", default="batch_norm", help="Normalization: batch_norm/layer_norm/none")
    cnn_task_parser.add_argument("--channels", default="16,32,64", help="Comma-separated CNN channels")
    cnn_task_parser.add_argument("--kernel-size", type=int, default=5)
    cnn_task_parser.add_argument("--dropout", type=float, default=0.2)
    cnn_task_parser.add_argument("--learning-rate", type=float, default=0.001)
    cnn_task_parser.add_argument("--batch-size", type=int, default=16)
    cnn_task_parser.add_argument("--epochs", type=int, default=20)
    cnn_task_parser.add_argument("--seed", type=int, default=42)

    matrix_parser = subparsers.add_parser("create-matrix", help="Expand a CNN1D matrix into portable tasks")
    matrix_parser.add_argument("--config", required=True, help="Path to matrix JSON config")
    matrix_parser.add_argument("--out", required=True, help="Matrix output directory")
    matrix_parser.add_argument("--max-tasks", type=int, default=None, help="Safety cap for generated task count")

    npz_matrix_parser = subparsers.add_parser("create-npz-matrix", help="Expand an npz_plus_labels CNN1D matrix into portable tasks")
    npz_matrix_parser.add_argument("--config", required=True, help="Path to NPZ matrix JSON config")
    npz_matrix_parser.add_argument("--out", required=True, help="Matrix output directory")
    npz_matrix_parser.add_argument("--max-tasks", type=int, default=None, help="Safety cap for generated task count")

    scan_parser = subparsers.add_parser("scan-runs", help="Scan task folders into a registry")
    scan_parser.add_argument("--runs", required=True, help="Directory containing task folders")
    scan_parser.add_argument("--out", required=True, help="Registry output directory")

    queue_parser = subparsers.add_parser("run-queue", help="Run pending task folders locally")
    queue_parser.add_argument("--tasks", required=True, help="Directory containing task folders")
    queue_parser.add_argument("--max-tasks", type=int, default=None, help="Maximum tasks to run")
    queue_parser.add_argument("--rerun-failed", action="store_true", help="Run failed tasks again")
    queue_parser.add_argument("--dry-run", action="store_true", help="Only print selected tasks")

    candidates_parser = subparsers.add_parser("select-candidates", help="Select top model candidates from a registry")
    candidates_parser.add_argument("--registry", required=True, help="Path to run_registry.csv")
    candidates_parser.add_argument("--out", required=True, help="Output directory")
    candidates_parser.add_argument("--metric", default=None, help="Metric name to rank by")
    candidates_parser.add_argument("--top", type=int, default=10, help="Number of candidates to output")
    candidates_parser.add_argument("--direction", choices=["auto", "min", "max"], default="auto")

    aggregate_parser = subparsers.add_parser("aggregate-matrix", help="Aggregate matrix registry metrics by experiment fields")
    aggregate_parser.add_argument("--registry", required=True, help="Path to run_registry.csv")
    aggregate_parser.add_argument("--out", required=True, help="Output directory")
    aggregate_parser.add_argument("--metric", default=None, help="Metric name to aggregate")
    aggregate_parser.add_argument("--group-by", default="window_id,activation", help="Comma-separated registry fields")
    aggregate_parser.add_argument("--direction", choices=["auto", "min", "max"], default="auto")

    report_parser = subparsers.add_parser("final-report", help="Generate a Markdown summary report")
    report_parser.add_argument("--dataset-manifest", required=True, help="Path to dataset_manifest.json")
    report_parser.add_argument("--registry", required=True, help="Path to run_registry.csv")
    report_parser.add_argument("--candidates", required=True, help="Path to model_candidates.csv")
    report_parser.add_argument("--out", required=True, help="Markdown report output path")
    report_parser.add_argument("--matrix-manifest", default=None, help="Optional matrix_manifest.json")
    report_parser.add_argument("--title", default="Spectral Deep Matrix Report", help="Report title")

    args = parser.parse_args(argv)
    if args.command == "train":
        return _train(Path(args.config))
    if args.command == "bind-data":
        return _bind_data(args)
    if args.command == "inspect-dataset-config":
        return _inspect_dataset_config(args)
    if args.command == "create-npz-cnn1d-task":
        return _create_npz_cnn1d_task(args)
    if args.command == "create-dummy-task":
        return _create_dummy_task(args)
    if args.command == "create-cnn1d-task":
        return _create_cnn1d_task(args)
    if args.command == "create-matrix":
        return _create_matrix(args)
    if args.command == "create-npz-matrix":
        return _create_npz_matrix(args)
    if args.command == "scan-runs":
        return _scan_runs(args)
    if args.command == "run-queue":
        return _run_queue(args)
    if args.command == "select-candidates":
        return _select_candidates(args)
    if args.command == "aggregate-matrix":
        return _aggregate_matrix(args)
    if args.command == "final-report":
        return _final_report(args)
    raise ValueError(args.command)


def _train(config_path: Path) -> int:
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    spec = ExperimentSpec.from_dict(config, config_path)
    dataset = load_csv_matrix(spec.dataset)
    split = make_holdout_split(dataset, spec.split)
    x = apply_preprocess(dataset.x, spec.preprocess)

    train_x = [x[index] for index in split.train_indices]
    train_y = [dataset.y[index] for index in split.train_indices]
    test_x = [x[index] for index in split.test_indices]
    test_y = [dataset.y[index] for index in split.test_indices]

    if spec.model.name != "nearest_centroid":
        raise ValueError(f"MVP only supports nearest_centroid, got: {spec.model.name}")

    model = NearestCentroidClassifier().fit(train_x, train_y)
    predictions = model.predict(test_x)
    metrics = {"accuracy": _accuracy(test_y, predictions)}

    run_id = time.strftime("%Y%m%d_%H%M%S")
    run_dir = spec.output_dir / spec.name / run_id
    _write_predictions(run_dir, dataset, split.test_indices, test_y, predictions)

    manifest = RunManifest(
        run_id=run_id,
        experiment_name=spec.name,
        dataset_path=str(dataset.source_path),
        dataset_hash=dataset.content_hash,
        n_samples=dataset.n_samples,
        n_features=dataset.n_features,
        task_kind=spec.task.kind,
        target_column=spec.task.target_column,
        split_id=split.split_id,
        train_size=len(split.train_indices),
        test_size=len(split.test_indices),
        preprocess_steps=spec.preprocess.steps,
        model_name=spec.model.name,
        metrics=metrics,
    )
    manifest_path = write_manifest(manifest, run_dir)
    registry_path = write_registry_row(manifest, spec.output_dir)
    print(f"run_id={run_id}")
    print(f"manifest={manifest_path}")
    print(f"registry={registry_path}")
    print(f"accuracy={metrics['accuracy']:.4f}")
    return 0


def _bind_data(args: argparse.Namespace) -> int:
    result = bind_spectrum_supervision(
        spectra_path=Path(args.spectra).resolve(),
        supervision_path=Path(args.supervision).resolve(),
        link_key=args.link_key,
        target_column=args.target,
        output_dir=Path(args.out).resolve(),
    )
    print(f"dataset_hash={result.dataset_hash}")
    print(f"joined_rows={result.joined_rows}")
    print(f"joined={result.joined_path}")
    print(f"manifest={result.manifest_path}")
    print(f"report={result.report_path}")
    return 0


def _inspect_dataset_config(args: argparse.Namespace) -> int:
    result = inspect_npz_plus_labels_config(
        config_path=Path(args.config),
        output_dir=Path(args.out).resolve() if args.out else None,
    )
    print(f"status={result.status}")
    print(f"samples={result.sample_count}")
    print(f"wavelengths={result.wavelength_count}")
    print(f"split_counts={json.dumps(result.split_counts, ensure_ascii=False, sort_keys=True)}")
    print(f"cv_fold_counts={json.dumps(result.cv_fold_counts, ensure_ascii=False, sort_keys=True)}")
    print(f"window_count={result.window_count}")
    if result.manifest_path:
        print(f"manifest={result.manifest_path}")
    if result.report_path:
        print(f"report={result.report_path}")
    return 0


def _create_npz_cnn1d_task(args: argparse.Namespace) -> int:
    channels = _parse_channels(args.channels) if args.channels else None
    result = create_npz_cnn1d_task(
        config_path=Path(args.config),
        task_id=args.task_id,
        output_dir=Path(args.out).resolve(),
        task=args.task,
        cv_fold=args.cv_fold,
        window_id=args.window_id,
        preprocess_id=args.preprocess_id,
        model_id=args.model_id,
        pooling_id=args.pooling_id,
        activation_id=args.activation_id,
        dropout=args.dropout,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        batch_size=args.batch_size,
        epochs=args.epochs,
        seed=args.seed,
        channels=channels,
        kernel_size=args.kernel_size,
        target_transform=args.target_transform,
        loss_id=args.loss_id,
    )
    print(f"task_id={result.task_id}")
    print(f"task_dir={result.task_dir}")
    print(f"data={result.data_path}")
    print(f"config={result.config_path}")
    print(f"manifest={result.manifest_path}")
    print(f"run_script={result.run_script}")
    print(f"train_size={result.train_size}")
    print(f"val_size={result.val_size}")
    print(f"feature_count={result.feature_count}")
    return 0


def _create_dummy_task(args: argparse.Namespace) -> int:
    result = create_dummy_task(
        dataset_dir=Path(args.dataset).resolve(),
        task_id=args.task_id,
        output_dir=Path(args.out).resolve(),
        metric_value=args.metric_value,
    )
    print(f"task_id={result.task_id}")
    print(f"task_dir={result.task_dir}")
    print(f"run_script={result.run_script}")
    return 0


def _create_cnn1d_task(args: argparse.Namespace) -> int:
    result = create_cnn1d_task(
        dataset_dir=Path(args.dataset).resolve(),
        task_id=args.task_id,
        output_dir=Path(args.out).resolve(),
        target_column=args.target,
        task_kind=args.task_kind,
        feature_prefix=args.feature_prefix,
        activation=args.activation,
        normalization=args.normalization,
        channels=_parse_channels(args.channels),
        kernel_size=args.kernel_size,
        dropout=args.dropout,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        epochs=args.epochs,
        seed=args.seed,
    )
    print(f"task_id={result.task_id}")
    print(f"task_dir={result.task_dir}")
    print(f"config={result.config_path}")
    print(f"run_script={result.run_script}")
    return 0


def _scan_runs(args: argparse.Namespace) -> int:
    result = scan_runs(
        runs_dir=Path(args.runs).resolve(),
        output_dir=Path(args.out).resolve(),
    )
    print(f"scanned={result.scanned}")
    print(f"succeeded={result.succeeded}")
    print(f"failed={result.failed}")
    print(f"registry={result.registry_path}")
    return 0


def _create_matrix(args: argparse.Namespace) -> int:
    result = create_cnn1d_matrix(
        config_path=Path(args.config),
        output_dir=Path(args.out),
        max_tasks=args.max_tasks,
    )
    print(f"matrix_dir={result.matrix_dir}")
    print(f"tasks_dir={result.tasks_dir}")
    print(f"task_count={result.task_count}")
    print(f"task_index={result.task_index_path}")
    print(f"manifest={result.manifest_path}")
    return 0


def _create_npz_matrix(args: argparse.Namespace) -> int:
    result = create_npz_cnn1d_matrix(
        config_path=Path(args.config),
        output_dir=Path(args.out),
        max_tasks=args.max_tasks,
    )
    print(f"matrix_dir={result.matrix_dir}")
    print(f"tasks_dir={result.tasks_dir}")
    print(f"task_count={result.task_count}")
    print(f"task_index={result.task_index_path}")
    print(f"manifest={result.manifest_path}")
    return 0


def _run_queue(args: argparse.Namespace) -> int:
    result = run_queue(
        tasks_dir=Path(args.tasks).resolve(),
        max_tasks=args.max_tasks,
        rerun_failed=args.rerun_failed,
        dry_run=args.dry_run,
    )
    print(f"selected={result.selected}")
    print(f"executed={result.executed}")
    print(f"skipped={result.skipped}")
    print(f"succeeded={result.succeeded}")
    print(f"failed={result.failed}")
    if result.task_ids:
        print("tasks=" + ",".join(result.task_ids))
    return 0 if result.failed == 0 else 1


def _select_candidates(args: argparse.Namespace) -> int:
    result = select_candidates(
        registry_path=Path(args.registry).resolve(),
        output_dir=Path(args.out).resolve(),
        metric_name=args.metric,
        top=args.top,
        direction=args.direction,
    )
    print(f"input_rows={result.input_rows}")
    print(f"eligible_rows={result.eligible_rows}")
    print(f"selected_rows={result.selected_rows}")
    print(f"metric={result.metric_name}")
    print(f"direction={result.direction}")
    print(f"candidates={result.candidates_path}")
    print(f"report={result.report_path}")
    return 0


def _aggregate_matrix(args: argparse.Namespace) -> int:
    result = aggregate_matrix_results(
        registry_path=Path(args.registry).resolve(),
        output_dir=Path(args.out).resolve(),
        metric_name=args.metric,
        group_by=_parse_csv_list(args.group_by),
        direction=args.direction,
    )
    print(f"input_rows={result.input_rows}")
    print(f"eligible_rows={result.eligible_rows}")
    print(f"group_count={result.group_count}")
    print(f"metric={result.metric_name}")
    print(f"direction={result.direction}")
    print(f"group_by={','.join(result.group_by)}")
    print(f"group_summary={result.summary_path}")
    print(f"run_details={result.details_path}")
    print(f"report={result.report_path}")
    return 0


def _final_report(args: argparse.Namespace) -> int:
    result = generate_final_report(
        dataset_manifest_path=Path(args.dataset_manifest).resolve(),
        registry_path=Path(args.registry).resolve(),
        candidates_path=Path(args.candidates).resolve(),
        output_path=Path(args.out).resolve(),
        matrix_manifest_path=Path(args.matrix_manifest).resolve() if args.matrix_manifest else None,
        title=args.title,
    )
    print(f"registry_rows={result.registry_rows}")
    print(f"candidate_rows={result.candidate_rows}")
    print(f"report={result.report_path}")
    return 0


def _parse_channels(raw: str) -> list[int]:
    channels = [int(value.strip()) for value in raw.split(",") if value.strip()]
    if not channels:
        raise ValueError("channels must contain at least one integer")
    return channels


def _parse_csv_list(raw: str) -> list[str]:
    values = [value.strip() for value in raw.split(",") if value.strip()]
    if not values:
        raise ValueError("Expected at least one comma-separated value")
    return values


def _accuracy(y_true: list[str], y_pred: list[str]) -> float:
    if len(y_true) != len(y_pred):
        raise ValueError("Prediction length mismatch")
    correct = sum(1 for left, right in zip(y_true, y_pred) if left == right)
    return correct / len(y_true)


def _write_predictions(
    run_dir: Path,
    dataset,
    test_indices: list[int],
    y_true: list[str],
    y_pred: list[str],
) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "predictions.csv"
    lines = ["sample_id,y_true,y_pred"]
    for index, truth, prediction in zip(test_indices, y_true, y_pred):
        lines.append(f"{dataset.sample_ids[index]},{truth},{prediction}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    raise SystemExit(main())
