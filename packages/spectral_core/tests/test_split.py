import unittest
from pathlib import Path

from spectral_core.data import SpectralDataset
from spectral_core.schema import SplitSpec
from spectral_core.splits import make_holdout_split


class SplitTests(unittest.TestCase):
    def test_stratified_holdout_keeps_both_classes_in_test(self):
        dataset = SpectralDataset(
            sample_ids=[f"S{i}" for i in range(8)],
            feature_names=["w1"],
            x=[[float(i)] for i in range(8)],
            y=["a", "a", "a", "a", "b", "b", "b", "b"],
            rows=[],
            source_path=Path("dummy.csv"),
            content_hash="abc",
        )
        split = make_holdout_split(dataset, SplitSpec(test_size=0.25, stratify=True, seed=1))
        test_labels = {dataset.y[index] for index in split.test_indices}
        self.assertEqual(test_labels, {"a", "b"})


if __name__ == "__main__":
    unittest.main()

