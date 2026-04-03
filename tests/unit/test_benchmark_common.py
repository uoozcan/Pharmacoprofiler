import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.evaluate._common import (
    normalize_token,
    resolve_manifest_artifacts,
    resolve_output_dir,
)


class BenchmarkCommonTest(unittest.TestCase):
    def test_normalize_token_strips_case_and_punctuation(self):
        self.assertEqual(normalize_token("AZD-6244"), "azd6244")
        self.assertEqual(normalize_token(" Soft Tissue "), "softtissue")

    def test_resolve_output_dir_falls_back_when_preferred_path_fails(self):
        with tempfile.NamedTemporaryFile() as handle:
            preferred = Path(handle.name) / "cannot-create-child"
            resolved = resolve_output_dir(preferred)
        self.assertEqual(resolved, Path("/tmp/pharmacoprofiler_outputs/legacy_pic50_baseline").resolve())
        self.assertTrue(resolved.exists())

    def test_resolve_manifest_artifacts_returns_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source_root = tmp_path / "source"
            source_root.mkdir()
            manifest_path = tmp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "source_root": str(source_root),
                        "artifacts": [
                            {
                                "name": "trained_model",
                                "relative_dir": "models",
                                "filename": "model.joblib",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            resolved = resolve_manifest_artifacts(manifest_path)
        self.assertEqual(resolved["trained_model"], (source_root / "models" / "model.joblib").resolve())


if __name__ == "__main__":
    unittest.main()
