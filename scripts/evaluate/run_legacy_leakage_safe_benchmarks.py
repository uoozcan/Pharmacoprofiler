from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from collections.abc import Iterable

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    RandomForestRegressor = None
    Ridge = None
    mean_absolute_error = None
    mean_squared_error = None
    r2_score = None

try:
    from ._common import REPO_ROOT, load_json, normalize_token, resolve_output_dir
except ImportError:
    from _common import REPO_ROOT, load_json, normalize_token, resolve_output_dir


DEFAULT_RUNNER_CONFIG = REPO_ROOT / "configs" / "models" / "legacy-pic50-leakage-safe-runner.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run leakage-safe GDSC benchmark regimes using the saved split registry."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_RUNNER_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument(
        "--models",
        type=str,
        default=None,
        help="Comma-separated subset of models to run. Defaults to config list.",
    )
    parser.add_argument(
        "--regimes",
        type=str,
        default=None,
        help="Comma-separated subset of regimes to run. Defaults to all saved regimes.",
    )
    return parser.parse_args()


def load_inputs(config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    legacy_root = Path(config["legacy_root"]).resolve()
    gdsc_df = pd.read_csv((legacy_root / config["gdsc_response_path"]).resolve(), sep="\t")
    omics_df = pd.read_csv((legacy_root / config["gdsc_omics_path"]).resolve(), sep="\t")
    split_df = pd.read_csv((REPO_ROOT / config["split_registry_path"]).resolve(), sep="\t")
    return gdsc_df, omics_df, split_df


def build_feature_frame(
    gdsc_df: pd.DataFrame,
    split_df: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    work_df = gdsc_df.copy()
    work_df["source_row_id"] = work_df.index.astype(int)
    work_df[config["drug_column"]] = work_df[config["drug_column"]].map(normalize_token)
    work_df[config["cell_line_column"]] = work_df[config["cell_line_column"]].map(normalize_token)
    merged = work_df.merge(split_df, on="source_row_id", suffixes=("", "_split"), how="inner")
    fingerprint_lengths = merged["FINGERPRINT"].astype(str).str.len()
    merged = merged.loc[fingerprint_lengths == 1024].copy()
    return merged[
        [
            "source_row_id",
            config["drug_column"],
            config["cell_line_column"],
            config["target_column"],
            "pair_random_fold",
            "compound_holdout_fold",
            "cell_line_holdout_fold",
            "double_cold_start_fold",
            "FINGERPRINT",
        ]
    ].rename(
        columns={
            config["drug_column"]: "DRUG_NAME_edited",
            config["cell_line_column"]: "CELL_LINE_NAME_edited",
            config["target_column"]: "pIC50",
        }
    )


def prepare_feature_assets(
    feature_df: pd.DataFrame,
    omics_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    omics_work = omics_df.copy()
    omics_work["CELL_LINE_NAME"] = omics_work["CELL_LINE_NAME"].map(normalize_token)
    omics_lookup = {
        str(cell_line): row.to_numpy(dtype=np.float32, copy=True)
        for cell_line, row in omics_work.set_index("CELL_LINE_NAME").iterrows()
    }
    fingerprint_lookup: dict[str, np.ndarray] = {}
    valid_rows = []
    missing_cell_lines = 0
    for row in feature_df.itertuples(index=False):
        cell_line = str(row.CELL_LINE_NAME_edited)
        if cell_line not in omics_lookup:
            missing_cell_lines += 1
            continue
        drug_name = str(row.DRUG_NAME_edited)
        if drug_name not in fingerprint_lookup:
            fingerprint_lookup[drug_name] = np.fromiter(
                (int(bit) for bit in str(row.FINGERPRINT)),
                dtype=np.float32,
                count=1024,
            )
        valid_rows.append(
            {
                "source_row_id": int(row.source_row_id),
                "DRUG_NAME_edited": drug_name,
                "CELL_LINE_NAME_edited": cell_line,
                "pIC50": float(row.pIC50),
                "pair_random_fold": int(row.pair_random_fold),
                "compound_holdout_fold": int(row.compound_holdout_fold),
                "cell_line_holdout_fold": int(row.cell_line_holdout_fold),
                "double_cold_start_fold": int(row.double_cold_start_fold),
            }
        )
    if missing_cell_lines:
        print(f"warning: skipped {missing_cell_lines} rows with missing omics vectors")
    return pd.DataFrame(valid_rows), omics_lookup, fingerprint_lookup


def get_model(model_name: str) -> Any:
    if RandomForestRegressor is None or Ridge is None:
        raise RuntimeError("scikit-learn is required to run leakage-safe benchmark regimes.")
    if model_name == "legacy_rf":
        return RandomForestRegressor(max_depth=81, n_estimators=100, random_state=2, n_jobs=3)
    if model_name == "ridge":
        return Ridge(alpha=1.0, solver="lsqr", random_state=2)
    raise ValueError(f"Unsupported model: {model_name}")


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    if mean_absolute_error is None or mean_squared_error is None or r2_score is None:
        raise RuntimeError("scikit-learn is required to compute leakage-safe benchmark metrics.")
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred, squared=False)),
        "mse": float(mean_squared_error(y_true, y_pred)),
        "pearson_r": float(pearsonr(y_true, y_pred)[0]) if len(np.unique(y_true)) > 1 and len(np.unique(y_pred)) > 1 else float("nan"),
        "spearman_r": float(spearmanr(y_true, y_pred)[0]) if len(np.unique(y_true)) > 1 and len(np.unique(y_pred)) > 1 else float("nan"),
        "r_squared": float(r2_score(y_true, y_pred)),
    }


