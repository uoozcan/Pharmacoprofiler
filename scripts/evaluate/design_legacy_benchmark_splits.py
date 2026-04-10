from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from ._common import DEFAULT_CONFIG_PATH, REPO_ROOT, load_json, normalize_token, resolve_output_dir
except ImportError:
    from _common import DEFAULT_CONFIG_PATH, REPO_ROOT, load_json, normalize_token, resolve_output_dir


DEFAULT_DESIGN_CONFIG_PATH = REPO_ROOT / "configs" / "models" / "legacy-pic50-leakage-safe-benchmark-design.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Design deterministic split registries for stronger leakage-safe benchmarking of the legacy pIC50 model."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_DESIGN_CONFIG_PATH,
        help="Leakage-safe benchmark design config JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory override.",
    )
    return parser.parse_args()


def load_gdsc_response(config: dict[str, Any]) -> pd.DataFrame:
    legacy_root = Path(config["legacy_root"]).resolve()
    path = (legacy_root / config["gdsc_response_path"]).resolve()
    df = pd.read_csv(path, sep="\t")
    return df


def shuffled_round_robin(items: list[str], folds: int, seed: int) -> dict[str, int]:
    rng = random.Random(seed)
    values = sorted(set(items))
    rng.shuffle(values)
    return {value: index % folds for index, value in enumerate(values)}


def assign_pair_random_folds(df: pd.DataFrame, folds: int, seed: int) -> pd.Series:
    rng = random.Random(seed)
    indices = list(range(len(df)))
    rng.shuffle(indices)
    assignments = [0] * len(df)
    for fold_index, row_index in enumerate(indices):
        assignments[row_index] = fold_index % folds
    return pd.Series(assignments, index=df.index, name="pair_random_fold")


def summarize_fold_distribution(values: pd.Series, label: str) -> list[dict[str, Any]]:
    counts = values.value_counts().sort_index()
    return [
        {
            label: int(fold),
            "count": int(count),
        }
        for fold, count in counts.items()
    ]


def build_regime_summary(
    df: pd.DataFrame,
    regime_name: str,
    fold_column: str,
    leakproof_entity_column: str | None = None,
) -> dict[str, Any]:
    fold_counts = summarize_fold_distribution(df[fold_column], "fold")
    summary: dict[str, Any] = {
        "regime_name": regime_name,
        "fold_column": fold_column,
        "fold_counts": fold_counts,
        "rows": int(len(df)),
    }
    if leakproof_entity_column:
        grouped = df.groupby(fold_column)[leakproof_entity_column].nunique().sort_index()
        summary["unique_entity_counts"] = [
            {"fold": int(fold), "unique_entities": int(count)} for fold, count in grouped.items()
        ]
    return summary


def build_double_cold_start_summary(
    df: pd.DataFrame,
    drug_fold_column: str,
    cell_fold_column: str,
    folds: int,
) -> list[dict[str, Any]]:
    summaries = []
    for fold in range(folds):
        mask = (df[drug_fold_column] == fold) & (df[cell_fold_column] == fold)
        test_rows = df[mask]
        summaries.append(
            {
                "fold": fold,
                "test_rows": int(len(test_rows)),
                "test_drugs": int(test_rows["DRUG_NAME_edited"].nunique()),
                "test_cell_lines": int(test_rows["CELL_LINE_NAME_edited"].nunique()),
            }
        )
    return summaries


