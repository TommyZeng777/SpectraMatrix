from __future__ import annotations

import random
from dataclasses import dataclass
from math import ceil

from spectral_core.data import SpectralDataset
from spectral_core.schema import SplitSpec


@dataclass(frozen=True)
class SplitResult:
    train_indices: list[int]
    test_indices: list[int]
    split_id: str


def make_holdout_split(dataset: SpectralDataset, spec: SplitSpec) -> SplitResult:
    if spec.method not in {"holdout", "cv_smoke"}:
        raise ValueError(f"MVP supports holdout/cv_smoke only, got: {spec.method}")
    if not 0 < spec.test_size < 1:
        raise ValueError("test_size must be between 0 and 1")

    rng = random.Random(spec.seed)
    indices = list(range(dataset.n_samples))

    if spec.stratify:
        grouped: dict[str, list[int]] = {}
        for index, label in enumerate(dataset.y):
            grouped.setdefault(label, []).append(index)
        test_indices: list[int] = []
        train_indices: list[int] = []
        for label_indices in grouped.values():
            shuffled = list(label_indices)
            rng.shuffle(shuffled)
            n_test = max(1, ceil(len(shuffled) * spec.test_size))
            test_indices.extend(shuffled[:n_test])
            train_indices.extend(shuffled[n_test:])
    else:
        shuffled = list(indices)
        rng.shuffle(shuffled)
        n_test = max(1, ceil(len(shuffled) * spec.test_size))
        test_indices = shuffled[:n_test]
        train_indices = shuffled[n_test:]

    if not train_indices or not test_indices:
        raise ValueError("Split produced an empty train or test partition")

    split_id = f"{spec.method}-seed{spec.seed}-test{spec.test_size:g}-stratified{int(spec.stratify)}"
    return SplitResult(
        train_indices=sorted(train_indices),
        test_indices=sorted(test_indices),
        split_id=split_id,
    )

