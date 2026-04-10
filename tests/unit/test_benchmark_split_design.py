import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "evaluate" / "design_legacy_benchmark_splits.py"
SCRIPT_DIR = SCRIPT_PATH.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location("benchmark_split_design", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC) if SPEC is not None else None

if SPEC is not None and SPEC.loader is not None and MODULE is not None:
    sys.modules[SPEC.name] = MODULE
    SPEC.loader.exec_module(MODULE)
    assign_pair_random_folds = MODULE.assign_pair_random_folds
    shuffled_round_robin = MODULE.shuffled_round_robin
    build_double_cold_start_summary = MODULE.build_double_cold_start_summary
else:  # pragma: no cover
    assign_pair_random_folds = None
    shuffled_round_robin = None
    build_double_cold_start_summary = None


@unittest.skipIf(
    assign_pair_random_folds is None or shuffled_round_robin is None or build_double_cold_start_summary is None,
    "Benchmark split design module could not be loaded",
)
class BenchmarkSplitDesignTest(unittest.TestCase):
    def test_shuffled_round_robin_assigns_every_entity_once(self):
        mapping = shuffled_round_robin(["a", "b", "c", "d", "e"], folds=3, seed=17)
        self.assertEqual(set(mapping.keys()), {"a", "b", "c", "d", "e"})
        self.assertTrue(all(value in {0, 1, 2} for value in mapping.values()))

    def test_pair_random_fold_assignment_has_expected_length(self):
        df = pd.DataFrame({"row": range(10)})
        assignments = assign_pair_random_folds(df, folds=5, seed=11)
        self.assertEqual(len(assignments), 10)
        self.assertEqual(set(assignments.tolist()), {0, 1, 2, 3, 4})

    def test_double_cold_start_summary_counts_only_matching_entity_folds(self):
        df = pd.DataFrame(
            {
                "DRUG_NAME_edited": ["d1", "d1", "d2", "d2"],
                "CELL_LINE_NAME_edited": ["c1", "c2", "c1", "c2"],
                "compound_holdout_fold": [0, 0, 1, 1],
                "cell_line_holdout_fold": [0, 1, 0, 1],
            }
        )
        summary = build_double_cold_start_summary(df, "compound_holdout_fold", "cell_line_holdout_fold", 2)
        self.assertEqual(summary[0]["test_rows"], 1)
        self.assertEqual(summary[1]["test_rows"], 1)
        self.assertEqual(summary[0]["test_drugs"], 1)
        self.assertEqual(summary[1]["test_cell_lines"], 1)


if __name__ == "__main__":
    unittest.main()
