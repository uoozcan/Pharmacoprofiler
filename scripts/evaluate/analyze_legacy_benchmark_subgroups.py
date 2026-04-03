from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from ._common import REPO_ROOT
except ImportError:
    from _common import REPO_ROOT
DEFAULT_OUTPUT_DIR = REPO_ROOT / "models" / "evaluation" / "legacy_pic50_baseline"
DEFAULT_TISSUE_VOCABULARY_PATH = REPO_ROOT / "configs" / "datasets" / "tissue_vocabulary.tsv"


def compute_global_metrics(df: pd.DataFrame) -> dict[str, float]:
    err = df["pIC50_Pred"] - df["pIC50_True"]
    ss_res = float((err**2).sum())
    ss_tot = float(((df["pIC50_True"] - df["pIC50_True"].mean()) ** 2).sum())
    return {
        "rows": int(len(df)),
        "pearson_r": float(df["pIC50_True"].corr(df["pIC50_Pred"], method="pearson")),
        "spearman_r": float(df["pIC50_True"].corr(df["pIC50_Pred"], method="spearman")),
        "mae": float(err.abs().mean()),
        "mse": float((err**2).mean()),
        "rmse": float(np.sqrt((err**2).mean())),
        "r_squared": float(1 - (ss_res / ss_tot)) if ss_tot > 0 else float("nan"),
        "mean_signed_error": float(err.mean()),
        "underpredict_share": float((err < 0).mean()),
        "overpredict_share": float((err > 0).mean()),
    }


def bootstrap_confidence_intervals(
    df: pd.DataFrame,
    n_bootstrap: int,
    seed: int,
) -> dict[str, dict[str, float]]:
    y_true = df["pIC50_True"].to_numpy()
    y_pred = df["pIC50_Pred"].to_numpy()
    n_rows = len(df)
    rng = np.random.default_rng(seed)
    metrics: list[tuple[float, float, float, float, float]] = []

    for _ in range(n_bootstrap):
        idx = rng.integers(0, n_rows, n_rows)
        yt = y_true[idx]
        yp = y_pred[idx]
        err = yp - yt
        ss_res = float((err**2).sum())
        ss_tot = float(((yt - yt.mean()) ** 2).sum())
        pearson = float(pd.Series(yt).corr(pd.Series(yp), method="pearson"))
        spearman = float(pd.Series(yt).corr(pd.Series(yp), method="spearman"))
        mae = float(np.abs(err).mean())
        rmse = float(np.sqrt((err**2).mean()))
        r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else float("nan")
        metrics.append((pearson, spearman, mae, rmse, r2))

    arr = np.array(metrics, dtype=float)
    metric_names = ["pearson_r", "spearman_r", "mae", "rmse", "r_squared"]
    summary: dict[str, dict[str, float]] = {}
    for i, metric_name in enumerate(metric_names):
        col = arr[:, i]
        summary[metric_name] = {
            "mean": float(np.nanmean(col)),
            "ci95_low": float(np.nanpercentile(col, 2.5)),
            "ci95_high": float(np.nanpercentile(col, 97.5)),
        }
    return summary