def iter_index_chunks(index_array: np.ndarray, chunk_size: int) -> Iterable[np.ndarray]:
    for start in range(0, len(index_array), chunk_size):
        yield index_array[start : start + chunk_size]


def assemble_feature_chunk(
    rows: pd.DataFrame,
    omics_lookup: dict[str, np.ndarray],
    fingerprint_lookup: dict[str, np.ndarray],
) -> np.ndarray:
    omics_part = np.vstack([omics_lookup[cell_line] for cell_line in rows["CELL_LINE_NAME_edited"]]).astype(np.float32, copy=False)
    fingerprint_part = np.vstack([fingerprint_lookup[drug_name] for drug_name in rows["DRUG_NAME_edited"]]).astype(np.float32, copy=False)
    return np.hstack([omics_part, fingerprint_part])


def materialize_feature_memmap(
    rows: pd.DataFrame,
    omics_lookup: dict[str, np.ndarray],
    fingerprint_lookup: dict[str, np.ndarray],
    destination: Path,
    chunk_size: int = 2048,
) -> np.memmap:
    n_features = len(next(iter(omics_lookup.values()))) + len(next(iter(fingerprint_lookup.values())))
    matrix = np.memmap(destination, dtype=np.float32, mode="w+", shape=(len(rows), n_features))
    for start in range(0, len(rows), chunk_size):
        stop = min(start + chunk_size, len(rows))
        chunk_rows = rows.iloc[start:stop]
        matrix[start:stop, :] = assemble_feature_chunk(chunk_rows, omics_lookup, fingerprint_lookup)
    matrix.flush()
    return matrix


