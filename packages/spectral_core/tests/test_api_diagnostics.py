import json
import importlib.util
import tempfile
import unittest
from pathlib import Path

HAS_FASTAPI = importlib.util.find_spec("fastapi") is not None


@unittest.skipUnless(HAS_FASTAPI, "fastapi is not installed")
class DiagnosticsSaveTests(unittest.TestCase):
    def test_save_diagnostics_session_writes_json_and_markdown(self):
        from spectral_core.api.app import SaveDiagnosticsRequest, _save_diagnostics_session

        with tempfile.TemporaryDirectory() as tmp:
            request = SaveDiagnosticsRequest(
                out=tmp,
                session_id="test-session",
                started_at="2026-07-01T10:00:00",
                stopped_at="2026-07-01T10:01:00",
                url="http://127.0.0.1:8765/#matrix",
                user_agent="test",
                events=[
                    {
                        "at": "2026-07-01T10:00:10",
                        "name": "api.error",
                        "detail": {"path": "/api/matrix/create-npz", "http_status": 400, "detail": "bad config"},
                    }
                ],
            )

            result = _save_diagnostics_session(request)

            json_path = Path(result["json"])
            markdown_path = Path(result["markdown"])
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["event_count"], 1)
            self.assertIn("api.error", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
