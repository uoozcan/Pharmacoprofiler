from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import joblib
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    joblib = None

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    Chem = None
    AllChem = None


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class AssetConfig:
    omics_filename: str = "GDSC_extracted_988_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt"
    cell_line_filename: str = "GDSC_988_cell_line_name_main_fix_RRID_v1.txt"
    model_filename: str = "GDSC_CCLE_cross_domain_mode_7_v4.joblib"


def resolve_asset_dir() -> Path:
    env_path = os.environ.get("PHARMACOPROFILER_ASSET_DIR")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return Path(__file__).resolve().parent / "assets"


class PIC50Predictor:
    def __init__(self, asset_dir: Path | None = None, asset_config: AssetConfig | None = None):
        self.asset_dir = asset_dir or resolve_asset_dir()
        self.asset_config = asset_config or AssetConfig()
        self.omics_file: pd.DataFrame | None = None
        self.cl_dict_file: pd.DataFrame | None = None
        self.loaded_model: Any | None = None
        self.cl_tissue_dict: dict[str, str] = {}
        self.cl_rrid_dict: dict[str, str] = {}
        self.cl_main_dict: dict[str, str] = {}
        self.main_cl_list: list[str] = []
        self.omics_lookup: dict[str, np.ndarray] = {}
        self.omics_feature_count = 0
        self.is_loaded = False
        self.load_error: str | None = None

    def _asset_path(self, filename: str) -> Path:
        return self.asset_dir / filename

    def required_assets(self) -> dict[str, Path]:
        return {
            "omics_file": self._asset_path(self.asset_config.omics_filename),
            "cell_line_file": self._asset_path(self.asset_config.cell_line_filename),
            "model_file": self._asset_path(self.asset_config.model_filename),
        }

    def asset_status(self) -> dict[str, dict[str, Any]]:
        status: dict[str, dict[str, Any]] = {}
        for label, path in self.required_assets().items():
            entry = {"path": str(path), "exists": path.exists()}
            if path.exists():
                entry["size_bytes"] = path.stat().st_size
            status[label] = entry
        return status

    def dependency_status(self) -> dict[str, bool]:
        return {
            "joblib": joblib is not None,
            "rdkit": Chem is not None and AllChem is not None,
        }

    def load_model_and_data(self) -> bool:
        try:
            LOGGER.info("Loading prediction assets from %s", self.asset_dir)
            dependency_status = self.dependency_status()
            missing_dependencies = [name for name, available in dependency_status.items() if not available]
            if missing_dependencies:
                self.load_error = "Missing required Python dependencies: " + ", ".join(missing_dependencies)
                LOGGER.warning(self.load_error)
                self.is_loaded = False
                return False

            assets = self.required_assets()
            missing = [label for label, path in assets.items() if not path.exists()]
            if missing:
                self.load_error = (
                    "Missing required prediction assets: "
                    + ", ".join(f"{label}={assets[label]}" for label in missing)
                )
                LOGGER.warning(self.load_error)
                self.is_loaded = False
                return False

            self.omics_file = pd.read_csv(assets["omics_file"], delimiter="\t")
            self.cl_dict_file = pd.read_csv(assets["cell_line_file"], delimiter="\t")
            self.loaded_model = joblib.load(assets["model_file"])

            self.cl_dict_file = self.cl_dict_file.rename(columns={"edited": "CELL_LINE_NAME"})
            self.main_cl_list = self.cl_dict_file["CELL_LINE_NAME"].tolist()
            self.cl_main_dict = dict(zip(self.cl_dict_file["CELL_LINE_NAME"], self.cl_dict_file["main"]))
            self.cl_tissue_dict = dict(zip(self.cl_dict_file["CELL_LINE_NAME"], self.cl_dict_file["TISSUE"]))
            self.cl_rrid_dict = dict(zip(self.cl_dict_file["CELL_LINE_NAME"], self.cl_dict_file["RRID"]))
            omics_only_df = self.omics_file.set_index("CELL_LINE_NAME")
            self.omics_feature_count = int(omics_only_df.shape[1])
            self.omics_lookup = {
                cell_line: row.to_numpy(dtype=np.float32)
                for cell_line, row in omics_only_df.iterrows()
            }

            self.is_loaded = True
            self.load_error = None
            LOGGER.info("Loaded predictor with %s cell lines", len(self.main_cl_list))
            return True
        except Exception as exc:  # pragma: no cover - defensive service path
            self.load_error = str(exc)
            self.is_loaded = False
            LOGGER.exception("Failed to load prediction assets")
            return False

    def smiles_to_ecfp4(self, smiles_string: str) -> list[int] | None:
        if Chem is None or AllChem is None:
            LOGGER.error("RDKit is not available in the current environment")
            return None
        try:
            mol = Chem.MolFromSmiles(smiles_string.strip())
            if mol is None:
                return None
            ecfp4_fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=1024)
            return [int(bit) for bit in ecfp4_fp.ToBitString()]
        except Exception:
            LOGGER.exception("Error converting SMILES to ECFP4")
            return None

    def _format_invalid_result(self, smiles_list: list[Any], invalid_smiles: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "total_smiles_submitted": len(smiles_list),
            "valid_smiles_count": 0,
            "invalid_smiles_count": len(invalid_smiles),
            "predictions": {},
            "total_predictions": 0,
            "invalid_smiles": invalid_smiles,
        }

    def predict_batch(self, smiles_list: list[Any]) -> dict[str, Any]:
        if not self.is_loaded or self.omics_file is None or self.cl_dict_file is None or self.loaded_model is None:
            return {
                "error": "Model not loaded",
                "asset_status": self.asset_status(),
                "load_error": self.load_error,
            }

        valid_compounds: list[dict[str, Any]] = []
        invalid_smiles: list[dict[str, Any]] = []
        for smiles in smiles_list:
            if not isinstance(smiles, str) or not smiles.strip():
                invalid_smiles.append({"smiles": smiles, "error": "Invalid or empty SMILES string"})
                continue
            ecfp4_bits = self.smiles_to_ecfp4(smiles)
            if ecfp4_bits is None:
                invalid_smiles.append({"smiles": smiles, "error": "Could not parse SMILES"})
                continue
            valid_compounds.append({"smiles": smiles, "ecfp4": ecfp4_bits})

        if not valid_compounds:
            return self._format_invalid_result(smiles_list, invalid_smiles)

        all_data: list[dict[str, Any]] = []
        for compound in valid_compounds:
            for cell_line in self.main_cl_list:
                omics_features = self.omics_lookup.get(cell_line)
                if omics_features is None:
                    continue
                combined_features = list(omics_features) + compound["ecfp4"]
                all_data.append(
                    {"smiles": compound["smiles"], "cell_line": cell_line, "features": combined_features}
                )

        feature_matrix = np.array([row["features"] for row in all_data], dtype=np.float32)
        predictions = self.loaded_model.predict(feature_matrix) if len(all_data) else []

        grouped_predictions: dict[str, list[dict[str, Any]]] = {}
        for i, data_row in enumerate(all_data):
            smiles = data_row["smiles"]
            cell_line = data_row["cell_line"]
            grouped_predictions.setdefault(smiles, []).append(
                {
                    "CELL_LINE_NAME": self.cl_main_dict.get(cell_line, cell_line),
                    "RRID": self.cl_rrid_dict.get(cell_line, ""),
                    "TISSUE": self.cl_tissue_dict.get(cell_line, ""),
                    "pIC50_Prediction": float(predictions[i]),
                }
            )

        result = {
            "total_smiles_submitted": len(smiles_list),
            "valid_smiles_count": len(valid_compounds),
            "invalid_smiles_count": len(invalid_smiles),
            "predictions": grouped_predictions,
            "total_predictions": int(len(predictions)),
            "model_version": self.asset_config.model_filename,
            "feature_schema_version": "omics_3747_plus_ecfp4_1024_v1",
        }
        if invalid_smiles:
            result["invalid_smiles"] = invalid_smiles
        return result

    def info(self) -> dict[str, Any]:
        if not self.is_loaded or self.omics_file is None:
            return {
                "model_loaded": False,
                "asset_status": self.asset_status(),
                "load_error": self.load_error,
                "dependency_status": self.dependency_status(),
            }
        return {
            "model_loaded": True,
            "model_info": {
                "dataset": "GDSC-trained cross-domain pIC50 predictor",
                "cell_lines_count": len(self.main_cl_list),
                "omics_features": self.omics_feature_count,
                "ecfp4_features": 1024,
                "total_features": int(self.omics_feature_count + 1024),
                "available_tissues": len(set(self.cl_tissue_dict.values())),
                "model_version": self.asset_config.model_filename,
                "feature_schema_version": "omics_3747_plus_ecfp4_1024_v1",
            },
            "asset_status": self.asset_status(),
            "dependency_status": self.dependency_status(),
        }


def load_artifact_manifest(manifest_path: Path) -> dict[str, Any]:
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