def fit_predict_chunked_ridge(
    feature_df: pd.DataFrame,
    train_index: np.ndarray,
    test_index: np.ndarray,
    omics_lookup: dict[str, np.ndarray],
    fingerprint_lookup: dict[str, np.ndarray],
    alpha: float = 1.0,
    chunk_size: int = 2048,
) -> np.ndarray:
    n_features = len(next(iter(omics_lookup.values()))) + len(next(iter(fingerprint_lookup.values())))
    xtx = np.zeros((n_features, n_features), dtype=np.float64)
    xty = np.zeros(n_features, dtype=np.float64)
    sum_x = np.zeros(n_features, dtype=np.float64)
    sum_y = 0.0
    train_count = 0

    for chunk_index in iter_index_chunks(train_index, chunk_size):
        chunk_rows = feature_df.iloc[chunk_index]
        chunk_x = assemble_feature_chunk(chunk_rows, omics_lookup, fingerprint_lookup).astype(np.float64, copy=False)
        chunk_y = chunk_rows["pIC50"].to_numpy(dtype=np.float64, copy=False)
        xtx += chunk_x.T @ chunk_x
        xty += chunk_x.T @ chunk_y
        sum_x += chunk_x.sum(axis=0)
        sum_y += float(chunk_y.sum())
        train_count += len(chunk_y)

    system_matrix = np.zeros((n_features + 1, n_features + 1), dtype=np.float64)
    system_matrix[:n_features, :n_features] = xtx
    system_matrix[np.diag_indices(n_features)] += alpha
    system_matrix[:n_features, n_features] = sum_x
    system_matrix[n_features, :n_features] = sum_x
    system_matrix[n_features, n_features] = float(train_count)
    system_rhs = np.zeros(n_features + 1, dtype=np.float64)
    system_rhs[:n_features] = xty
    system_rhs[n_features] = sum_y
    solution = np.linalg.solve(system_matrix, system_rhs)
    coefficients = solution[:n_features]
    intercept = float(solution[n_features])

    prediction_chunks = []
    for chunk_index in iter_index_chunks(test_index, chunk_size):
        chunk_rows = feature_df.iloc[chunk_index]
        chunk_x = assemble_feature_chunk(chunk_rows, omics_lookup, fingerprint_lookup).astype(np.float64, copy=False)
        prediction_chunks.append(chunk_x @ coefficients + intercept)
    if not prediction_chunks:
        return np.array([], dtype=np.float64)
    return np.concatenate(prediction_chunks)


def fit_predict_chunked_ols(
    feature_df: pd.DataFrame,
    train_index: np.ndarray,
    test_index: np.ndarray,
    omics_lookup: dict[str, np.ndarray],
    fingerprint_lookup: dict[str, np.ndarray],
    chunk_size: int = 2048,
) -> np.ndarray:
    n_features = len(next(iter(omics_lookup.values()))) + len(next(iter(fingerprint_lookup.values())))
    xtx = np.zeros((n_features, n_features), dtype=np.float64)
    xty = np.zeros(n_features, dtype=np.float64)
    sum_x = np.zeros(n_features, dtype=np.float64)
    sum_y = 0.0
    train_count = 0

    for chunk_index in iter_index_chunks(train_index, chunk_size):
        chunk_rows = feature_df.iloc[chunk_index]
        chunk_x = assemble_feature_chunk(chunk_rows, omics_lookup, fingerprint_lookup).astype(np.float64, copy=False)
        chunk_y = chunk_rows["pIC50"].to_numpy(dtype=np.float64, copy=False)
        xtx += chunk_x.T @ chunk_x
        xty += chunk_x.T @ chunk_y
        sum_x += chunk_x.sum(axis=0)
        sum_y += float(chunk_y.sum())
        train_count += len(chunk_y)

    system_matrix = np.zeros((n_features + 1, n_features + 1), dtype=np.float64)
    system_matrix[:n_features, :n_features] = xtx
    system_matrix[:n_features, n_features] = sum_x
    system_matrix[n_features, :n_features] = sum_x
    system_matrix[n_features, n_features] = float(train_count)
    system_rhs = np.zeros(n_features + 1, dtype=np.float64)
    system_rhs[:n_features] = xty
    system_rhs[n_features] = sum_y
    solution = np.linalg.lstsq(system_matrix, system_rhs, rcond=None)[0]
    coefficients = solution[:n_features]
    intercept = float(solution[n_features])

    prediction_chunks = []
    for chunk_index in iter_index_chunks(test_index, chunk_size):
        chunk_rows = feature_df.iloc[chunk_index]
        chunk_x = assemble_feature_chunk(chunk_rows, omics_lookup, fingerprint_lookup).astype(np.float64, copy=False)
        prediction_chunks.append(chunk_x @ coefficients + intercept)
    if not prediction_chunks:
        return np.array([], dtype=np.float64)
    return np.concatenate(prediction_chunks)


