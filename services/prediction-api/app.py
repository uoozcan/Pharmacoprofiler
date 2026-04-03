from __future__ import annotations

from datetime import datetime, timezone
import logging
import os

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


def _request_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _attach_response_metadata(payload: dict) -> dict:
    enriched = dict(payload)
    enriched["api_version"] = API_VERSION
    enriched["request_timestamp"] = _request_timestamp()
    return enriched


def _max_smiles_per_request() -> int:
    return int(os.environ.get("MAX_SMILES_PER_REQUEST", "10"))


def _json_payload() -> dict | None:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def _extract_smiles_list(data: dict, *, single: bool = False) -> tuple[list[str] | None, tuple[dict, int] | None]:
    if single:
        if "smiles" not in data:
            return None, ({"error": 'Missing "smiles" field in request'}, 400)
        if not isinstance(data["smiles"], str):
            return None, ({"error": "SMILES must be a string"}, 400)
        return [data["smiles"]], None

    smiles_input = data.get("smiles")
    if smiles_input is None and "smiles_list" in data:
        smiles_input = data["smiles_list"]
    if smiles_input is None:
        return None, ({"error": 'Either "smiles" or "smiles_list" key is required'}, 400)
    if isinstance(smiles_input, str):
        return [smiles_input], None
    if isinstance(smiles_input, list):
        return smiles_input, None
    return None, ({"error": "SMILES must be a string or list of strings"}, 400)


def _predict_response(predictor: PIC50Predictor, smiles_list: list[str]) -> tuple[dict, int]:
    max_smiles = _max_smiles_per_request()
    if len(smiles_list) > max_smiles:
        return (
            {
                "error": (
                    f"Too many SMILES strings. Maximum allowed: {max_smiles}, provided: {len(smiles_list)}"
                )
            },
            400,
        )

    result = predictor.predict_batch(smiles_list)
    if result.get("error") == "Model not loaded":
        return result, 503
    return _attach_response_metadata(result), 200


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
                "request_limits": {
                    "max_smiles_per_request": _max_smiles_per_request(),
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
        payload.setdefault("dependency_status", predictor.dependency_status())
        payload.setdefault("asset_status", predictor.asset_status())
        payload["api_version"] = API_VERSION
        return jsonify(payload), code

    @app.route("/api/predict", methods=["POST"])
    def predict():
        data = _json_payload()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        smiles_list, error = _extract_smiles_list(data, single=False)
        if error is not None:
            payload, code = error
            return jsonify(payload), code
        payload, code = _predict_response(predictor, smiles_list or [])
        return jsonify(payload), code

    @app.route("/api/predict/single", methods=["POST"])
    def predict_single():
        data = _json_payload()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        smiles_list, error = _extract_smiles_list(data, single=True)
        if error is not None:
            payload, code = error
            return jsonify(payload), code
        payload, code = _predict_response(predictor, smiles_list or [])
        return jsonify(payload), code

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    LOGGER.info("Starting pIC50 Prediction API on %s:%s", host, port)
    app.run(host=host, port=port, debug=debug)
