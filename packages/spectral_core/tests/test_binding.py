import json
import tempfile
import unittest
from pathlib import Path

from spectral_core.binding import bind_spectrum_supervision


class BindingTests(unittest.TestCase):
    def test_binds_spectra_and_supervision_by_linkcode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spectra = root / "spectra.csv"
            supervision = root / "supervision.csv"
            out = root / "frozen"
            spectra.write_text(
                "linkcode,w1,w2\n"
                "S1,0.1,0.2\n"
                "S2,0.3,0.4\n",
                encoding="utf-8",
            )
            supervision.write_text(
                "linkcode,target,batch\n"
                "S1,10,A\n"
                "S2,20,B\n",
                encoding="utf-8",
            )

            result = bind_spectrum_supervision(spectra, supervision, "linkcode", "target", out)

            self.assertEqual(result.joined_rows, 2)
            self.assertTrue(result.joined_path.exists())
            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["target_column"], "target")
            self.assertEqual(manifest["spectra_only_count"], 0)

    def test_rejects_duplicate_linkcode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spectra = root / "spectra.csv"
            supervision = root / "supervision.csv"
            spectra.write_text(
                "linkcode,w1\n"
                "S1,0.1\n"
                "S1,0.2\n",
                encoding="utf-8",
            )
            supervision.write_text("linkcode,target\nS1,10\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Duplicate"):
                bind_spectrum_supervision(spectra, supervision, "linkcode", "target", root / "out")


if __name__ == "__main__":
    unittest.main()

