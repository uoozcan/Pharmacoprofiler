import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "evaluate" / "build_leakage_safe_model_comparison.py"
SCRIPT_DIR = SCRIPT_PATH.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location("model_comparison_builder", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC) if SPEC is not None else None

if SPEC is not None and SPEC.loader is not None and MODULE is not None:
    sys.modules[SPEC.name] = MODULE
    SPEC.loader.exec_module(MODULE)
    collect_model_rows = MODULE.collect_model_rows
    read_summary_if_present = MODULE.read_summary_if_present
    validate_status = MODULE.validate_status
    write_outputs = MODULE.write_outputs
    EXPECTED_MODEL_LAYOUT = MODULE.EXPECTED_MODEL_LAYOUT
    DEFAULT_LEAKAGE_SAFE_DIR = MODULE.DEFAULT_LEAKAGE_SAFE_DIR
else:  # pragma: no cover
    collect_model_rows = None
    read_summary_if_present = None
    validate_status = None
    write_outputs = None
    EXPECTED_MODEL_LAYOUT = None
    DEFAULT_LEAKAGE_SAFE_DIR = None


@unittest.skipIf(
    collect_model_rows is None
    or read_summary_if_present is None
    or validate_status is None
    or write_outputs is None
    or EXPECTED_MODEL_LAYOUT is None
    or DEFAULT_LEAKAGE_SAFE_DIR is None,
    "Model comparison builder module could not be loaded",
)
class ModelComparisonBuilderTest(unittest.TestCase):
    def test_read_summary_if_present_filters_requested_model(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            summary_path = Path(temp_dir) / "regime_summary.tsv"
            pd.DataFrame(
                [
                    {
                        "regime_name": "pair_random",
                        "model_name": "ridge",
                        "folds": 5,
                        "mean_mae": 0.4,
                        "mean_rmse": 0.5,
                        "mean_pearson_r": 0.8,
                        "mean_spearman_r": 0.7,
                        "mean_r_squared": 0.6,
                        "total_test_rows": 10,
                    },
                    {
                        "regime_name": "pair_random",
                        "model_name": "ols",
                        "folds": 5,
                        "mean_mae": 0.5,
                        "mean_rmse": 0.6,
                        "mean_pearson_r": 0.7,
                        "mean_spearman_r": 0.6,
                        "mean_r_squared": 0.5,
                        "total_test_rows": 10,
                    },
                ]
            ).to_csv(summary_path, sep="\t", index=False)
            row = read_summary_if_present(summary_path, "pair_random", "ols")
            self.assertIsNotNone(row)
            self.assertEqual(row.iloc[0]["model_name"], "ols")
            self.assertAlmostEqual(float(row.iloc[0]["mean_mae"]), 0.5)

    def test_collect_model_rows_marks_missing_regimes_pending(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            original_layout = EXPECTED_MODEL_LAYOUT["ridge"].copy()
            EXPECTED_MODEL_LAYOUT["ridge"] = {
                "pair_random": base / "pair.tsv",
                "cell_line_holdout": base / "missing.tsv",
                "compound_holdout": base / "missing2.tsv",
                "double_cold_start": base / "missing3.tsv",
            }
            try:
                pd.DataFrame(
                    [
                        {
                            "regime_name": "pair_random",
                            "model_name": "ridge",
                            "folds": 5,
                            "mean_mae": 0.4,
                            "mean_rmse": 0.5,
                            "mean_pearson_r": 0.8,
                            "mean_spearman_r": 0.7,
                            "mean_r_squared": 0.6,
                            "total_test_rows": 10,
                        }
                    ]
                ).to_csv(base / "pair.tsv", sep="\t", index=False)
                comparison, status = collect_model_rows(["ridge"])
                self.assertEqual(len(comparison), 1)
                self.assertFalse(status["ridge"]["complete"])
                self.assertTrue(status["ridge"]["regimes"]["pair_random"]["present"])
                self.assertFalse(status["ridge"]["regimes"]["cell_line_holdout"]["present"])
            finally:
                EXPECTED_MODEL_LAYOUT["ridge"] = original_layout

    def test_validate_status_raises_for_missing_regimes(self):
        with self.assertRaises(FileNotFoundError):
            validate_status(
                {
                    "ridge": {
                        "complete": False,
                        "regimes": {
                            "pair_random": {"present": True},
                            "cell_line_holdout": {"present": False},
                        },
                    }
                }
            )

    def test_write_outputs_emits_tsv_and_status_json(self):
        comparison = pd.DataFrame(
            [
                {
                    "regime_name": "pair_random",
                    "model_name": "ridge",
                    "folds": 5,
                    "mean_mae": 0.4,
                    "mean_rmse": 0.5,
                    "mean_pearson_r": 0.8,
                    "mean_spearman_r": 0.7,
                    "mean_r_squared": 0.6,
                    "total_test_rows": 10,
                }
            ]
        )
        status = {
            "ridge": {
                "complete": True,
                "regimes": {"pair_random": {"expected_path": "/tmp/pair.tsv", "present": True}},
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            output_tsv = Path(temp_dir) / "comparison.tsv"
            status_json = Path(temp_dir) / "status.json"
            write_outputs(comparison, status, output_tsv, status_json)
            self.assertTrue(output_tsv.exists())
            loaded = json.loads(status_json.read_text(encoding="utf-8"))
            self.assertEqual(loaded["completed_models"], ["ridge"])
            self.assertEqual(loaded["pending_models"], [])


if __name__ == "__main__":
    unittest.main()
