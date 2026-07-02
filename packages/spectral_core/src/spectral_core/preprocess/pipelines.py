from __future__ import annotations

from math import sqrt

from spectral_core.schema import PreprocessSpec


def apply_preprocess(x: list[list[float]], spec: PreprocessSpec) -> list[list[float]]:
    current = [list(row) for row in x]
    for step in spec.steps:
        if step == "raw":
            continue
        if step == "snv":
            current = [_snv(row) for row in current]
            continue
        if step == "l2":
            current = [_l2(row) for row in current]
            continue
        raise ValueError(f"Unsupported preprocess step in MVP: {step}")
    return current


def _snv(row: list[float]) -> list[float]:
    mean = sum(row) / len(row)
    variance = sum((value - mean) ** 2 for value in row) / len(row)
    std = sqrt(variance)
    if std == 0:
        return [0.0 for _ in row]
    return [(value - mean) / std for value in row]


def _l2(row: list[float]) -> list[float]:
    norm = sqrt(sum(value * value for value in row))
    if norm == 0:
        return [0.0 for _ in row]
    return [value / norm for value in row]

