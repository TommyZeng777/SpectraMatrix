import unittest

from spectral_core.preprocess import apply_preprocess
from spectral_core.schema import PreprocessSpec


class PreprocessTests(unittest.TestCase):
    def test_raw_keeps_values(self):
        self.assertEqual(
            apply_preprocess([[1.0, 2.0]], PreprocessSpec(["raw"])),
            [[1.0, 2.0]],
        )

    def test_snv_centers_each_row(self):
        transformed = apply_preprocess([[1.0, 2.0, 3.0]], PreprocessSpec(["snv"]))
        self.assertAlmostEqual(sum(transformed[0]), 0.0, places=7)


if __name__ == "__main__":
    unittest.main()