def fold_masks(df: pd.DataFrame, regime_name: str, fold: int) -> tuple[pd.Series, pd.Series]:
    if regime_name == "pair_random":
        test_mask = df["pair_random_fold"] == fold
        train_mask = ~test_mask
        return train_mask, test_mask
    if regime_name == "compound_holdout":
        test_mask = df["compound_holdout_fold"] == fold
        train_mask = ~test_mask
        return train_mask, test_mask
    if regime_name == "cell_line_holdout":
        test_mask = df["cell_line_holdout_fold"] == fold
        train_mask = ~test_mask
        return train_mask, test_mask
    if regime_name == "double_cold_start":
        test_mask = (df["compound_holdout_fold"] == fold) & (df["cell_line_holdout_fold"] == fold)
        train_mask = (df["compound_holdout_fold"] != fold) & (df["cell_line_holdout_fold"] != fold)
        return train_mask, test_mask
    raise ValueError(f"Unsupported regime: {regime_name}")


def run_regime(
    feature_df: pd.DataFrame,
    regime_name: str,
    folds: list[int],
    model_names: list[str],
    omics_lookup: dict[str, np.ndarray],
    fingerprint_lookup: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fold_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []

    for fold in folds:
        train_mask, test_mask = fold_masks(feature_df, regime_name, fold)
        if int(test_mask.sum()) == 0:
            continue
        train_index = np.flatnonzero(train_mask.to_numpy())
        test_index = np.flatnonzero(test_mask.to_numpy())
        y_test = feature_df.iloc[test_index]["pIC50"].to_numpy(dtype=np.float32)
        test_rows = feature_df.iloc[test_index].reset_index(drop=True)

        for model_name in model_names:
            if model_name == "ridge":
                predictions = fit_predict_chunked_ridge(
                    feature_df,
                    train_index,
                    test_index,
                    omics_lookup,
                    fingerprint_lookup,
                )
                train_rows = int(len(train_index))
            elif model_name == "ols":
                predictions = fit_predict_chunked_ols(
                    feature_df,
                    train_index,
                    test_index,
                    omics_lookup,
                    fingerprint_lookup,
                )
                train_rows = int(len(train_index))
            else:
                model = get_model(model_name)
                train_rows_df = feature_df.iloc[train_index]
                test_rows_df = feature_df.iloc[test_index]
                with tempfile.TemporaryDirectory(prefix="pharmacoprofiler-rf-", dir="/tmp") as temp_dir:
                    temp_root = Path(temp_dir)
                    x_train = materialize_feature_memmap(
                        train_rows_df,
                        omics_lookup,
                        fingerprint_lookup,
                        temp_root / "x_train.dat",
                    )
                    x_test = materialize_feature_memmap(
                        test_rows_df,
                        omics_lookup,
                        fingerprint_lookup,
                        temp_root / "x_test.dat",
                    )
                    y_train = train_rows_df["pIC50"].to_numpy(dtype=np.float32)
                    model.fit(x_train, y_train)
                    predictions = model.predict(x_test)
                    train_rows = int(len(y_train))
            metrics = compute_metrics(y_test, predictions)
            fold_rows.append(
                {
                    "regime_name": regime_name,
                    "fold": fold,
                    "model_name": model_name,
                    "train_rows": train_rows,
                    "test_rows": int(len(y_test)),
                    "test_drugs": int(test_rows["DRUG_NAME_edited"].nunique()),
                    "test_cell_lines": int(test_rows["CELL_LINE_NAME_edited"].nunique()),
                    **metrics,
                }
            )
            for idx, pred in enumerate(predictions):
                prediction_rows.append(
                    {
                        "regime_name": regime_name,
                        "fold": fold,
                        "model_name": model_name,
                        "source_row_id": int(test_rows.loc[idx, "source_row_id"]),
                        "DRUG_NAME_edited": test_rows.loc[idx, "DRUG_NAME_edited"],
                        "CELL_LINE_NAME_edited": test_rows.loc[idx, "CELL_LINE_NAME_edited"],
                        "pIC50_true": float(y_test[idx]),
                        "pIC50_pred": float(pred),
                    }
                )
    return pd.DataFrame(fold_rows), pd.DataFrame(prediction_rows)


def summarize_regime_metrics(fold_metrics: pd.DataFrame) -> pd.DataFrame:
    summary = (
        fold_metrics.groupby(["regime_name", "model_name"])
        .agg(
            folds=("fold", "nunique"),
            mean_mae=("mae", "mean"),
            mean_rmse=("rmse", "mean"),
            mean_pearson_r=("pearson_r", "mean"),
            mean_spearman_r=("spearman_r", "mean"),
            mean_r_squared=("r_squared", "mean"),
            total_test_rows=("test_rows", "sum"),
        )
        .reset_index()
        .sort_values(["regime_name", "mean_mae"])
    )
    return summary


def write_dataframe_atomic(df: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_suffix(destination.suffix + ".tmp")
    df.to_csv(temp_path, sep="\t", index=False)
    shutil.move(temp_path, destination)


def write_text_atomic(text: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_suffix(destination.suffix + ".tmp")
    temp_path.write_text(text, encoding="utf-8")
    shutil.move(temp_path, destination)


def write_outputs(
    output_dir: Path,
    config: dict[str, Any],
    model_names: list[str],
    feature_df: pd.DataFrame,
    fold_metrics_df: pd.DataFrame,
    prediction_df: pd.DataFrame,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_dataframe_atomic(fold_metrics_df, output_dir / "fold_metrics.tsv")

    if fold_metrics_df.empty:
        regime_summary_df = pd.DataFrame(
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
    else:
        regime_summary_df = summarize_regime_metrics(fold_metrics_df)
    write_dataframe_atomic(regime_summary_df, output_dir / "regime_summary.tsv")

    summary = {
        "runner_name": config["runner_name"],
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "models": model_names,
        "rows_used": int(len(feature_df)),
        "regimes": regime_summary_df.to_dict(orient="records"),
    }
    write_text_atomic(json.dumps(summary, indent=2), output_dir / "regime_benchmark_summary.json")
    write_dataframe_atomic(prediction_df, output_dir / "regime_predictions.tsv")


def main() -> None:
    args = parse_args()
    config = load_json(args.config.resolve())
    output_dir = resolve_output_dir(
        (REPO_ROOT / config["output_dir"]).resolve(),
        str(args.output_dir.resolve()) if args.output_dir else os.environ.get("PHARMACOPROFILER_BENCHMARK_OUTPUT_DIR"),
    )
    model_names = [name.strip() for name in args.models.split(",")] if args.models else list(config["models"])
    gdsc_df, omics_df, split_df = load_inputs(config)
    raw_feature_df = build_feature_frame(gdsc_df, split_df, config)
    feature_df, omics_lookup, fingerprint_lookup = prepare_feature_assets(raw_feature_df, omics_df)

    regimes = {
        "pair_random": list(range(5)),
        "compound_holdout": list(range(5)),
        "cell_line_holdout": list(range(5)),
        "double_cold_start": list(range(5)),
    }
    if args.regimes:
        requested_regimes = [name.strip() for name in args.regimes.split(",") if name.strip()]
        regimes = {name: regimes[name] for name in requested_regimes}

    all_fold_metrics = []
    all_predictions = []
    for regime_name, folds in regimes.items():
        print(f"running regime: {regime_name} | folds={len(folds)} | models={','.join(model_names)}")
        fold_metrics, prediction_rows = run_regime(
            feature_df,
            regime_name,
            folds,
            model_names,
            omics_lookup,
            fingerprint_lookup,
        )
        all_fold_metrics.append(fold_metrics)
        all_predictions.append(prediction_rows)
        fold_metrics_df = pd.concat(all_fold_metrics, ignore_index=True)
        prediction_df = pd.concat(all_predictions, ignore_index=True)
        write_outputs(output_dir, config, model_names, feature_df, fold_metrics_df, prediction_df)
        print(
            "completed regime: "
            f"{regime_name} | fold_rows={len(fold_metrics)} | prediction_rows={len(prediction_rows)}"
        )

    fold_metrics_df = pd.concat(all_fold_metrics, ignore_index=True)
    prediction_df = pd.concat(all_predictions, ignore_index=True)
    write_outputs(output_dir, config, model_names, feature_df, fold_metrics_df, prediction_df)
    regime_summary_df = summarize_regime_metrics(fold_metrics_df)

    print("summary:")
    print(f"output_dir: {output_dir}")
    print(f"rows_used: {len(feature_df)}")
    print(regime_summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
