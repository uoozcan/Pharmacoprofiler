from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "configs" / "models" / "legacy-pic50-benchmark-config.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_token(value: Any) -> str:
    return "".join(character for character in str(value).lower() if character.isalnum())


def ensure_output_dir(preferred_path: Path) -> Path:
    override = os.environ.get("PHARMACOPROFILER_BENCHMARK_OUTPUT_DIR")
    if override:
        output_dir = Path(override).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    try:
        preferred_path.mkdir(parents=True, exist_ok=True)
        return preferred_path
    except OSError:
        fallback_dir = Path("/tmp/pharmacoprofiler_outputs/legacy_pic50_baseline").resolve()
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir


def main() -> None:
    config = load_json(CONFIG_PATH)
    legacy_root = Path(config["legacy_root"]).resolve()
    output_dir = ensure_output_dir((REPO_ROOT / config["output_dir"]).resolve())

    gdsc_path = (legacy_root / config["gdsc_response_path"]).resolve()
    ccle_vector_path = (legacy_root / config["ccle_vector_path"]).resolve()
    raw_ccle_response_path = (legacy_root / config["raw_ccle_response_path"]).resolve()

    gdsc_df = pd.read_csv(gdsc_path, sep="\t")
    ccle_vector_df = pd.read_csv(ccle_vector_path, sep="\t", usecols=["CELL_LINE_NAME"])
    ccle_raw_df = pd.read_csv(raw_ccle_response_path, sep="\t")

    fingerprint_map: dict[str, str] = {}
    for _, row in gdsc_df[["DRUG_NAME", "DRUG_NAME_edited", "FINGERPRINT"]].dropna().iterrows():
        fingerprint = str(row["FINGERPRINT"])
        if len(fingerprint) != 1024:
            continue
        for source_value in (row["DRUG_NAME"], row["DRUG_NAME_edited"]):
            normalized = normalize_token(source_value)
            if normalized and normalized not in fingerprint_map:
                fingerprint_map[normalized] = fingerprint

    reconstructed_df = ccle_raw_df.copy()
    reconstructed_df["CELL_LINE_NAME_edited"] = reconstructed_df["CELL_LINE_NAME_edited"].astype(str).str.lower()
    reconstructed_df["DRUG_NAME_edited"] = reconstructed_df["DRUG_NAME"].map(normalize_token)
    reconstructed_df["FINGERPRINT"] = reconstructed_df["DRUG_NAME_edited"].map(fingerprint_map)
    reconstructed_df["pIC50"] = reconstructed_df[config["raw_target_column"]]

    valid_cell_lines = set(ccle_vector_df["CELL_LINE_NAME"].astype(str).str.lower().tolist())
    reconstructed_df = reconstructed_df[
        reconstructed_df["CELL_LINE_NAME_edited"].isin(valid_cell_lines) & reconstructed_df["FINGERPRINT"].notna()
    ].copy()
    reconstructed_df.sort_values(by=["CELL_LINE_NAME_edited", "DRUG_NAME_edited"], inplace=True)

    reconstruction_summary = {
        "raw_rows": int(len(ccle_raw_df)),
        "reconstructed_rows": int(len(reconstructed_df)),
        "raw_unique_drugs": int(ccle_raw_df["DRUG_NAME"].nunique()),
        "reconstructed_unique_drugs": int(reconstructed_df["DRUG_NAME_edited"].nunique()),
        "raw_unique_cell_lines": int(ccle_raw_df["CELL_LINE_NAME_edited"].nunique()),
        "reconstructed_unique_cell_lines": int(reconstructed_df["CELL_LINE_NAME_edited"].nunique()),
        "gdsc_unique_drugs": int(gdsc_df["DRUG_NAME_edited"].nunique()),
        "ccle_vector_cell_lines": int(ccle_vector_df["CELL_LINE_NAME"].nunique()),
        "mapped_drugs": sorted(reconstructed_df["DRUG_NAME_edited"].unique().tolist()),
    }

    output_path = output_dir / "ccle_response_reconstructed.tsv"
    summary_path = output_dir / "ccle_response_reconstruction_summary.json"

    reconstructed_df.to_csv(output_path, sep="\t", index=False)
    summary_path.write_text(json.dumps(reconstruction_summary, indent=2), encoding="utf-8")

    print(f"Preferred output dir: {(REPO_ROOT / config['output_dir']).resolve()}")
    print(f"Actual output dir: {output_dir}")
    print(f"Wrote reconstructed CCLE benchmark input to: {output_path}")
    print(f"Wrote reconstruction summary to: {summary_path}")
    print(json.dumps(reconstruction_summary, indent=2))


if __name__ == "__main__":
    main()
