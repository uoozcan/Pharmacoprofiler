from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd

try:
    from ._common import (
        DEFAULT_CONFIG_PATH,
        REPO_ROOT,
        fingerprint_map_from_gdsc,
        load_json,
        normalize_token,
        resolve_benchmark_paths,
    )
except ImportError:
    from _common import (
        DEFAULT_CONFIG_PATH,
        REPO_ROOT,
        fingerprint_map_from_gdsc,
        load_json,
        normalize_token,
        resolve_benchmark_paths,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconstruct the CCLE cross-domain benchmark input.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Benchmark config JSON describing legacy inputs and default output paths.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory override.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    config = load_json(config_path)
    output_override = str(args.output_dir.resolve()) if args.output_dir else os.environ.get(
        "PHARMACOPROFILER_BENCHMARK_OUTPUT_DIR"
    )
    paths = resolve_benchmark_paths(config, output_dir_override=output_override)

    gdsc_df = pd.read_csv(paths.gdsc_response_path, sep="\t")
    ccle_vector_df = pd.read_csv(paths.ccle_vector_path, sep="\t", usecols=["CELL_LINE_NAME"])
    ccle_raw_df = pd.read_csv(paths.raw_ccle_response_path, sep="\t")

    fingerprint_map = fingerprint_map_from_gdsc(gdsc_df)
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

    output_path = paths.output_dir / "ccle_response_reconstructed.tsv"
    summary_path = paths.output_dir / "ccle_response_reconstruction_summary.json"
    reconstruction_summary["source_mode"] = "reconstructed_from_raw"
    reconstruction_summary["source_path"] = str(paths.raw_ccle_response_path)

    reconstructed_df.to_csv(output_path, sep="\t", index=False)
    summary_path.write_text(json.dumps(reconstruction_summary, indent=2), encoding="utf-8")

    print("summary:")
    print(f"config_path: {config_path}")
    print(f"preferred_output_dir: {(REPO_ROOT / config['output_dir']).resolve()}")
    print(f"output_dir: {paths.output_dir}")
    print(f"Wrote reconstructed CCLE benchmark input to: {output_path}")
    print(f"Wrote reconstruction summary to: {summary_path}")
    print(json.dumps(reconstruction_summary, indent=2))


if __name__ == "__main__":
    main()
