from __future__ import annotations

import logging
import os

import pandas as pd
from flask import Flask, jsonify, request

try:
    from flask_cors import CORS
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    def CORS(app: Flask) -> Flask:
        return app

try:
    from .predictor import PIC50Predictor
except ImportError:
    from predictor import PIC50Predictor


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
API_VERSION = "1.0.0"


def create_app(predictor_instance: PIC50Predictor | None = None) -> Flask:
    app = Flask(__name__)
    CORS(app)
    predictor = predictor_instance or PIC50Predictor()
    if predictor_instance is None:
        predictor.load_model_and_data()
    app.config["PREDICTOR"] = predictor

    @app.route("/", methods=["GET"])
    def home():
        return jsonify(
            {
                "service": "pIC50 Prediction API",
                "version": API_VERSION,
                "status": "running",
                "model_loaded": predictor.is_loaded,
                "endpoints": {
                    "POST /api/predict": "Predict pIC50 values from SMILES",
                    "POST /api/predict/single": "Predict pIC50 for a single SMILES string",
                    "GET /api/health": "Health check",
                    "GET /api/info": "Model information",
                },
                "asset_dir": str(predictor.asset_dir),
                "dependency_status": predictor.dependency_status(),
            }
        )

    @app.route("/api/health", methods=["GET"])
    def health_check():
        code = 200 if predictor.is_loaded else 503
        return (
            jsonify(
                {
                    "status": "healthy" if predictor.is_loaded else "degraded",
                    "model_loaded": predictor.is_loaded,
                    "cell_lines_count": len(predictor.main_cl_list),
                    "service": "pIC50 Prediction API",
                    "version": API_VERSION,
                    "load_error": predictor.load_error,
                    "dependency_status": predictor.dependency_status(),
                }
            ),
            code,
        )

    @app.route("/api/info", methods=["GET"])
    def info():
        code = 200 if predictor.is_loaded else 503
        payload = predictor.info()
        payload["api_version"] = API_VERSION
        return jsonify(payload), code

    @app.route("/api/predict", methods=["POST"])
    def predict():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        smiles_input = data.get("smiles")
        if smiles_input is None and "smiles_list" in data:
            smiles_input = data["smiles_list"]
        if smiles_input is None:
            return jsonify({"error": 'Either "smiles" or "smiles_list" key is required'}), 400

        if isinstance(smiles_input, str):
            smiles_list = [smiles_input]
        elif isinstance(smiles_input, list):
            smiles_list = smiles_input
        else:
            return jsonify({"error": "SMILES must be a string or list of strings"}), 400

        max_smiles = int(os.environ.get("MAX_SMILES_PER_REQUEST", "10"))
        if len(smiles_list) > max_smiles:
            return (
                jsonify(
                    {
                        "error": f"Too many SMILES strings. Maximum allowed: {max_smiles}, provided: {len(smiles_list)}"
                    }
                ),
                400,
            )

        result = predictor.predict_batch(smiles_list)
        if "error" in result and result["error"] == "Model not loaded":
            return jsonify(result), 503

        result["api_version"] = API_VERSION
        result["request_timestamp"] = pd.Timestamp.now().isoformat()
        return jsonify(result)

    @app.route("/api/predict/single", methods=["POST"])
    def predict_single():
        data = request.get_json()
        if not data or "smiles" not in data:
            return jsonify({"error": 'Missing "smiles" field in request'}), 400
        if not isinstance(data["smiles"], str):
            return jsonify({"error": "SMILES must be a string"}), 400
        result = predictor.predict_batch([data["smiles"]])
        if "error" in result and result["error"] == "Model not loaded":
            return jsonify(result), 503
        result["api_version"] = API_VERSION
        result["request_timestamp"] = pd.Timestamp.now().isoformat()
        return jsonify(result)

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    LOGGER.info("Starting pIC50 Prediction API on %s:%s", host, port)
    app.run(host=host, port=port, debug=debug)
