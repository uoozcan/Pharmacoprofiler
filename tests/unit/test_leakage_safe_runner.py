import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "evaluate" / "run_legacy_leakage_safe_benchmarks.py"
SCRIPT_DIR = SCRIPT_PATH.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location("leakage_safe_runner", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC) if SPEC is not None else None

if SPEC is not None and SPEC.loader is not None and MODULE is not None:
    sys.modules[SPEC.name] = MODULE
    SPEC.loader.exec_module(MODULE)
    fit_predict_chunked_ridge = MODULE.fit_predict_chunked_ridge
    fold_masks = MODULE.fold_masks
    materialize_feature_memmap = MODULE.materialize_feature_memmap
    summarize_regime_metrics = MODULE.summarize_regime_metrics
else:  # pragma: no cover
    fit_predict_chunked_ridge = None
    fold_masks = None
    materialize_feature_memmap = None
    summarize_regime_metrics = None


@unittest.skipIf(
    fold_masks is None or summarize_regime_metrics is None or fit_predict_chunked_ridge is None or materialize_feature_memmap is None,
    "Leakage-safe runner module could not be loaded",
)
class LeakageSafeRunnerTest(unittest.TestCase):
    def test_double_cold_start_masks_exclude_seen_entities(self):
        df = pd.DataFrame(
            {
                "compound_holdout_fold": [0, 0, 1, 1],
                "cell_line_holdout_fold": [0, 1, 0, 1],
            }
        )
        train_mask, test_mask = fold_masks(df, "double_cold_start", 0)
        self.assertEqual(test_mask.tolist(), [True, False, False, False])
        self.assertEqual(train_mask.tolist(), [False, False, False, True])

    def test_regime_summary_aggregates_fold_metrics(self):
        fold_metrics = pd.DataFrame(
            {
                "regime_name": ["pair_random", "pair_random", "compound_holdout"],
                "model_name": ["legacy_rf", "legacy_rf", "ridge"],
                "fold": [0, 1, 0],
                "mae": [0.5, 0.7, 1.0],
                "rmse": [0.6, 0.8, 1.1],
                "pearson_r": [0.8, 0.7, 0.2],
                "spearman_r": [0.75, 0.65, 0.1],
                "r_squared": [0.4, 0.3, -0.1],
                "test_rows": [10, 12, 8],
            }
        )
        summary = summarize_regime_metrics(fold_metrics)
        pair_row = summary[(summary["regime_name"] == "pair_random") & (summary["model_name"] == "legacy_rf")].iloc[0]
        self.assertEqual(int(pair_row["folds"]), 2)
        self.assertAlmostEqual(float(pair_row["mean_mae"]), 0.6)
        self.assertEqual(int(pair_row["total_test_rows"]), 22)

    def test_chunked_ridge_recovers_simple_linear_signal(self):
        feature_df = pd.DataFrame(
            {
                "source_row_id": [0, 1, 2, 3],
                "DRUG_NAME_edited": ["drug_a", "drug_a", "drug_b", "drug_b"],
                "CELL_LINE_NAME_edited": ["cell_1", "cell_2", "cell_1", "cell_2"],
                "pIC50": [1.0, 2.0, 1.0, 2.0],
                "pair_random_fold": [0, 0, 1, 1],
                "compound_holdout_fold": [0, 0, 1, 1],
                "cell_line_holdout_fold": [0, 1, 0, 1],
                "double_cold_start_fold": [0, 1, 0, 1],
            }
        )
        omics_lookup = {
            "cell_1": pd.Series([0.0, 1.0], dtype="float32").to_numpy(),
            "cell_2": pd.Series([1.0, 1.0], dtype="float32").to_numpy(),
        }
        fingerprint_lookup = {
            "drug_a": pd.Series([1.0, 0.0], dtype="float32").to_numpy(),
            "drug_b": pd.Series([1.0, 1.0], dtype="float32").to_numpy(),
        }
        predictions = fit_predict_chunked_ridge(
            feature_df,
            train_index=pd.Index([0, 1]).to_numpy(),
            test_index=pd.Index([2, 3]).to_numpy(),
            omics_lookup=omics_lookup,
            fingerprint_lookup=fingerprint_lookup,
            alpha=1e-6,
            chunk_size=1,
        )
        self.assertEqual(len(predictions), 2)
        self.assertAlmostEqual(float(predictions[0]), 1.0, places=4)
        self.assertAlmostEqual(float(predictions[1]), 2.0, places=4)

    def test_feature_memmap_materializes_expected_shape(self):
        rows = pd.DataFrame(
            {
                "DRUG_NAME_edited": ["drug_a", "drug_b"],
                "CELL_LINE_NAME_edited": ["cell_1", "cell_2"],
            }
        )
        omics_lookup = {
            "cell_1": np.array([0.0, 1.0], dtype=np.float32),
            "cell_2": np.array([2.0, 3.0], dtype=np.float32),
        }
        fingerprint_lookup = {
            "drug_a": np.array([1.0, 0.0], dtype=np.float32),
            "drug_b": np.array([0.0, 1.0], dtype=np.float32),
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            matrix = materialize_feature_memmap(
                rows,
                omics_lookup,
                fingerprint_lookup,
                Path(temp_dir) / "features.dat",
                chunk_size=1,
            )
            self.assertEqual(matrix.shape, (2, 4))
            np.testing.assert_allclose(matrix[0], np.array([0.0, 1.0, 1.0, 0.0], dtype=np.float32))
            np.testing.assert_allclose(matrix[1], np.array([2.0, 3.0, 0.0, 1.0], dtype=np.float32))


if __name__ == "__main__":
    unittest.main()
