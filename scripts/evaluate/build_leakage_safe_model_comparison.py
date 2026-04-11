from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEAKAGE_SAFE_DIR = REPO_ROOT / "models" / "evaluation" / "leakage_safe_regimes"
DEFAULT_COMPARISON_TSV = DEFAULT_LEAKAGE_SAFE_DIR / "multi_model_regime_comparison.tsv"
DEFAULT_STATUS_JSON = DEFAULT_LEAKAGE_SAFE_DIR / "multi_model_regime_status.json"

REGIME_ORDER = ["pair_random", "cell_line_holdout", "compound_holdout", "double_cold_start"]
EXPECTED_MODEL_LAYOUT = {
    "ridge": {
        "pair_random": DEFAULT_LEAKAGE_SAFE_DIR / "regime_summary.tsv",
        "cell_line_holdout": DEFAULT_LEAKAGE_SAFE_DIR / "ridge_cell_line_holdout" / "regime_summary.tsv",
        "compound_holdout": DEFAULT_LEAKAGE_SAFE_DIR / "ridge_compound_holdout" / "regime_summary.tsv",
        "double_cold_start": DEFAULT_LEAKAGE_SAFE_DIR / "ridge_double_cold_start" / "regime_summary.tsv",
    },
    "ols": {
        "pair_random": DEFAULT_LEAKAGE_SAFE_DIR / "ols_pair_random" / "regime_summary.tsv",
        "cell_line_holdout": DEFAULT_LEAKAGE_SAFE_DIR / "ols_cell_line_holdout" / "regime_summary.tsv",
        "compound_holdout": DEFAULT_LEAKAGE_SAFE_DIR / "ols_compound_holdout" / "regime_summary.tsv",
        "double_cold_start": DEFAULT_LEAKAGE_SAFE_DIR / "ols_double_cold_start" / "regime_summary.tsv",
    },
    "legacy_rf": {
        "pair_random": DEFAULT_LEAKAGE_SAFE_DIR / "rf_pair_random" / "regime_summary.tsv",
        "cell_line_holdout": DEFAULT_LEAKAGE_SAFE_DIR / "rf_cell_line_holdout" / "regime_summary.tsv",
        "compound_holdout": DEFAULT_LEAKAGE_SAFE_DIR / "rf_compound_holdout" / "regime_summary.tsv",
        "double_cold_start": DEFAULT_LEAKAGE_SAFE_DIR / "rf_double_cold_start" / "regime_summary.tsv",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate per-model leakage-safe regime summaries into a canonical multi-model comparison shell."
    )
    parser.add_argument("--output-tsv", type=Path, default=DEFAULT_COMPARISON_TSV)
    parser.add_argument("--status-json", type=Path, default=DEFAULT_STATUS_JSON)
    parser.add_argument("--models", nargs="+", default=["ridge", "ols", "legacy_rf"])
    parser.add_argument("--strict", action="store_true", help="Fail if any expected model-regime summary is missing.")
    return parser.parse_args()


def read_summary_if_present(path: Path, regime_name: str, model_name: str) -> pd.DataFrame | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    summary = pd.read_csv(path, sep="\t")
    if summary.empty:
        return None
    required_columns = {
        "regime_name",
        "model_name",
        "folds",
        "mean_mae",
        "mean_rmse",
        "mean_pearson_r",
        "mean_spearman_r",
        "mean_r_squared",
        "total_test_rows",
    }
    missing_columns = required_columns.difference(summary.columns)
    if missing_columns:
        raise ValueError(f"summary file {path} is missing required columns: {sorted(missing_columns)}")
    matches = summary[(summary["regime_name"].astype(str) == regime_name) & (summary["model_name"].astype(str) == model_name)]
    if matches.empty:
        return None
    return matches.iloc[[0]].copy()


def collect_model_rows(models: list[str]) -> tuple[pd.DataFrame, dict]:
    rows: list[pd.DataFrame] = []
    status: dict[str, dict] = {}
    for model_name in models:
        if model_name not in EXPECTED_MODEL_LAYOUT:
            raise ValueError(f"unsupported model layout requested: {model_name}")
        model_status = {"complete": True, "regimes": {}}
        for regime_name in REGIME_ORDER:
            summary_path = EXPECTED_MODEL_LAYOUT[model_name][regime_name]
            row = read_summary_if_present(summary_path, regime_name, model_name)
            model_status["regimes"][regime_name] = {
                "expected_path": str(summary_path),
                "present": row is not None,
            }
            if row is None:
                model_status["complete"] = False
            else:
                rows.append(row)
        status[model_name] = model_status
    if rows:
        comparison = pd.concat(rows, ignore_index=True)
        comparison["regime_name"] = pd.Categorical(comparison["regime_name"], categories=REGIME_ORDER, ordered=True)
        comparison = comparison.sort_values(["model_name", "regime_name"]).reset_index(drop=True)
    else:
        comparison = pd.DataFrame(
            columns=[
                "regime_name",
                "model_name",
                "folds",
                "mean_mae",
                "mean_rmse",
                "mean_pearson_r",
                "mean_spearman_r",
                "mean_r_squared",
                "total_test_rows",
            ]
        )
    return comparison, status


def write_outputs(comparison: pd.DataFrame, status: dict, output_tsv: Path, status_json: Path) -> None:
    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    status_json.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(output_tsv, sep="\t", index=False)
    payload = {
        "models": status,
        "completed_models": [name for name, details in status.items() if details["complete"]],
        "pending_models": [name for name, details in status.items() if not details["complete"]],
        "regime_order": REGIME_ORDER,
    }
    status_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def validate_status(status: dict) -> None:
    missing = []
    for model_name, details in status.items():
        for regime_name, regime_status in details["regimes"].items():
            if not regime_status["present"]:
                missing.append(f"{model_name}:{regime_name}")
    if missing:
        raise FileNotFoundError(f"missing expected regime summaries: {', '.join(missing)}")


def main() -> None:
    args = parse_args()
    comparison, status = collect_model_rows(args.models)
    if args.strict:
        validate_status(status)
    output_tsv = args.output_tsv.resolve()
    status_json = args.status_json.resolve()
    write_outputs(comparison, status, output_tsv, status_json)
    print("summary:")
    print(f"output_tsv: {output_tsv}")
    print(f"status_json: {status_json}")
    print(f"rows_written: {len(comparison)}")
    print(f"completed_models: {[name for name, details in status.items() if details['complete']]}")
    print(f"pending_models: {[name for name, details in status.items() if not details['complete']]}")


if __name__ == "__main__":
    main()
