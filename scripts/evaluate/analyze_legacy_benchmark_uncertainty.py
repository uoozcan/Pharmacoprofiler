from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import joblib
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    joblib = None

try:
    from scipy.stats import pearsonr
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    pearsonr = None

try:
    from sklearn.ensemble._forest import _generate_sample_indices, _get_n_samples_bootstrap
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    _generate_sample_indices = None
    _get_n_samples_bootstrap = None

try:
    from ._common import (
        DEFAULT_CONFIG_PATH,
        BenchmarkPaths,
        load_json,
        normalize_token,
        require_existing,
        resolve_benchmark_paths,
        resolve_manifest_artifacts,
    )
    from .run_legacy_benchmark_baseline import build_test_matrix, load_or_reconstruct_ccle_response, split_fingerprints
    from .analyze_legacy_benchmark_subgroups import (
        DEFAULT_TISSUE_VOCABULARY_PATH,
        load_tissue_vocabulary,
        normalize_tissues,
    )
except ImportError:
    from _common import (
        DEFAULT_CONFIG_PATH,
        BenchmarkPaths,
        load_json,
        normalize_token,
        require_existing,
        resolve_benchmark_paths,
        resolve_manifest_artifacts,
    )
    from run_legacy_benchmark_baseline import build_test_matrix, load_or_reconstruct_ccle_response, split_fingerprints
    from analyze_legacy_benchmark_subgroups import (
        DEFAULT_TISSUE_VOCABULARY_PATH,
        load_tissue_vocabulary,
        normalize_tissues,
    )


DEFAULT_CONFORMAL_LEVEL = 0.90
DEFAULT_CONFORMAL_LEVELS = (0.50, 0.60, 0.70, 0.80, 0.90, 0.95)
DEFAULT_CALIBRATION_ROWS = 10000
DEFAULT_CALIBRATION_SEED = 17


def require_runtime_dependencies() -> None:
    missing: list[str] = []
    if joblib is None:
        missing.append("joblib")
    if pearsonr is None:
        missing.append("scipy")
    if _generate_sample_indices is None or _get_n_samples_bootstrap is None:
        missing.append("scikit-learn")
    if missing:
        raise SystemExit(
            "Missing runtime dependencies for uncertainty analysis: "
            + ", ".join(missing)
            + ". Install the benchmark dependencies and rerun."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze uncertainty and applicability proxies for the canonical legacy pIC50 benchmark."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Benchmark config JSON describing legacy inputs and output locations.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory override.",
    )
    parser.add_argument(
        "--tissue-vocabulary",
        type=Path,
        default=DEFAULT_TISSUE_VOCABULARY_PATH,
        help="Versioned tissue vocabulary for manuscript-facing subgroup reporting.",
    )
    return parser.parse_args()


def resolve_output_dir(args: argparse.Namespace, paths: BenchmarkPaths) -> Path:
    override = args.output_dir.resolve() if args.output_dir else None
    env_override = os.environ.get("PHARMACOPROFILER_BENCHMARK_OUTPUT_DIR")
    if override is not None:
        override.mkdir(parents=True, exist_ok=True)
        return override
    if env_override:
        output_dir = Path(env_override).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    return paths.output_dir


