from __future__ import annotations

import argparse
import ast
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from ._common import REPO_ROOT, normalize_token, resolve_output_dir
except ImportError:
    from _common import REPO_ROOT, normalize_token, resolve_output_dir


DEFAULT_BENCHMARK_DIR = REPO_ROOT / "models" / "evaluation" / "legacy_pic50_baseline"
DEFAULT_COMPOUND_TABLE = Path(
    "/home/umut/projects/pharmacoprofiler_legacy/Merged_all_platforms_compound_file_drug_target_update_v8.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Annotate the canonical legacy benchmark with mechanism-aware compound metadata."
    )
    parser.add_argument(
        "--benchmark-dir",
        type=Path,
        default=DEFAULT_BENCHMARK_DIR,
        help="Directory containing benchmark outputs such as drug_metrics.tsv.",
    )
    parser.add_argument(
        "--compound-table",
        type=Path,
        default=DEFAULT_COMPOUND_TABLE,
        help="Merged compound-target annotation table from the legacy workspace.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory override.",
    )
    return parser.parse_args()


def parse_targets(value: Any) -> list[str]:
    if value is None or pd.isna(value):
        return []
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return []
    try:
        parsed = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        regex_matches = re.findall(r"'([^']+?)(?: \(Pchembl_value=[^']*)?'", text)
        parsed = regex_matches if regex_matches else [text]
    if isinstance(parsed, list):
        entries = [str(entry) for entry in parsed if str(entry).strip()]
    else:
        entries = [str(parsed)]
    cleaned = []
    for entry in entries:
        target_name = entry.split(" (Pchembl_value=")[0].strip().strip("[]'\"")
        if target_name:
            cleaned.append(target_name)
    return cleaned


def categorize_target_count(target_count: int) -> str:
    if target_count == 0:
        return "none"
    if target_count == 1:
        return "single"
    if target_count <= 5:
        return "few"
    if target_count <= 20:
        return "moderate"
    return "broad"


def prepare_compound_annotations(compound_table: pd.DataFrame) -> pd.DataFrame:
    df = compound_table.copy()
    df["COMPOUND_NAME"] = df["COMPOUND_NAME"].astype(str)
    df["PREFERRED_COMPOUND_NAME"] = df["PREFERRED_COMPOUND_NAME"].fillna("").astype(str)
    df["compound_name_key"] = df["COMPOUND_NAME"].map(normalize_token)
    df["preferred_name_key"] = df["PREFERRED_COMPOUND_NAME"].map(normalize_token)
    df["parsed_targets"] = df["TARGETS"].map(parse_targets)
    df["target_count"] = df["parsed_targets"].map(len)
    df["primary_target"] = df["parsed_targets"].map(lambda values: values[0] if values else "")
    df["target_preview"] = df["parsed_targets"].map(lambda values: " | ".join(values[:3]))
    df["compound_class_clean"] = (
        df["COMPOUND_CLASS"].fillna("").astype(str).str.strip().replace({"": "Unclassified"})
    )
    return df


def select_best_match(matches: pd.DataFrame) -> pd.Series:
    ranked = matches.assign(
        has_targets=matches["target_count"] > 0,
        has_preferred=matches["PREFERRED_COMPOUND_NAME"].astype(str).str.strip() != "",
    ).sort_values(
        ["has_targets", "target_count", "has_preferred"],
        ascending=[False, False, False],
    )
    return ranked.iloc[0]


