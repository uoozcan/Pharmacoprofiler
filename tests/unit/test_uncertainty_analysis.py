import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd


ANALYSIS_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "evaluate" / "analyze_legacy_benchmark_uncertainty.py"
)
ANALYSIS_DIR = ANALYSIS_PATH.parent
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
SPEC = importlib.util.spec_from_file_location("legacy_uncertainty_analysis", ANALYSIS_PATH)
MODULE = importlib.util.module_from_spec(SPEC) if SPEC is not None else None

if SPEC is not None and SPEC.loader is not None and MODULE is not None:
    sys.modules[SPEC.name] = MODULE
    SPEC.loader.exec_module(MODULE)
    build_calibration_reference_split = MODULE.build_calibration_reference_split
    build_summary = MODULE.build_summary
    build_calibration_summary = MODULE.build_calibration_summary
    build_calibrated_prediction_table = MODULE.build_calibrated_prediction_table
    conformal_quantile = MODULE.conformal_quantile
    correlation_or_none = MODULE.correlation_or_none
    posthoc_interval_inflation = MODULE.posthoc_interval_inflation
    summarize_conformal_interval_calibration = MODULE.summarize_conformal_interval_calibration
    summarize_interval_calibration = MODULE.summarize_interval_calibration
else:  # pragma: no cover - defensive import path
    build_calibration_reference_split = None
    build_summary = None
    build_calibration_summary = None
    build_calibrated_prediction_table = None
    conformal_quantile = None
    correlation_or_none = None
    posthoc_interval_inflation = None
    summarize_conformal_interval_calibration = None
    summarize_interval_calibration = None


