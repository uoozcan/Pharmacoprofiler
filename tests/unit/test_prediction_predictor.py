import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd


PREDICTOR_PATH = Path(__file__).resolve().parents[2] / "services" / "prediction-api" / "predictor.py"
PREDICTOR_DIR = PREDICTOR_PATH.parent
if str(PREDICTOR_DIR) not in sys.path:
    sys.path.insert(0, str(PREDICTOR_DIR))
SPEC = importlib.util.spec_from_file_location("prediction_api_predictor", PREDICTOR_PATH)
MODULE = importlib.util.module_from_spec(SPEC) if SPEC is not None else None

if SPEC is not None and SPEC.loader is not None and MODULE is not None:
    sys.modules[SPEC.name] = MODULE
    SPEC.loader.exec_module(MODULE)
    PIC50Predictor = MODULE.PIC50Predictor
else:  # pragma: no cover - defensive import path
    PIC50Predictor = None


@unittest.skipIf(PIC50Predictor is None, "Predictor module could not be loaded")
class PredictorSanitizationTest(unittest.TestCase):
    def test_build_cell_line_metadata_replaces_nan_with_empty_string(self):
        predictor = PIC50Predictor()
        cell_line_df = pd.DataFrame(
            {
                "edited": ["cell_a", "cell_b"],
                "main": ["A549", "MCF7"],
                "TISSUE": [pd.NA, "Breast"],
                "RRID": ["CVCL_0023", pd.NA],
            }
        )
        predictor._build_cell_line_metadata(cell_line_df)

        self.assertEqual(predictor.cl_tissue_dict["cell_a"], "")
        self.assertEqual(predictor.cl_rrid_dict["cell_b"], "")
        self.assertEqual(predictor.cl_main_dict["cell_a"], "A549")


if __name__ == "__main__":
    unittest.main()