def annotate_benchmark_drugs(drug_metrics: pd.DataFrame, compound_table: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    annotated_rows = []
    unmatched = []

    for row in drug_metrics.itertuples(index=False):
        drug_name = str(row.DRUG_NAME)
        drug_key = normalize_token(drug_name)
        exact_matches = compound_table[
            (compound_table["compound_name_key"] == drug_key) | (compound_table["preferred_name_key"] == drug_key)
        ]
        if exact_matches.empty:
            unmatched.append(drug_name)
            annotated_rows.append(
                {
                    **row._asdict(),
                    "match_status": "unmatched",
                    "match_column": "",
                    "compound_name": "",
                    "preferred_name": "",
                    "compound_class": "Unmatched",
                    "target_count": 0,
                    "target_count_bucket": "none",
                    "primary_target": "",
                    "target_preview": "",
                }
            )
            continue

        best_match = select_best_match(exact_matches)
        match_column = "COMPOUND_NAME" if best_match["compound_name_key"] == drug_key else "PREFERRED_COMPOUND_NAME"
        annotated_rows.append(
            {
                **row._asdict(),
                "match_status": "matched",
                "match_column": match_column,
                "compound_name": best_match["COMPOUND_NAME"],
                "preferred_name": best_match["PREFERRED_COMPOUND_NAME"],
                "compound_class": best_match["compound_class_clean"],
                "target_count": int(best_match["target_count"]),
                "target_count_bucket": categorize_target_count(int(best_match["target_count"])),
                "primary_target": best_match["primary_target"],
                "target_preview": best_match["target_preview"],
            }
        )

    annotated_df = pd.DataFrame(annotated_rows)
    return annotated_df, unmatched


def summarize_mechanism_classes(annotated_df: pd.DataFrame) -> pd.DataFrame:
    mapped = annotated_df[annotated_df["match_status"] == "matched"].copy()
    summary = (
        mapped.groupby("compound_class", dropna=False)
        .agg(
            n_drugs=("DRUG_NAME", "size"),
            mean_mae=("mae", "mean"),
            mean_signed_error=("mean_signed_error", "mean"),
            mean_pearson=("pearson_r", "mean"),
            median_target_count=("target_count", "median"),
        )
        .reset_index()
        .sort_values(["mean_mae", "n_drugs"], ascending=[False, False])
    )
    return summary


def build_summary(
    annotated_df: pd.DataFrame,
    class_metrics: pd.DataFrame,
    unmatched: list[str],
    compound_table_path: Path,
) -> dict[str, Any]:
    mapped = annotated_df[annotated_df["match_status"] == "matched"].copy()
    worst_row = mapped.sort_values("mae", ascending=False).iloc[0].to_dict()
    broadest_row = mapped.sort_values("target_count", ascending=False).iloc[0].to_dict()
    return {
        "analysis_name": "legacy_pic50_mechanism_annotations",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "compound_table_path": str(compound_table_path),
        "mapped_benchmark_drugs": int(len(mapped)),
        "total_benchmark_drugs": int(len(annotated_df)),
        "unmatched_benchmark_drugs": unmatched,
        "class_counts": class_metrics[["compound_class", "n_drugs"]].to_dict(orient="records"),
        "worst_mae_drug": {
            "drug_name": worst_row["DRUG_NAME"],
            "mae": float(worst_row["mae"]),
            "compound_class": worst_row["compound_class"],
            "target_count": int(worst_row["target_count"]),
            "target_preview": worst_row["target_preview"],
        },
        "broadest_target_drug": {
            "drug_name": broadest_row["DRUG_NAME"],
            "target_count": int(broadest_row["target_count"]),
            "compound_class": broadest_row["compound_class"],
            "mae": float(broadest_row["mae"]),
        },
    }


def main() -> None:
    args = parse_args()
    benchmark_dir = args.benchmark_dir.resolve()
    output_dir = resolve_output_dir(DEFAULT_BENCHMARK_DIR, str(args.output_dir.resolve())) if args.output_dir else resolve_output_dir(DEFAULT_BENCHMARK_DIR, os.environ.get("PHARMACOPROFILER_BENCHMARK_OUTPUT_DIR"))
    drug_metrics_path = benchmark_dir / "drug_metrics.tsv"
    if not drug_metrics_path.exists():
        raise FileNotFoundError(f"Missing benchmark drug metrics: {drug_metrics_path}")
    if not args.compound_table.exists():
        raise FileNotFoundError(f"Missing compound annotation table: {args.compound_table}")

    drug_metrics = pd.read_csv(drug_metrics_path, sep="\t")
    compound_table = pd.read_csv(
        args.compound_table,
        usecols=["COMPOUND_NAME", "PREFERRED_COMPOUND_NAME", "COMPOUND_CLASS", "TARGETS", "TARGETS_UNIPROT"],
    )
    prepared_compounds = prepare_compound_annotations(compound_table)
    annotated_df, unmatched = annotate_benchmark_drugs(drug_metrics, prepared_compounds)
    class_metrics = summarize_mechanism_classes(annotated_df)
    summary = build_summary(annotated_df, class_metrics, unmatched, args.compound_table.resolve())

    output_dir.mkdir(parents=True, exist_ok=True)
    annotated_df.to_csv(output_dir / "mechanism_annotated_drug_metrics.tsv", sep="\t", index=False)
    class_metrics.to_csv(output_dir / "mechanism_class_metrics.tsv", sep="\t", index=False)
    (output_dir / "mechanism_analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("summary:")
    print(f"output_dir: {output_dir}")
    print(f"mapped_benchmark_drugs: {summary['mapped_benchmark_drugs']}")
    print(f"unmatched_benchmark_drugs: {summary['unmatched_benchmark_drugs']}")
    print(f"worst_mae_drug: {summary['worst_mae_drug']}")


if __name__ == "__main__":
    main()
