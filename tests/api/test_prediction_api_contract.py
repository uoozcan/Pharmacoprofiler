import importlib.util
import os
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

    def asset_status(self):
        return {"model_file": {"exists": self.is_loaded}}

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
            "fingerprint_info": {"type": "ECFP4", "radius": 2, "bits": 1024, "library": "RDKit"},
            "performance_limits": {"max_smiles_per_request": "10"},
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
    def setUp(self):
        self._old_max_smiles = os.environ.get("MAX_SMILES_PER_REQUEST")

    def tearDown(self):
        if self._old_max_smiles is None:
            os.environ.pop("MAX_SMILES_PER_REQUEST", None)
        else:
            os.environ["MAX_SMILES_PER_REQUEST"] = self._old_max_smiles

    def test_degraded_service_returns_503(self):
        app: Flask = create_app(FakePredictor(loaded=False))
        client = app.test_client()
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 503)
        payload = response.get_json()
        self.assertEqual(payload["status"], "degraded")

    def test_degraded_info_returns_503_with_expected_fields(self):
        app: Flask = create_app(FakePredictor(loaded=False))
        client = app.test_client()
        response = client.get("/api/info")
        self.assertEqual(response.status_code, 503)
        payload = response.get_json()
        self.assertFalse(payload["model_loaded"])
        self.assertIn("asset_status", payload)
        self.assertIn("dependency_status", payload)
        self.assertIn("api_version", payload)

    def test_predict_accepts_legacy_smiles_key(self):
        app: Flask = create_app(FakePredictor(loaded=True))
        client = app.test_client()
        response = client.post("/api/predict", json={"smiles": "CCO"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("predictions", payload)
        self.assertEqual(payload["valid_smiles_count"], 1)
        self.assertIn("api_version", payload)
        self.assertIn("request_timestamp", payload)

    def test_predict_rejects_missing_smiles(self):
        app: Flask = create_app(FakePredictor(loaded=True))
        client = app.test_client()
        response = client.post("/api/predict", json={"foo": "bar"})
        self.assertEqual(response.status_code, 400)

    def test_predict_accepts_smiles_list_alias(self):
        app: Flask = create_app(FakePredictor(loaded=True))
        client = app.test_client()
        response = client.post("/api/predict", json={"smiles_list": ["CCO"]})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["valid_smiles_count"], 1)
        self.assertIn("CCO", payload["predictions"])

    def test_predict_single_success_path(self):
        app: Flask = create_app(FakePredictor(loaded=True))
        client = app.test_client()
        response = client.post("/api/predict/single", json={"smiles": "CCO"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["valid_smiles_count"], 1)
        self.assertIn("request_timestamp", payload)

    def test_predict_enforces_max_smiles_limit(self):
        os.environ["MAX_SMILES_PER_REQUEST"] = "1"
        app: Flask = create_app(FakePredictor(loaded=True))
        client = app.test_client()
        response = client.post("/api/predict", json={"smiles_list": ["CCO", "CCC"]})
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertIn("Too many SMILES strings", payload["error"])

    def test_predict_reports_invalid_smiles_shape(self):
        app: Flask = create_app(FakePredictor(loaded=True))
        client = app.test_client()
        response = client.post("/api/predict", json={"smiles_list": ["", "CCO"]})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["invalid_smiles_count"], 1)
        self.assertIn("invalid_smiles", payload)
        self.assertEqual(payload["invalid_smiles"][0]["error"], "Invalid or empty SMILES string")
        self.assertIn("api_version", payload)

    def test_home_reports_request_limit_and_single_endpoint(self):
        os.environ["MAX_SMILES_PER_REQUEST"] = "7"
        app: Flask = create_app(FakePredictor(loaded=True))
        client = app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["request_limits"]["max_smiles_per_request"], 7)
        self.assertIn("POST /api/predict/single", payload["endpoints"])


if __name__ == "__main__":
    unittest.main()