@unittest.skipIf(
    build_calibration_reference_split is None
    or
    build_summary is None
    or build_calibration_summary is None
    or build_calibrated_prediction_table is None
    or conformal_quantile is None
    or correlation_or_none is None
    or posthoc_interval_inflation is None
    or summarize_conformal_interval_calibration is None
    or summarize_interval_calibration is None,
    "Uncertainty analysis module could not be loaded",
)
class UncertaintyAnalysisTest(unittest.TestCase):
    def test_correlation_or_none_returns_none_for_constant_series(self):
        self.assertIsNone(correlation_or_none(pd.Series([1.0, 1.0, 1.0]), pd.Series([0.1, 0.2, 0.3])))

    def test_build_summary_uses_extreme_bins_and_global_counts(self):
        uncertainty_df = pd.DataFrame(
            {
                "CELL_LINE_NAME": ["a", "a", "b", "b"],
                "DRUG_NAME": ["d1", "d2", "d1", "d2"],
                "prediction_std": [0.2, 0.4, 0.6, 0.8],
                "absolute_error": [0.3, 0.5, 0.7, 0.9],
                "within_tree_interval_90": [1.0, 1.0, 0.0, 1.0],
                "nearest_train_cosine": [0.95, 0.95, 0.90, 0.90],
            }
        )
        uncertainty_bins = pd.DataFrame(
            [
                {
                    "uncertainty_bin": "Q1 lowest",
                    "n": 2,
                    "mean_prediction_std": 0.3,
                    "mae": 0.4,
                    "rmse": 0.45,
                    "interval_coverage_90": 1.0,
                    "mean_signed_error": -0.1,
                },
                {
                    "uncertainty_bin": "Q5 highest",
                    "n": 2,
                    "mean_prediction_std": 0.7,
                    "mae": 0.8,
                    "rmse": 0.85,
                    "interval_coverage_90": 0.5,
                    "mean_signed_error": -0.6,
                },
            ]
        )
        applicability_bins = pd.DataFrame(
            [
                {
                    "applicability_bin": "Q1 lowest",
                    "n": 2,
                    "mean_nearest_train_cosine": 0.90,
                    "mae": 0.8,
                    "mean_prediction_std": 0.7,
                    "mean_signed_error": -0.6,
                },
                {
                    "applicability_bin": "Q5 highest",
                    "n": 2,
                    "mean_nearest_train_cosine": 0.95,
                    "mae": 0.4,
                    "mean_prediction_std": 0.3,
                    "mean_signed_error": -0.1,
                },
            ]
        )
        cell_line_summary = pd.DataFrame(
            {
                "CELL_LINE_NAME": ["a", "b"],
                "n": [2, 2],
                "nearest_train_cosine": [0.95, 0.90],
                "mae": [0.4, 0.8],
            }
        )
        interval_calibration = pd.DataFrame(
            [
                {
                    "nominal_coverage": 0.80,
                    "empirical_coverage": 0.75,
                    "coverage_gap": -0.05,
                    "mean_interval_width": 0.8,
                },
                {
                    "nominal_coverage": 0.90,
                    "empirical_coverage": 0.70,
                    "coverage_gap": -0.20,
                    "mean_interval_width": 1.2,
                },
            ]
        )
        posthoc_calibration = {
            "target_coverage": 0.90,
            "inflation_factor": 1.35,
            "posthoc_empirical_coverage": 0.90,
        }

        summary = build_summary(
            uncertainty_df=uncertainty_df,
            uncertainty_bins=uncertainty_bins,
            applicability_bins=applicability_bins,
            cell_line_summary=cell_line_summary,
            interval_calibration=interval_calibration,
            conformal_interval_calibration=pd.DataFrame(
                [
                    {
                        "nominal_coverage": 0.90,
                        "raw_empirical_coverage": 0.70,
                        "conformal_empirical_coverage": 0.88,
                        "raw_coverage_gap": -0.20,
                        "conformal_coverage_gap": -0.02,
                        "raw_mean_interval_width": 1.2,
                        "conformal_mean_interval_width": 1.8,
                        "conformal_quantile": 0.95,
                    }
                ]
            ),
            posthoc_calibration=posthoc_calibration,
            calibration_metadata={"source": "gdsc_post_training_reference_split", "selected_rows": 4},
            response_metadata={"reconstructed": True},
            artifact_paths={"trained_model": Path("/tmp/model.joblib")},
        )

        self.assertEqual(summary["global"]["rows"], 4)
        self.assertEqual(summary["global"]["cell_lines"], 2)
        self.assertEqual(summary["global"]["drugs"], 2)
        self.assertEqual(summary["highest_uncertainty_bin"]["uncertainty_bin"], "Q5 highest")
        self.assertEqual(summary["lowest_applicability_bin"]["applicability_bin"], "Q1 lowest")
        self.assertIn("uncertainty_vs_absolute_error_pearson", summary["global"])
        self.assertAlmostEqual(summary["global"]["tree_interval_90_coverage_gap"], -0.20)
        self.assertAlmostEqual(summary["global"]["conformal_interval_90_coverage"], 0.88)
        self.assertAlmostEqual(summary["posthoc_interval_calibration_90"]["inflation_factor"], 1.35)

    def test_summarize_interval_calibration_reports_expected_levels(self):
        estimator_predictions = pd.DataFrame(
            {
                0: [0.9, 1.0, 1.1, 1.2],
                1: [1.9, 2.0, 2.1, 2.2],
            }
        ).to_numpy()
        labels = pd.Series([1.05, 2.05]).to_numpy()

        calibration = summarize_interval_calibration(estimator_predictions, labels)

        self.assertEqual(calibration["nominal_coverage"].tolist(), [0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
        self.assertTrue((calibration["mean_interval_width"] > 0).all())

    def test_posthoc_interval_inflation_returns_positive_factor(self):
        labels = pd.Series([1.0, 2.0, 3.0]).to_numpy()
        lower = pd.Series([0.8, 1.7, 2.5]).to_numpy()
        upper = pd.Series([1.1, 2.1, 3.1]).to_numpy()

        calibration = posthoc_interval_inflation(labels, lower, upper, target_coverage=0.90)

        self.assertGreater(calibration["inflation_factor"], 0.0)
        self.assertGreaterEqual(calibration["posthoc_empirical_coverage"], 0.0)
        self.assertLessEqual(calibration["posthoc_empirical_coverage"], 1.0)

    def test_conformal_quantile_uses_higher_quantile(self):
        scores = pd.Series([0.1, 0.2, 0.3, 0.4]).to_numpy()
        self.assertAlmostEqual(conformal_quantile(scores, 0.90), 0.4)

    def test_build_calibration_reference_split_is_deterministic(self):
        gdsc_response_df = pd.DataFrame(
            {
                "CELL_LINE_NAME_edited": ["cl1", "cl1", "cl2", "cl2"],
                "DRUG_NAME_edited": ["d1", "d2", "d1", "d2"],
                "FINGERPRINT": ["0" * 1024, "1" * 1024, "0" * 1024, "1" * 1024],
                "pIC50": [1.0, 2.0, 3.0, 4.0],
            }
        )
        gdsc_omics_df = pd.DataFrame(
            {
                "CELL_LINE_NAME": ["cl1", "cl2"],
                "f1": [0.1, 0.2],
                "f2": [0.3, 0.4],
            }
        )
        _, calibration_df_a, metadata_a = build_calibration_reference_split(
            gdsc_response_df, gdsc_omics_df, target_column="pIC50", sample_size=2, seed=11
        )
        _, calibration_df_b, metadata_b = build_calibration_reference_split(
            gdsc_response_df, gdsc_omics_df, target_column="pIC50", sample_size=2, seed=11
        )

        pd.testing.assert_frame_equal(calibration_df_a, calibration_df_b)
        self.assertEqual(metadata_a, metadata_b)

    def test_summarize_conformal_interval_calibration_improves_coverage_fields(self):
        true_values = pd.Series([1.0, 2.0, 3.0]).to_numpy()
        point_predictions = pd.Series([1.1, 2.1, 2.9]).to_numpy()
        estimator_predictions = pd.DataFrame(
            {
                0: [1.0, 1.1, 1.2, 1.3],
                1: [2.0, 2.1, 2.2, 2.3],
                2: [2.8, 2.9, 3.0, 3.1],
            }
        ).to_numpy()
        conformal_scores = pd.Series([0.2, 0.3, 0.4, 0.5]).to_numpy()
        interval_scale = pd.Series([0.5, 0.7, 0.9]).to_numpy()

        calibration = summarize_conformal_interval_calibration(
            true_values, point_predictions, estimator_predictions, conformal_scores, interval_scale
        )

        self.assertIn("raw_empirical_coverage", calibration.columns)
        self.assertIn("conformal_empirical_coverage", calibration.columns)
        self.assertIn("conformal_quantile", calibration.columns)

    def test_build_calibrated_prediction_table_adds_api_ready_columns(self):
        uncertainty_df = pd.DataFrame(
            {
                "CELL_LINE_NAME": ["a"],
                "DRUG_NAME": ["d"],
                "pIC50_True": [5.0],
                "pIC50_Pred": [4.8],
                "prediction_std": [0.3],
                "prediction_interval_low_90": [4.4],
                "prediction_interval_high_90": [5.1],
                "signed_error": [-0.2],
                "absolute_error": [0.2],
                "squared_error": [0.04],
                "within_tree_interval_90": [1.0],
                "nearest_train_cosine": [0.95],
            }
        )

        calibrated = build_calibrated_prediction_table(uncertainty_df, conformal_quantile_90=0.5)

        self.assertIn("conformal_prediction_interval_low_90", calibrated.columns)
        self.assertIn("prediction_interval_level", calibrated.columns)
        self.assertIn("uncertainty_method", calibrated.columns)
        self.assertIn("applicability_score", calibrated.columns)
        self.assertIn("conformal_interval_scale", calibrated.columns)
        self.assertEqual(calibrated.loc[0, "uncertainty_method"], "split_conformal_tree_std_scaled")

    def test_build_calibration_summary_selects_90_percent_row(self):
        conformal_interval_calibration = pd.DataFrame(
            [
                {
                    "nominal_coverage": 0.90,
                    "raw_empirical_coverage": 0.70,
                    "conformal_empirical_coverage": 0.89,
                    "raw_coverage_gap": -0.20,
                    "conformal_coverage_gap": -0.01,
                    "raw_mean_interval_width": 1.2,
                    "conformal_mean_interval_width": 1.8,
                    "conformal_quantile": 0.95,
                }
            ]
        )
        conformal_subgroups = pd.DataFrame(
            [
                {
                    "subgroup_type": "tissue",
                    "subgroup_label": "Lung",
                    "n": 30,
                    "raw_interval_coverage_90": 0.7,
                    "conformal_interval_coverage_90": 0.88,
                    "raw_mean_interval_width_90": 1.1,
                    "conformal_mean_interval_width_90": 1.7,
                    "mae": 0.4,
                    "mean_signed_error": -0.2,
                },
                {
                    "subgroup_type": "potency_bin",
                    "subgroup_label": ">7.5",
                    "n": 10,
                    "raw_interval_coverage_90": 0.6,
                    "conformal_interval_coverage_90": 0.82,
                    "raw_mean_interval_width_90": 1.1,
                    "conformal_mean_interval_width_90": 1.7,
                    "mae": 0.8,
                    "mean_signed_error": -0.7,
                },
            ]
        )

        summary = build_calibration_summary(
            conformal_interval_calibration,
            conformal_subgroups,
            {"selected_rows": 1000},
        )

        self.assertEqual(summary["target_nominal_coverage"], 0.9)
        self.assertEqual(summary["largest_tissue_coverage_gap_90"]["subgroup_type"], "tissue")
        self.assertEqual(summary["highest_potency_bin_coverage_90"]["subgroup_label"], ">7.5")


if __name__ == "__main__":
    unittest.main()
