from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt


class NearestCentroidClassifier:
    """Tiny dependency-free baseline for validating the experiment pipeline."""

    def __init__(self) -> None:
        self.centroids: dict[str, list[float]] = {}
        self.majority_label: str | None = None

    def fit(self, x: list[list[float]], y: list[str]) -> "NearestCentroidClassifier":
        if not x:
            raise ValueError("Cannot fit on an empty dataset")
        grouped: dict[str, list[list[float]]] = defaultdict(list)
        for row, label in zip(x, y):
            grouped[label].append(row)
        self.centroids = {
            label: _mean_vector(rows)
            for label, rows in grouped.items()
        }
        self.majority_label = Counter(y).most_common(1)[0][0]
        return self

    def predict(self, x: list[list[float]]) -> list[str]:
        if not self.centroids:
            raise ValueError("Model is not fitted")
        predictions: list[str] = []
        for row in x:
            label = min(
                self.centroids,
                key=lambda candidate: _euclidean(row, self.centroids[candidate]),
            )
            predictions.append(label)
        return predictions


def _mean_vector(rows: list[list[float]]) -> list[float]:
    width = len(rows[0])
    return [sum(row[index] for row in rows) / len(rows) for index in range(width)]


def _euclidean(a: list[float], b: list[float]) -> float:
    return sqrt(sum((left - right) ** 2 for left, right in zip(a, b)))

