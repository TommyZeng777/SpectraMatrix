"""Generate a tiny synthetic CSV dataset for first-run smoke tests.

The generated files are fake and contain no laboratory measurements.
They are written into an ignored runtime folder by default.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def generate(out_dir: Path, sample_count: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    spectra_path = out_dir / "sample_spectra.csv"
    supervision_path = out_dir / "sample_supervision.csv"
    wavelengths = [str(value) for value in range(500, 511)]

    with spectra_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_id", "sample_link_code", *wavelengths])
        for idx in range(sample_count):
            link_code = f"DEMO{idx + 1:03d}"
            baseline = 0.12 + idx * 0.011
            values = [
                round(baseline + math.sin((idx + 1) * (j + 1) / 8) * 0.018, 6)
                for j, _ in enumerate(wavelengths)
            ]
            writer.writerow([f"scan_{idx + 1:03d}", link_code, *values])

    with supervision_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_link_code", "ppm_mg_kg"])
        for idx in range(sample_count):
            writer.writerow([f"DEMO{idx + 1:03d}", 120 + idx * 37])

    print(f"Wrote {spectra_path}")
    print(f"Wrote {supervision_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="datasets/sample_csv", help="Output folder for generated CSV files.")
    parser.add_argument("--samples", type=int, default=12, help="Number of synthetic samples to create.")
    args = parser.parse_args()
    if args.samples < 2:
        raise SystemExit("--samples must be at least 2")
    generate(Path(args.out), args.samples)


if __name__ == "__main__":
    main()