def compute_tree_interval_predictions(model: Any, feature_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    estimator_predictions = np.vstack(
        [estimator.predict(feature_matrix).astype(np.float32) for estimator in model.estimators_]
    )
    return (
        estimator_predictions.std(axis=0, ddof=1),
        np.quantile(estimator_predictions, 0.05, axis=0),
        np.quantile(estimator_predictions, 0.95, axis=0),
    )


def collect_tree_predictions(model: Any, feature_matrix: np.ndarray) -> np.ndarray:
    return np.vstack([estimator.predict(feature_matrix).astype(np.float32) for estimator in model.estimators_])


def build_calibration_reference_split(
    gdsc_response_df: pd.DataFrame,
    gdsc_omics_df: pd.DataFrame,
    target_column: str,
    sample_size: int = DEFAULT_CALIBRATION_ROWS,
    seed: int = DEFAULT_CALIBRATION_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    eligible = gdsc_response_df.copy()
    valid_cell_lines = set(gdsc_omics_df["CELL_LINE_NAME"].astype(str).tolist())
    eligible = eligible[
        eligible["CELL_LINE_NAME_edited"].astype(str).isin(valid_cell_lines)
        & eligible[target_column].notna()
        & eligible["FINGERPRINT"].astype(str).str.len().eq(1024)
    ].copy()
    if eligible.empty:
        raise ValueError("No eligible GDSC rows available for conformal calibration.")

    selected_rows = min(sample_size, len(eligible))
    rng = np.random.default_rng(seed)
    sampled_index = rng.choice(eligible.index.to_numpy(), size=selected_rows, replace=False)
    sampled_response = eligible.loc[sampled_index].copy()
    sampled_response.sort_values(["CELL_LINE_NAME_edited", "DRUG_NAME_edited"], inplace=True)
    sampled_response["source_row_id"] = sampled_response.index.astype(int)
    split_df = split_fingerprints(sampled_response, gdsc_omics_df, target_column)
    split_df["source_row_id"] = sampled_response["source_row_id"].tolist()
    merged_df = pd.merge(gdsc_omics_df, split_df, on="CELL_LINE_NAME", how="inner")
    merged_df = merged_df.dropna(subset=["DRUG_NAME", target_column]).copy()
    features = merged_df.drop(["DRUG_NAME", "CELL_LINE_NAME", target_column, "source_row_id"], axis=1).astype(np.float32)
    labels = merged_df[[target_column]].astype(np.float32)
    calibration_df = pd.concat([features, labels], axis=1)
    metadata = {
        "source": "gdsc_post_training_reference_split",
        "seed": seed,
        "requested_rows": int(sample_size),
        "selected_rows": int(selected_rows),
        "eligible_rows": int(len(eligible)),
        "selected_drugs": int(sampled_response["DRUG_NAME_edited"].nunique()),
        "selected_cell_lines": int(sampled_response["CELL_LINE_NAME_edited"].nunique()),
    }
    return merged_df, calibration_df, metadata


def build_training_row_registry(
    gdsc_response_df: pd.DataFrame,
    gdsc_omics_df: pd.DataFrame,
    target_column: str,
) -> pd.DataFrame:
    registry_response = gdsc_response_df.copy()
    registry_response["source_row_id"] = registry_response.index.astype(int)
    registry_split = registry_response[["CELL_LINE_NAME_edited", "DRUG_NAME_edited", target_column, "source_row_id"]].rename(
        columns={"CELL_LINE_NAME_edited": "CELL_LINE_NAME", "DRUG_NAME_edited": "DRUG_NAME"}
    )
    registry = pd.merge(gdsc_omics_df[["CELL_LINE_NAME"]], registry_split, on="CELL_LINE_NAME", how="inner")
    registry = registry.dropna(subset=["DRUG_NAME", target_column]).copy()
    return registry[["source_row_id"]].reset_index(drop=True)


def compute_oob_scaled_conformal_scores(
    model: Any,
    gdsc_response_df: pd.DataFrame,
    gdsc_omics_df: pd.DataFrame,
    calibration_merged_df: pd.DataFrame,
    calibration_df: pd.DataFrame,
    target_column: str,
) -> tuple[np.ndarray, dict[str, Any]]:
    training_registry = build_training_row_registry(gdsc_response_df, gdsc_omics_df, target_column)
    source_to_position = (
        training_registry.reset_index().drop_duplicates("source_row_id").set_index("source_row_id")["index"]
    )
    calibration_positions = calibration_merged_df["source_row_id"].map(source_to_position)
    if calibration_positions.isna().any():
        raise ValueError("Failed to align calibration rows to the reconstructed GDSC training registry.")

    calibration_positions_array = calibration_positions.to_numpy(dtype=int)
    calibration_features = calibration_df.drop([target_column], axis=1).to_numpy(dtype=np.float32)
    calibration_labels = calibration_df[target_column].to_numpy(dtype=np.float32)
    n_training_rows = int(len(training_registry))
    n_bootstrap = _get_n_samples_bootstrap(n_training_rows, getattr(model, "max_samples", None))

    prediction_sum = np.zeros(len(calibration_df), dtype=np.float64)
    prediction_sq_sum = np.zeros(len(calibration_df), dtype=np.float64)
    prediction_count = np.zeros(len(calibration_df), dtype=np.int32)

    for estimator in model.estimators_:
        sample_indices = _generate_sample_indices(estimator.random_state, n_training_rows, n_bootstrap)
        in_bag = np.zeros(n_training_rows, dtype=bool)
        in_bag[sample_indices] = True
        oob_mask = ~in_bag[calibration_positions_array]
        if not oob_mask.any():
            continue
        estimator_predictions = estimator.predict(calibration_features[oob_mask]).astype(np.float64)
        prediction_sum[oob_mask] += estimator_predictions
        prediction_sq_sum[oob_mask] += estimator_predictions**2
        prediction_count[oob_mask] += 1

    valid_mask = prediction_count > 0
    if not valid_mask.any():
        raise ValueError("No out-of-bag estimator predictions were available for the calibration split.")

    oob_mean = np.divide(
        prediction_sum,
        prediction_count,
        out=np.full_like(prediction_sum, np.nan, dtype=np.float64),
        where=valid_mask,
    )
    oob_second_moment = np.divide(
        prediction_sq_sum,
        prediction_count,
        out=np.zeros_like(prediction_sq_sum, dtype=np.float64),
        where=valid_mask,
    )
    oob_variance = np.maximum(oob_second_moment - (oob_mean**2), 1e-12)
    oob_std = np.sqrt(oob_variance)
    scores = np.abs(calibration_labels[valid_mask] - oob_mean[valid_mask]) / np.maximum(oob_std[valid_mask], 1e-6)
    metadata = {
        "oob_rows": int(valid_mask.sum()),
        "dropped_rows_without_oob_predictions": int((~valid_mask).sum()),
        "mean_oob_estimators_per_row": float(prediction_count[valid_mask].mean()),
        "min_oob_estimators_per_row": int(prediction_count[valid_mask].min()),
        "max_oob_estimators_per_row": int(prediction_count[valid_mask].max()),
    }
    return scores.astype(np.float32), metadata


def nearest_train_cosine_similarity(
    gdsc_omics_df: pd.DataFrame,
    ccle_omics_df: pd.DataFrame,
) -> dict[str, float]:
    gdsc_matrix = gdsc_omics_df.set_index("CELL_LINE_NAME").astype(np.float32)
    ccle_matrix = ccle_omics_df.set_index("CELL_LINE_NAME").astype(np.float32)
    feature_columns = [column for column in gdsc_matrix.columns if column in ccle_matrix.columns]
    gdsc_values = gdsc_matrix[feature_columns].to_numpy(dtype=np.float32)
    ccle_values = ccle_matrix[feature_columns].to_numpy(dtype=np.float32)

    gdsc_norms = np.linalg.norm(gdsc_values, axis=1, keepdims=True)
    ccle_norms = np.linalg.norm(ccle_values, axis=1, keepdims=True)
    gdsc_norms[gdsc_norms == 0] = 1.0
    ccle_norms[ccle_norms == 0] = 1.0

    normalized_gdsc = gdsc_values / gdsc_norms
    normalized_ccle = ccle_values / ccle_norms
    similarity_matrix = normalized_ccle @ normalized_gdsc.T
    nearest_similarity = similarity_matrix.max(axis=1)

    return {
        str(cell_line): float(similarity)
        for cell_line, similarity in zip(ccle_matrix.index.tolist(), nearest_similarity.tolist())
    }


def add_quantile_bins(
    df: pd.DataFrame,
    source_column: str,
    output_column: str,
    labels: list[str],
) -> pd.DataFrame:
    binned = df.copy()
    binned[output_column] = pd.qcut(
        binned[source_column],
        q=len(labels),
        labels=labels,
        duplicates="drop",
    )
    return binned


def summarize_uncertainty_bins(df: pd.DataFrame) -> pd.DataFrame:
    plot_df = add_quantile_bins(
        df,
        source_column="prediction_std",
        output_column="uncertainty_bin",
        labels=["Q1 lowest", "Q2", "Q3", "Q4", "Q5 highest"],
    )
    summary = (
        plot_df.groupby("uncertainty_bin", observed=False)
        .agg(
            n=("CELL_LINE_NAME", "size"),
            mean_prediction_std=("prediction_std", "mean"),
            mae=("absolute_error", "mean"),
            rmse=("squared_error", lambda values: float(np.sqrt(np.mean(values)))),
            interval_coverage_90=("within_tree_interval_90", "mean"),
            mean_signed_error=("signed_error", "mean"),
        )
        .reset_index()
    )
    return summary


def summarize_applicability_bins(df: pd.DataFrame) -> pd.DataFrame:
    plot_df = add_quantile_bins(
        df,
        source_column="nearest_train_cosine",
        output_column="applicability_bin",
        labels=["Q1 lowest", "Q2", "Q3", "Q4", "Q5 highest"],
    )
    summary = (
        plot_df.groupby("applicability_bin", observed=False)
        .agg(
            n=("CELL_LINE_NAME", "size"),
            mean_nearest_train_cosine=("nearest_train_cosine", "mean"),
            mae=("absolute_error", "mean"),
            mean_prediction_std=("prediction_std", "mean"),
            mean_signed_error=("signed_error", "mean"),
        )
        .reset_index()
    )
    return summary


def summarize_cell_line_applicability(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("CELL_LINE_NAME")
        .agg(
            n=("DRUG_NAME", "size"),
            nearest_train_cosine=("nearest_train_cosine", "first"),
            mae=("absolute_error", "mean"),
            rmse=("squared_error", lambda values: float(np.sqrt(np.mean(values)))),
            mean_prediction_std=("prediction_std", "mean"),
            mean_signed_error=("signed_error", "mean"),
        )
        .reset_index()
        .sort_values(["nearest_train_cosine", "mae"], ascending=[True, False])
    )
    return summary


def summarize_interval_calibration(
    estimator_predictions: np.ndarray,
    true_values: np.ndarray,
) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    for nominal_level in [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]:
        alpha = (1.0 - nominal_level) / 2.0
        lower = np.quantile(estimator_predictions, alpha, axis=0)
        upper = np.quantile(estimator_predictions, 1.0 - alpha, axis=0)
        coverage = ((true_values >= lower) & (true_values <= upper)).mean()
        mean_width = float(np.mean(upper - lower))
        rows.append(
            {
                "nominal_coverage": float(nominal_level),
                "empirical_coverage": float(coverage),
                "coverage_gap": float(coverage - nominal_level),
                "mean_interval_width": mean_width,
            }
        )
    return pd.DataFrame(rows)


def conformal_quantile(scores: np.ndarray, nominal_level: float) -> float:
    scores = np.asarray(scores, dtype=float)
    if scores.size == 0:
        raise ValueError("Conformal calibration scores cannot be empty.")
    quantile_level = min(1.0, np.ceil((scores.size + 1) * nominal_level) / scores.size)
    try:
        return float(np.quantile(scores, quantile_level, method="higher"))
    except TypeError:  # pragma: no cover - NumPy compatibility
        return float(np.quantile(scores, quantile_level, interpolation="higher"))


def summarize_conformal_interval_calibration(
    true_values: np.ndarray,
    point_predictions: np.ndarray,
    estimator_predictions: np.ndarray,
    conformal_scores: np.ndarray,
    interval_scale: np.ndarray,
) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    for nominal_level in DEFAULT_CONFORMAL_LEVELS:
        alpha = (1.0 - nominal_level) / 2.0
        raw_lower = np.quantile(estimator_predictions, alpha, axis=0)
        raw_upper = np.quantile(estimator_predictions, 1.0 - alpha, axis=0)
        raw_coverage = float(((true_values >= raw_lower) & (true_values <= raw_upper)).mean())
        raw_width = float(np.mean(raw_upper - raw_lower))

        qhat = conformal_quantile(conformal_scores, nominal_level)
        conformal_lower = point_predictions - (qhat * interval_scale)
        conformal_upper = point_predictions + (qhat * interval_scale)
        conformal_coverage = float(((true_values >= conformal_lower) & (true_values <= conformal_upper)).mean())
        conformal_width = float(np.mean(conformal_upper - conformal_lower))

        rows.append(
            {
                "nominal_coverage": float(nominal_level),
                "raw_empirical_coverage": raw_coverage,
                "conformal_empirical_coverage": conformal_coverage,
                "raw_coverage_gap": float(raw_coverage - nominal_level),
                "conformal_coverage_gap": float(conformal_coverage - nominal_level),
                "raw_mean_interval_width": raw_width,
                "conformal_mean_interval_width": conformal_width,
                "conformal_quantile": qhat,
            }
        )
    return pd.DataFrame(rows)


def posthoc_interval_inflation(
    true_values: np.ndarray,
    lower_values: np.ndarray,
    upper_values: np.ndarray,
    target_coverage: float = 0.90,
) -> dict[str, float]:
    centers = (lower_values + upper_values) / 2.0
    half_width = np.maximum((upper_values - lower_values) / 2.0, 1e-6)
    scaled_residual = np.abs(true_values - centers) / half_width
    inflation_factor = float(np.quantile(scaled_residual, target_coverage))
    adjusted_lower = centers - inflation_factor * half_width
    adjusted_upper = centers + inflation_factor * half_width
    adjusted_coverage = float(((true_values >= adjusted_lower) & (true_values <= adjusted_upper)).mean())
    return {
        "target_coverage": float(target_coverage),
        "inflation_factor": inflation_factor,
        "posthoc_empirical_coverage": adjusted_coverage,
    }


def build_calibrated_prediction_table(
    uncertainty_df: pd.DataFrame,
    conformal_quantile_90: float,
    interval_scale_column: str = "prediction_std",
) -> pd.DataFrame:
    calibrated = uncertainty_df.copy()
    interval_scale = np.maximum(calibrated[interval_scale_column].to_numpy(dtype=float), 1e-6)
    calibrated["uncalibrated_prediction_interval_low_90"] = calibrated["prediction_interval_low_90"]
    calibrated["uncalibrated_prediction_interval_high_90"] = calibrated["prediction_interval_high_90"]
    calibrated["uncalibrated_prediction_interval_width_90"] = (
        calibrated["uncalibrated_prediction_interval_high_90"] - calibrated["uncalibrated_prediction_interval_low_90"]
    )
    calibrated["conformal_interval_scale"] = interval_scale
    calibrated["conformal_prediction_interval_low_90"] = calibrated["pIC50_Pred"] - (conformal_quantile_90 * interval_scale)
    calibrated["conformal_prediction_interval_high_90"] = calibrated["pIC50_Pred"] + (conformal_quantile_90 * interval_scale)
    calibrated["conformal_prediction_interval_width_90"] = (
        calibrated["conformal_prediction_interval_high_90"] - calibrated["conformal_prediction_interval_low_90"]
    )
    calibrated["within_conformal_interval_90"] = (
        (calibrated["pIC50_True"] >= calibrated["conformal_prediction_interval_low_90"])
        & (calibrated["pIC50_True"] <= calibrated["conformal_prediction_interval_high_90"])
    ).astype(float)
    calibrated["prediction_interval_level"] = DEFAULT_CONFORMAL_LEVEL
    calibrated["uncertainty_method"] = "split_conformal_tree_std_scaled"
    calibrated["applicability_score"] = calibrated["nearest_train_cosine"]
    return calibrated


def attach_metadata_and_tissues(
    calibrated_df: pd.DataFrame,
    cell_line_metadata_path: Path,
    tissue_vocabulary_path: Path,
) -> pd.DataFrame:
    metadata_df = pd.read_csv(cell_line_metadata_path, sep="\t").copy()
    metadata_df["edited"] = metadata_df["edited"].astype(str)
    metadata_df["TISSUE"] = metadata_df["TISSUE"].fillna("UNKNOWN").astype(str)
    lookup = metadata_df[["edited", "main", "RRID", "TISSUE"]].rename(
        columns={"edited": "CELL_LINE_NAME", "main": "CELL_LINE_MAIN", "TISSUE": "TISSUE_NAME"}
    )
    merged = calibrated_df.merge(lookup, on="CELL_LINE_NAME", how="left")
    merged["TISSUE_NAME"] = merged["TISSUE_NAME"].fillna("UNKNOWN")
    vocabulary_df = load_tissue_vocabulary(tissue_vocabulary_path)
    try:
        return normalize_tissues(merged, vocabulary_df)
    except ValueError:
        vocab = vocabulary_df.copy()
        vocab["effective_code"] = np.where(
            vocab["merge_into_code"].astype(str).str.len() > 0,
            vocab["merge_into_code"],
            vocab["normalized_code"],
        )
        alias_map = {
            "Bladder": "urinary_tract",
            "Central Nervous System": "central_nervous_system",
            "Esophagus": "oesophagus",
            "Haematopoietic and Lymphoid": "haematopoietic_and_lymphoid_tissue",
            "Head and Neck": "upper_aerodigestive_tract",
            "Large Intestine": "large_intestine",
            "Peripheral Nervous System": "peripheral_nervous_system",
            "UNKNOWN": "unknown",
        }
        vocab["code_key"] = vocab["effective_code"].map(normalize_token)
        vocab["token_key"] = vocab["raw_label"].map(normalize_token)
        token_lookup = (
            vocab.sort_values("raw_label")
            .drop_duplicates("token_key")
            .set_index("token_key")[["effective_code", "display_label"]]
        )
        code_lookup = (
            vocab.sort_values("raw_label")
            .drop_duplicates("code_key")
            .set_index("code_key")[["effective_code", "display_label"]]
        )
        fallback = merged.copy()
        fallback["token_key"] = fallback["TISSUE_NAME"].map(normalize_token)
        fallback["alias_key"] = fallback["TISSUE_NAME"].map(alias_map).fillna("").map(normalize_token)
        fallback["TISSUE_CODE"] = fallback["token_key"].map(token_lookup["effective_code"])
        fallback["TISSUE_DISPLAY"] = fallback["token_key"].map(token_lookup["display_label"])
        alias_resolved = fallback["TISSUE_CODE"].isna() & fallback["alias_key"].ne("")
        fallback.loc[alias_resolved, "TISSUE_CODE"] = fallback.loc[alias_resolved, "alias_key"].map(
            code_lookup["effective_code"]
        )
        fallback.loc[alias_resolved, "TISSUE_DISPLAY"] = fallback.loc[alias_resolved, "alias_key"].map(
            code_lookup["display_label"]
        )
        unresolved = fallback["TISSUE_CODE"].isna()
        fallback.loc[unresolved, "TISSUE_CODE"] = fallback.loc[unresolved, "token_key"].replace("", "unknown")
        fallback.loc[unresolved, "TISSUE_DISPLAY"] = fallback.loc[unresolved, "TISSUE_NAME"].replace("", "UNKNOWN")
        return fallback.drop(columns=["token_key", "alias_key"])


def summarize_conformal_subgroups(df: pd.DataFrame) -> pd.DataFrame:
    potency_df = df.copy()
    potency_df["potency_bin"] = pd.cut(
        potency_df["pIC50_True"],
        bins=[-np.inf, 5.5, 6.5, 7.5, np.inf],
        labels=["<=5.5", "5.5-6.5", "6.5-7.5", ">7.5"],
    )

    subgroup_frames = [
        ("tissue", df.groupby("TISSUE_DISPLAY", dropna=False)),
        ("drug", df.groupby("DRUG_NAME", dropna=False)),
        ("potency_bin", potency_df.groupby("potency_bin", observed=False, dropna=False)),
    ]
    rows: list[dict[str, Any]] = []
    for subgroup_type, grouped in subgroup_frames:
        for subgroup_label, subset in grouped:
            if pd.isna(subgroup_label):
                subgroup_label = "UNKNOWN"
            rows.append(
                {
                    "subgroup_type": subgroup_type,
                    "subgroup_label": str(subgroup_label),
                    "n": int(len(subset)),
                    "raw_interval_coverage_90": float(subset["within_tree_interval_90"].mean()),
                    "conformal_interval_coverage_90": float(subset["within_conformal_interval_90"].mean()),
                    "raw_mean_interval_width_90": float(subset["uncalibrated_prediction_interval_width_90"].mean()),
                    "conformal_mean_interval_width_90": float(
                        subset["conformal_prediction_interval_width_90"].mean()
                    ),
                    "mae": float(subset["absolute_error"].mean()),
                    "mean_signed_error": float(subset["signed_error"].mean()),
                }
            )
    return pd.DataFrame(rows).sort_values(["subgroup_type", "n"], ascending=[True, False]).reset_index(drop=True)


def correlation_or_none(x_values: pd.Series, y_values: pd.Series) -> float | None:
    if pearsonr is None:
        return None
    if x_values.nunique() <= 1 or y_values.nunique() <= 1:
        return None
    return float(pearsonr(x_values, y_values)[0])


def build_summary(
    uncertainty_df: pd.DataFrame,
    uncertainty_bins: pd.DataFrame,
    applicability_bins: pd.DataFrame,
    cell_line_summary: pd.DataFrame,
    interval_calibration: pd.DataFrame,
    conformal_interval_calibration: pd.DataFrame,
    posthoc_calibration: dict[str, float],
    calibration_metadata: dict[str, Any],
    response_metadata: dict[str, Any],
    artifact_paths: dict[str, Path],
) -> dict[str, Any]:
    calibration_90 = interval_calibration.loc[
        interval_calibration["nominal_coverage"] == 0.90
    ].to_dict(orient="records")[0]
    conformal_90 = conformal_interval_calibration.loc[
        conformal_interval_calibration["nominal_coverage"] == 0.90
    ].to_dict(orient="records")[0]
    return {
        "analysis_name": "legacy_pic50_uncertainty_and_applicability",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "ccle_response_source": response_metadata,
        "calibration_reference": calibration_metadata,
        "artifacts": {key: str(path) for key, path in artifact_paths.items()},
        "global": {
            "rows": int(len(uncertainty_df)),
            "cell_lines": int(uncertainty_df["CELL_LINE_NAME"].nunique()),
            "drugs": int(uncertainty_df["DRUG_NAME"].nunique()),
            "mean_prediction_std": float(uncertainty_df["prediction_std"].mean()),
            "median_prediction_std": float(uncertainty_df["prediction_std"].median()),
            "tree_interval_90_coverage": float(uncertainty_df["within_tree_interval_90"].mean()),
            "tree_interval_90_coverage_gap": float(calibration_90["coverage_gap"]),
            "conformal_interval_90_coverage": float(conformal_90["conformal_empirical_coverage"]),
            "conformal_interval_90_coverage_gap": float(conformal_90["conformal_coverage_gap"]),
            "conformal_interval_90_mean_width": float(conformal_90["conformal_mean_interval_width"]),
            "uncertainty_vs_absolute_error_pearson": correlation_or_none(
                uncertainty_df["prediction_std"], uncertainty_df["absolute_error"]
            ),
            "cell_line_similarity_vs_mae_pearson": correlation_or_none(
                cell_line_summary["nearest_train_cosine"], cell_line_summary["mae"]
            ),
        },
        "interval_calibration_90": calibration_90,
        "conformal_interval_calibration_90": conformal_90,
        "posthoc_interval_calibration_90": posthoc_calibration,
        "schema_ready_fields": [
            "prediction_interval",
            "prediction_interval_level",
            "uncertainty_method",
            "applicability_score",
        ],
        "highest_uncertainty_bin": uncertainty_bins.sort_values("mean_prediction_std", ascending=False)
        .head(1)
        .to_dict(orient="records")[0],
        "lowest_applicability_bin": applicability_bins.sort_values("mean_nearest_train_cosine", ascending=True)
        .head(1)
        .to_dict(orient="records")[0],
    }


def build_calibration_summary(
    conformal_interval_calibration: pd.DataFrame,
    conformal_subgroups: pd.DataFrame,
    calibration_metadata: dict[str, Any],
) -> dict[str, Any]:
    calibration_90 = conformal_interval_calibration.loc[
        conformal_interval_calibration["nominal_coverage"] == DEFAULT_CONFORMAL_LEVEL
    ].to_dict(orient="records")[0]
    tissue_subset = conformal_subgroups[conformal_subgroups["subgroup_type"] == "tissue"]
    potency_subset = conformal_subgroups[conformal_subgroups["subgroup_type"] == "potency_bin"]
    return {
        "analysis_name": "legacy_pic50_split_conformal_calibration",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "calibration_reference": calibration_metadata,
        "target_nominal_coverage": DEFAULT_CONFORMAL_LEVEL,
        "global_90": calibration_90,
        "largest_tissue_coverage_gap_90": tissue_subset.assign(
            conformal_gap=lambda frame: frame["conformal_interval_coverage_90"] - DEFAULT_CONFORMAL_LEVEL
        )
        .sort_values("conformal_gap")
        .head(1)
        .to_dict(orient="records")[0],
        "highest_potency_bin_coverage_90": potency_subset.loc[
            potency_subset["subgroup_label"] == ">7.5"
        ].to_dict(orient="records")[0],
    }


def write_outputs(
    output_dir: Path,
    uncertainty_df: pd.DataFrame,
    calibrated_predictions_df: pd.DataFrame,
    uncertainty_bins: pd.DataFrame,
    applicability_bins: pd.DataFrame,
    cell_line_summary: pd.DataFrame,
    interval_calibration: pd.DataFrame,
    conformal_interval_calibration: pd.DataFrame,
    conformal_subgroups: pd.DataFrame,
    summary: dict[str, Any],
    calibration_summary: dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    uncertainty_df.to_csv(output_dir / "ccle_predictions_with_uncertainty.tsv", sep="\t", index=False)
    calibrated_predictions_df.to_csv(output_dir / "ccle_predictions_with_calibrated_uncertainty.tsv", sep="\t", index=False)
    uncertainty_bins.to_csv(output_dir / "uncertainty_bin_metrics.tsv", sep="\t", index=False)
    applicability_bins.to_csv(output_dir / "applicability_bin_metrics.tsv", sep="\t", index=False)
    cell_line_summary.to_csv(output_dir / "cell_line_applicability_metrics.tsv", sep="\t", index=False)
    interval_calibration.to_csv(output_dir / "interval_calibration_metrics.tsv", sep="\t", index=False)
    conformal_interval_calibration.to_csv(output_dir / "conformal_interval_calibration_metrics.tsv", sep="\t", index=False)
    conformal_subgroups.to_csv(output_dir / "conformal_subgroup_interval_metrics.tsv", sep="\t", index=False)
    (output_dir / "uncertainty_applicability_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    (output_dir / "uncertainty_calibration_summary.json").write_text(
        json.dumps(calibration_summary, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    require_runtime_dependencies()
    config = load_json(args.config.resolve())
    paths = resolve_benchmark_paths(config)
    output_dir = resolve_output_dir(args, paths)
    tissue_vocabulary_path = args.tissue_vocabulary.resolve()

    require_existing(paths.gdsc_response_path, "GDSC response file")
    require_existing(paths.ccle_vector_path, "CCLE omics matrix")
    require_existing(paths.artifact_manifest_path, "artifact manifest")
    require_existing(tissue_vocabulary_path, "tissue vocabulary")

    artifact_paths = resolve_manifest_artifacts(paths.artifact_manifest_path)
    for label, path in artifact_paths.items():
        require_existing(path, f"artifact {label}")

    gdsc_response_df = pd.read_csv(paths.gdsc_response_path, sep="\t")
    ccle_vector_df = pd.read_csv(paths.ccle_vector_path, sep="\t")
    gdsc_omics_df = pd.read_csv(artifact_paths["omics_matrix"], sep="\t")
    ccle_response_df, response_metadata = load_or_reconstruct_ccle_response(
        paths,
        gdsc_response_df,
        ccle_vector_df,
        target_column=config["target_column"],
        raw_target_column=config["raw_target_column"],
    )
    merged_ccle_df, benchmark_df = build_test_matrix(
        ccle_vector_df,
        ccle_response_df,
        target_column=config["target_column"],
    )

    feature_matrix = benchmark_df.drop([config["target_column"]], axis=1).to_numpy(dtype=np.float32)
    labels = benchmark_df[config["target_column"]].to_numpy(dtype=np.float32)
    model = joblib.load(artifact_paths["trained_model"])
    predictions = model.predict(feature_matrix)
    estimator_predictions = collect_tree_predictions(model, feature_matrix)
    prediction_std = estimator_predictions.std(axis=0, ddof=1)
    lower_90 = np.quantile(estimator_predictions, 0.05, axis=0)
    upper_90 = np.quantile(estimator_predictions, 0.95, axis=0)

    nearest_similarity = nearest_train_cosine_similarity(gdsc_omics_df, ccle_vector_df)
    uncertainty_df = merged_ccle_df[["CELL_LINE_NAME", "DRUG_NAME"]].copy()
    uncertainty_df["pIC50_True"] = labels
    uncertainty_df["pIC50_Pred"] = predictions
    uncertainty_df["prediction_std"] = prediction_std
    uncertainty_df["prediction_interval_low_90"] = lower_90
    uncertainty_df["prediction_interval_high_90"] = upper_90
    uncertainty_df["signed_error"] = uncertainty_df["pIC50_Pred"] - uncertainty_df["pIC50_True"]
    uncertainty_df["absolute_error"] = uncertainty_df["signed_error"].abs()
    uncertainty_df["squared_error"] = uncertainty_df["signed_error"] ** 2
    uncertainty_df["within_tree_interval_90"] = (
        (uncertainty_df["pIC50_True"] >= uncertainty_df["prediction_interval_low_90"])
        & (uncertainty_df["pIC50_True"] <= uncertainty_df["prediction_interval_high_90"])
    ).astype(float)
    uncertainty_df["nearest_train_cosine"] = uncertainty_df["CELL_LINE_NAME"].map(nearest_similarity)

    calibration_merged_df, calibration_df, calibration_metadata = build_calibration_reference_split(
        gdsc_response_df,
        gdsc_omics_df,
        target_column=config["target_column"],
    )
    conformal_scores, oob_metadata = compute_oob_scaled_conformal_scores(
        model,
        gdsc_response_df,
        gdsc_omics_df,
        calibration_merged_df,
        calibration_df,
        target_column=config["target_column"],
    )
    calibration_metadata.update({"score_method": "oob_tree_std_scaled_absolute_residual", **oob_metadata})
    conformal_interval_calibration = summarize_conformal_interval_calibration(
        labels,
        predictions,
        estimator_predictions,
        conformal_scores,
        np.maximum(prediction_std, 1e-6),
    )
    conformal_quantile_90 = float(
        conformal_interval_calibration.loc[
            conformal_interval_calibration["nominal_coverage"] == DEFAULT_CONFORMAL_LEVEL,
            "conformal_quantile",
        ].iloc[0]
    )

    uncertainty_bins = summarize_uncertainty_bins(uncertainty_df)
    applicability_bins = summarize_applicability_bins(uncertainty_df)
    cell_line_summary = summarize_cell_line_applicability(uncertainty_df)
    interval_calibration = summarize_interval_calibration(estimator_predictions, labels)
    posthoc_calibration = posthoc_interval_inflation(labels, lower_90, upper_90)
    calibrated_predictions_df = build_calibrated_prediction_table(
        uncertainty_df,
        conformal_quantile_90,
        interval_scale_column="prediction_std",
    )
    calibrated_predictions_df = attach_metadata_and_tissues(
        calibrated_predictions_df,
        artifact_paths["cell_line_metadata"],
        tissue_vocabulary_path,
    )
    conformal_subgroups = summarize_conformal_subgroups(calibrated_predictions_df)
    summary = build_summary(
        uncertainty_df,
        uncertainty_bins,
        applicability_bins,
        cell_line_summary,
        interval_calibration,
        conformal_interval_calibration,
        posthoc_calibration,
        calibration_metadata,
        response_metadata,
        artifact_paths,
    )
    calibration_summary = build_calibration_summary(
        conformal_interval_calibration,
        conformal_subgroups,
        calibration_metadata,
    )
    write_outputs(
        output_dir,
        uncertainty_df,
        calibrated_predictions_df,
        uncertainty_bins,
        applicability_bins,
        cell_line_summary,
        interval_calibration,
        conformal_interval_calibration,
        conformal_subgroups,
        summary,
        calibration_summary,
    )

    print("summary:")
    print(f"output_dir: {output_dir}")
    print(f"rows: {len(uncertainty_df)}")
    print(f"mean_prediction_std: {summary['global']['mean_prediction_std']:.4f}")
    print(f"tree_interval_90_coverage: {summary['global']['tree_interval_90_coverage']:.4f}")
    print(f"tree_interval_90_coverage_gap: {summary['global']['tree_interval_90_coverage_gap']:.4f}")
    print(f"conformal_interval_90_coverage: {summary['global']['conformal_interval_90_coverage']:.4f}")
    print(f"conformal_interval_90_coverage_gap: {summary['global']['conformal_interval_90_coverage_gap']:.4f}")
    print(
        "uncertainty_vs_absolute_error_pearson: "
        f"{summary['global']['uncertainty_vs_absolute_error_pearson']}"
    )


if __name__ == "__main__":
    main()
