import importlib.util
import sys
import unittest
from pathlib import Path

try:
    from flask import Flask
except ModuleNotFoundError:
    Flask = object


APP_PATH = Path(__file__).resolve().parents[2] / "services" / "prediction-api" / "app.py"
APP_DIR = APP_PATH.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
SPEC = importlib.util.spec_from_file_location("prediction_api_app", APP_PATH)
MODULE = importlib.util.module_from_spec(SPEC) if SPEC is not None else None

if SPEC is not None and SPEC.loader is not None and MODULE is not None:
    try:
        SPEC.loader.exec_module(MODULE)
        create_app = MODULE.create_app
    except ModuleNotFoundError:
        create_app = None
else:
    create_app = None


class FakePredictor:
    def __init__(self, loaded: bool):
        self.is_loaded = loaded
        self.main_cl_list = ["a549", "mcf7"]
        self.asset_dir = Path("/tmp/fake-assets")
        self.load_error = None if loaded else "assets missing"

    def dependency_status(self):
        return {"joblib": True, "rdkit": True}

    def info(self):
        if not self.is_loaded:
            return {
                "model_loaded": False,
                "asset_status": {"model_file": {"exists": False}},
                "load_error": self.load_error,
            }
        return {
            "model_loaded": True,
            "model_info": {
                "dataset": "fake",
                "cell_lines_count": 2,
                "omics_features": 3747,
                "ecfp4_features": 1024,
                "total_features": 4771,
                "available_tissues": 2,
                "model_version": "fake.joblib",
                "feature_schema_version": "omics_3747_plus_ecfp4_1024_v1",
            },
            "asset_status": {"model_file": {"exists": True}},
            "dependency_status": self.dependency_status(),
        }

    def predict_batch(self, smiles_list):
        if not self.is_loaded:
            return {"error": "Model not loaded", "asset_status": {"model_file": {"exists": False}}}
        invalid = [item for item in smiles_list if not isinstance(item, str) or not item.strip()]
        if invalid:
            return {
                "total_smiles_submitted": len(smiles_list),
                "valid_smiles_count": 0,
                "invalid_smiles_count": len(invalid),
                "predictions": {},
                "total_predictions": 0,
                "invalid_smiles": [{"smiles": item, "error": "Invalid or empty SMILES string"} for item in invalid],
            }
        return {
            "total_smiles_submitted": len(smiles_list),
            "valid_smiles_count": len(smiles_list),
            "invalid_smiles_count": 0,
            "predictions": {
                smiles_list[0]: [
                    {
                        "CELL_LINE_NAME": "A549",
                        "RRID": "CVCL_0023",
                        "TISSUE": "lung",
                        "pIC50_Prediction": 6.1,
                    }
                ]
            },
            "total_predictions": 1,
            "model_version": "fake.joblib",
            "feature_schema_version": "omics_3747_plus_ecfp4_1024_v1",
        }


@unittest.skipIf(create_app is None, "Flask runtime is not available in the current environment")
class PredictionAPIContractTest(unittest.TestCase):
    def test_degraded_service_returns_503(self):
        app: Flask = create_app(FakePredictor(loaded=False))
        client = app.test_client()
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 503)
        payload = response.get_json()
        self.assertEqual(payload["status"], "degraded")

    def test_predict_accepts_legacy_smiles_key(self):
        app: Flask = create_app(FakePredictor(loaded=True))
        client = app.test_client()
        response = client.post("/api/predict", json={"smiles": "CCO"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("predictions", payload)
        self.assertEqual(payload["valid_smiles_count"], 1)
        self.assertIn("api_version", payload)

    def test_predict_rejects_missing_smiles(self):
        app: Flask = create_app(FakePredictor(loaded=True))
        client = app.test_client()
        response = client.post("/api/predict", json={"foo": "bar"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