def main() -> None:
    args = parse_args()
    config = load_json(args.config.resolve())
    preferred_output = (REPO_ROOT / config["output_dir"]).resolve()
    output_dir = resolve_output_dir(preferred_output, str(args.output_dir.resolve()) if args.output_dir else None)

    df = load_gdsc_response(config).copy()
    drug_col = config["drug_column"]
    cell_col = config["cell_line_column"]
    target_col = config["target_column"]
    df[drug_col] = df[drug_col].map(normalize_token)
    df[cell_col] = df[cell_col].map(normalize_token)

    pair_random_fold = assign_pair_random_folds(df, config["pair_random_folds"], config["pair_random_seed"])
    compound_fold_map = shuffled_round_robin(df[drug_col].tolist(), config["compound_holdout_folds"], config["entity_random_seed"])
    cell_line_fold_map = shuffled_round_robin(
        df[cell_col].tolist(),
        config["cell_line_holdout_folds"],
        config["entity_random_seed"] + 1,
    )

    split_df = df[[drug_col, cell_col, target_col]].copy()
    split_df.insert(0, "source_row_id", df.index.astype(int))
    split_df["pair_random_fold"] = pair_random_fold
    split_df["compound_holdout_fold"] = df[drug_col].map(compound_fold_map)
    split_df["cell_line_holdout_fold"] = df[cell_col].map(cell_line_fold_map)
    split_df["double_cold_start_fold"] = (
        split_df["compound_holdout_fold"] == split_df["cell_line_holdout_fold"]
    ).astype(int) * split_df["compound_holdout_fold"] + (
        split_df["compound_holdout_fold"] != split_df["cell_line_holdout_fold"]
    ).astype(int) * -1

    output_dir.mkdir(parents=True, exist_ok=True)
    split_df.to_csv(output_dir / "gdsc_split_registry.tsv", sep="\t", index=False)

    design_summary = {
        "design_name": config["design_name"],
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_rows": int(len(df)),
        "source_drugs": int(df[drug_col].nunique()),
        "source_cell_lines": int(df[cell_col].nunique()),
        "target_column": target_col,
        "regimes": [
            build_regime_summary(split_df, "pair_random", "pair_random_fold"),
            build_regime_summary(split_df, "compound_holdout", "compound_holdout_fold", drug_col),
            build_regime_summary(split_df, "cell_line_holdout", "cell_line_holdout_fold", cell_col),
            {
                "regime_name": "double_cold_start",
                "fold_logic": "test rows where compound_holdout_fold == cell_line_holdout_fold == fold",
                "eligible_test_rows": int((split_df["double_cold_start_fold"] >= 0).sum()),
                "fold_summaries": build_double_cold_start_summary(
                    split_df,
                    "compound_holdout_fold",
                    "cell_line_holdout_fold",
                    config["double_cold_start_folds"],
                ),
            },
        ],
        "seeds": {
            "pair_random_seed": config["pair_random_seed"],
            "entity_random_seed": config["entity_random_seed"],
        },
    }
    (output_dir / "benchmark_split_design_summary.json").write_text(
        json.dumps(design_summary, indent=2),
        encoding="utf-8",
    )

    regime_rows = []
    regime_rows.extend(
        {
            "regime_name": "pair_random",
            "fold": row["fold"],
            "count": row["count"],
            "detail_type": "rows",
        }
        for row in summarize_fold_distribution(split_df["pair_random_fold"], "fold")
    )
    regime_rows.extend(
        {
            "regime_name": "compound_holdout",
            "fold": row["fold"],
            "count": row["count"],
            "detail_type": "rows",
        }
        for row in summarize_fold_distribution(split_df["compound_holdout_fold"], "fold")
    )
    regime_rows.extend(
        {
            "regime_name": "cell_line_holdout",
            "fold": row["fold"],
            "count": row["count"],
            "detail_type": "rows",
        }
        for row in summarize_fold_distribution(split_df["cell_line_holdout_fold"], "fold")
    )
    regime_rows.extend(
        {
            "regime_name": "double_cold_start",
            "fold": row["fold"],
            "count": row["test_rows"],
            "detail_type": "eligible_test_rows",
        }
        for row in design_summary["regimes"][3]["fold_summaries"]
    )
    pd.DataFrame(regime_rows).to_csv(output_dir / "benchmark_split_regime_counts.tsv", sep="\t", index=False)

    print("summary:")
    print(f"output_dir: {output_dir}")
    print(f"source_rows: {design_summary['source_rows']}")
    print(f"source_drugs: {design_summary['source_drugs']}")
    print(f"source_cell_lines: {design_summary['source_cell_lines']}")


if __name__ == "__main__":
    main()
