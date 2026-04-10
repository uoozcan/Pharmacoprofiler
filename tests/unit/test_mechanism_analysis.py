import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd


ANALYSIS_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "evaluate" / "analyze_legacy_benchmark_mechanisms.py"
)
ANALYSIS_DIR = ANALYSIS_PATH.parent
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
SPEC = importlib.util.spec_from_file_location("legacy_mechanism_analysis", ANALYSIS_PATH)
MODULE = importlib.util.module_from_spec(SPEC) if SPEC is not None else None

if SPEC is not None and SPEC.loader is not None and MODULE is not None:
    sys.modules[SPEC.name] = MODULE
    SPEC.loader.exec_module(MODULE)
    annotate_benchmark_drugs = MODULE.annotate_benchmark_drugs
    parse_targets = MODULE.parse_targets
else:  # pragma: no cover
    annotate_benchmark_drugs = None
    parse_targets = None


@unittest.skipIf(annotate_benchmark_drugs is None or parse_targets is None, "Mechanism analysis module could not be loaded")
class MechanismAnalysisTest(unittest.TestCase):
    def test_parse_targets_extracts_clean_target_names(self):
        parsed = parse_targets("['Dual specificity kinase MEK1 (Pchembl_value=9.2)', 'EGFR (Pchembl_value=7.0)']")
        self.assertEqual(parsed, ["Dual specificity kinase MEK1", "EGFR"])

    def test_parse_targets_falls_back_for_malformed_list_text(self):
        parsed = parse_targets("['Serine/threonine-protein kinase B-raf (Pchembl_value=8.52)', 'VEGFR2 (Pchembl_value=6.3)'")
        self.assertEqual(parsed[:2], ["Serine/threonine-protein kinase B-raf", "VEGFR2"])

    def test_annotate_benchmark_drugs_marks_unmatched_rows(self):
        drug_metrics = pd.DataFrame(
            {
                "DRUG_NAME": ["selumetinib", "unknown_drug"],
                "mae": [0.5, 1.0],
                "mean_signed_error": [-0.1, -0.5],
                "pearson_r": [0.8, 0.2],
            }
        )
        compound_table = pd.DataFrame(
            {
                "COMPOUND_NAME": ["Selumetinib"],
                "PREFERRED_COMPOUND_NAME": ["SELUMETINIB"],
                "COMPOUND_CLASS": ["Kinase inhibitors"],
                "TARGETS": [["MEK1", "MEK2"]],
                "TARGETS_UNIPROT": [""],
                "compound_name_key": ["selumetinib"],
                "preferred_name_key": ["selumetinib"],
                "parsed_targets": [["MEK1", "MEK2"]],
                "target_count": [2],
                "primary_target": ["MEK1"],
                "target_preview": ["MEK1 | MEK2"],
                "compound_class_clean": ["Kinase inhibitors"],
            }
        )
        annotated_df, unmatched = annotate_benchmark_drugs(drug_metrics, compound_table)
        self.assertEqual(len(unmatched), 1)
        self.assertIn("unknown_drug", unmatched)
        matched = annotated_df[annotated_df["DRUG_NAME"] == "selumetinib"].iloc[0]
        self.assertEqual(matched["compound_class"], "Kinase inhibitors")
        self.assertEqual(int(matched["target_count"]), 2)
        self.assertEqual(matched["primary_target"], "MEK1")


if __name__ == "__main__":
    unittest.main()