def compute_group_metrics(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    tmp = df.copy()
    tmp["err"] = tmp["pIC50_Pred"] - tmp["pIC50_True"]
    grouped = (
        tmp.groupby(group_col)
        .apply(
            lambda x: pd.Series(
                {
                    "n": int(len(x)),
                    "pearson_r": float(x["pIC50_True"].corr(x["pIC50_Pred"], method="pearson")),
                    "spearman_r": float(x["pIC50_True"].corr(x["pIC50_Pred"], method="spearman")),
                    "mae": float(x["err"].abs().mean()),
                    "mean_signed_error": float(x["err"].mean()),
                }
            )
        )
        .reset_index()
    )
    return grouped.sort_values("n", ascending=False)


def compute_potency_bin_metrics(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp["err"] = tmp["pIC50_Pred"] - tmp["pIC50_True"]
    bins = [-np.inf, 5.5, 6.5, 7.5, np.inf]
    labels = ["<=5.5", "5.5-6.5", "6.5-7.5", ">7.5"]
    tmp["potency_bin"] = pd.cut(tmp["pIC50_True"], bins=bins, labels=labels)
    grouped = (
        tmp.groupby("potency_bin", observed=False)
        .apply(
            lambda x: pd.Series(
                {
                    "n": int(len(x)),
                    "pearson_r": float(x["pIC50_True"].corr(x["pIC50_Pred"], method="pearson")),
                    "spearman_r": float(x["pIC50_True"].corr(x["pIC50_Pred"], method="spearman")),
                    "mae": float(x["err"].abs().mean()),
                    "mean_signed_error": float(x["err"].mean()),
                    "true_mean": float(x["pIC50_True"].mean()),
                    "pred_mean": float(x["pIC50_Pred"].mean()),
                }
            )
        )
        .reset_index()
    )
    return grouped


def extract_top_error_examples(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    tmp = df.copy()
    tmp["signed_error"] = tmp["pIC50_Pred"] - tmp["pIC50_True"]
    tmp["abs_error"] = tmp["signed_error"].abs()
    return tmp.sort_values("abs_error", ascending=False).head(top_n).reset_index(drop=True)


def compute_calibration_summary(df: pd.DataFrame) -> dict[str, float]:
    x = df["pIC50_True"].to_numpy(dtype=float)
    y = df["pIC50_Pred"].to_numpy(dtype=float)
    design = np.vstack([x, np.ones(len(x))]).T
    slope, intercept = np.linalg.lstsq(design, y, rcond=None)[0]
    return {
        "global_slope": float(slope),
        "global_intercept": float(intercept),
    }


def add_tissue_from_reconstruction(pred_df: pd.DataFrame, reconstructed_path: Path) -> pd.DataFrame:
    reconstructed_df = pd.read_csv(reconstructed_path, sep="\t")
    key_cols = ["CELL_LINE_NAME_edited", "DRUG_NAME_edited", "TISSUE_NAME"]
    tissue_map = reconstructed_df[key_cols].drop_duplicates()
    merged = pred_df.merge(
        tissue_map,
        left_on=["CELL_LINE_NAME", "DRUG_NAME"],
        right_on=["CELL_LINE_NAME_edited", "DRUG_NAME_edited"],
        how="left",
    )
    merged["TISSUE_NAME"] = merged["TISSUE_NAME"].fillna("UNKNOWN")
    return merged


def load_tissue_vocabulary(vocabulary_path: Path) -> pd.DataFrame:
    vocabulary_df = pd.read_csv(vocabulary_path, sep="\t").fillna("")
    required_cols = {"raw_label", "normalized_code", "display_label", "merge_into_code", "note"}
    missing = required_cols.difference(vocabulary_df.columns)
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise ValueError(f"Missing required tissue vocabulary columns: {missing_str}")
    return vocabulary_df


def normalize_tissues(tissue_df: pd.DataFrame, vocabulary_df: pd.DataFrame) -> pd.DataFrame:
    vocab = vocabulary_df.copy()
    effective_code = np.where(
        vocab["merge_into_code"].astype(str).str.len() > 0,
        vocab["merge_into_code"],
        vocab["normalized_code"],
    )
    vocab["effective_code"] = effective_code
    lookup = vocab[["raw_label", "effective_code", "display_label"]].rename(
        columns={
            "raw_label": "TISSUE_NAME",
            "effective_code": "TISSUE_CODE",
            "display_label": "TISSUE_DISPLAY",
        }
    )
    merged = tissue_df.merge(lookup, on="TISSUE_NAME", how="left")
    unmapped = sorted(merged.loc[merged["TISSUE_CODE"].isna(), "TISSUE_NAME"].dropna().unique().tolist())
    if unmapped:
        raise ValueError(f"Unmapped tissue labels in reconstructed benchmark data: {', '.join(unmapped)}")
    return merged


def compute_normalized_tissue_metrics(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp["err"] = tmp["pIC50_Pred"] - tmp["pIC50_True"]
    grouped = (
        tmp.groupby(["TISSUE_CODE", "TISSUE_DISPLAY"], as_index=False)
        .apply(
            lambda x: pd.Series(
                {
                    "n": int(len(x)),
                    "pearson_r": float(x["pIC50_True"].corr(x["pIC50_Pred"], method="pearson")),
                    "spearman_r": float(x["pIC50_True"].corr(x["pIC50_Pred"], method="spearman")),
                    "mae": float(x["err"].abs().mean()),
                    "mean_signed_error": float(x["err"].mean()),
                }
            )
        )
        .reset_index(drop=True)
    )
    return grouped.sort_values("n", ascending=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze subgroup behavior from legacy benchmark outputs.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory containing ccle_predictions.tsv and benchmark outputs.",
    )
    parser.add_argument(
        "--predictions",
        type=Path,
        default=None,
        help="Optional path override for ccle_predictions.tsv.",
    )
    parser.add_argument(
        "--reconstructed-ccle",
        type=Path,
        default=None,
        help="Optional path override for ccle_response_reconstructed.tsv.",
    )
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=1000,
        help="Number of bootstrap resamples for CI estimation.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for bootstrap CI estimation.",
    )
    parser.add_argument(
        "--tissue-vocabulary",
        type=Path,
        default=DEFAULT_TISSUE_VOCABULARY_PATH,
        help="Versioned tissue vocabulary used for canonical normalized reporting.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = (args.predictions or (output_dir / "ccle_predictions.tsv")).resolve()
    reconstructed_path = (args.reconstructed_ccle or (output_dir / "ccle_response_reconstructed.tsv")).resolve()
    tissue_vocabulary_path = args.tissue_vocabulary.resolve()

    pred_df = pd.read_csv(predictions_path, sep="\t")
    global_metrics = compute_global_metrics(pred_df)
    bootstrap_ci = bootstrap_confidence_intervals(pred_df, args.bootstrap_samples, args.seed)
    calibration_summary = compute_calibration_summary(pred_df)

    drug_metrics = compute_group_metrics(pred_df, "DRUG_NAME")
    potency_bin_metrics = compute_potency_bin_metrics(pred_df)
    top_error_examples = extract_top_error_examples(pred_df)
    tissue_metrics_raw = None
    tissue_metrics_normalized = None
    if reconstructed_path.exists():
        with_tissue = add_tissue_from_reconstruction(pred_df, reconstructed_path)
        vocabulary_df = load_tissue_vocabulary(tissue_vocabulary_path)
        with_tissue_normalized = normalize_tissues(with_tissue, vocabulary_df)
        tissue_metrics_raw = compute_group_metrics(with_tissue, "TISSUE_NAME")
        tissue_metrics_normalized = compute_normalized_tissue_metrics(with_tissue_normalized)
        top_error_examples = with_tissue_normalized.merge(
            top_error_examples[["CELL_LINE_NAME", "DRUG_NAME", "pIC50_True", "pIC50_Pred", "signed_error", "abs_error"]],
            on=["CELL_LINE_NAME", "DRUG_NAME", "pIC50_True", "pIC50_Pred"],
            how="right",
        )[
            [
                "CELL_LINE_NAME",
                "DRUG_NAME",
                "TISSUE_NAME",
                "TISSUE_CODE",
                "TISSUE_DISPLAY",
                "pIC50_True",
                "pIC50_Pred",
                "signed_error",
                "abs_error",
            ]
        ]

    summary = {
        "source_files": {
            "predictions": str(predictions_path),
            "reconstructed_ccle": str(reconstructed_path) if reconstructed_path.exists() else None,
            "tissue_vocabulary": str(tissue_vocabulary_path) if reconstructed_path.exists() else None,
        },
        "global_metrics": global_metrics,
        "bootstrap_ci_95": bootstrap_ci,
        "calibration": calibration_summary,
    }

    (output_dir / "subgroup_analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    drug_metrics.to_csv(output_dir / "drug_metrics.tsv", sep="\t", index=False)
    potency_bin_metrics.to_csv(output_dir / "potency_bin_metrics.tsv", sep="\t", index=False)
    top_error_examples.to_csv(output_dir / "top_error_examples.tsv", sep="\t", index=False)
    if tissue_metrics_raw is not None and tissue_metrics_normalized is not None:
        tissue_metrics_raw.to_csv(output_dir / "tissue_metrics_raw.tsv", sep="\t", index=False)
        tissue_metrics_normalized.to_csv(output_dir / "tissue_metrics.tsv", sep="\t", index=False)
        tissue_metrics_normalized.to_csv(output_dir / "tissue_metrics_normalized.tsv", sep="\t", index=False)

    print("summary:")
    print(f"output_dir: {output_dir}")
    print(f"predictions_path: {predictions_path}")
    print(f"reconstructed_path: {reconstructed_path}")
    print(f"tissue_vocabulary_path: {tissue_vocabulary_path}")
    print(f"Wrote subgroup summary: {output_dir / 'subgroup_analysis_summary.json'}")
    print(f"Wrote drug metrics: {output_dir / 'drug_metrics.tsv'}")
    print(f"Wrote potency-bin metrics: {output_dir / 'potency_bin_metrics.tsv'}")
    print(f"Wrote top error examples: {output_dir / 'top_error_examples.tsv'}")
    if tissue_metrics_raw is not None and tissue_metrics_normalized is not None:
        print(f"Wrote raw tissue metrics: {output_dir / 'tissue_metrics_raw.tsv'}")
        print(f"Wrote normalized tissue metrics: {output_dir / 'tissue_metrics.tsv'}")
    else:
        print("Skipped tissue metrics: reconstructed CCLE file not found.")


if __name__ == "__main__":
    main()
