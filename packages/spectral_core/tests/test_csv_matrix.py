import tempfile
import unittest
from pathlib import Path

from spectral_core.data import load_csv_matrix
from spectral_core.schema import DatasetSpec


class CsvMatrixTests(unittest.TestCase):
    def test_loads_wide_spectrum_matrix(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spectra.csv"
            path.write_text(
                "sample_id,target,w1,w2\n"
                "S1,a,0.1,0.2\n"
                "S2,b,0.3,0.4\n",
                encoding="utf-8",
            )
            dataset = load_csv_matrix(DatasetSpec(path=path))

        self.assertEqual(dataset.n_samples, 2)
        self.assertEqual(dataset.n_features, 2)
        self.assertEqual(dataset.sample_ids, ["S1", "S2"])
        self.assertEqual(dataset.y, ["a", "b"])

    def test_rejects_duplicate_sample_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spectra.csv"
            path.write_text(
                "sample_id,target,w1\n"
                "S1,a,0.1\n"
                "S1,b,0.3\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unique"):
                load_csv_matrix(DatasetSpec(path=path))


if __name__ == "__main__":
    unittest.main()

