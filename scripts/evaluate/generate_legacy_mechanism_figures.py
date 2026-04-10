from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/pharmacoprofiler-matplotlib")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = REPO_ROOT / "models" / "evaluation" / "legacy_pic50_baseline"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "research" / "figures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate mechanism-aware benchmark figures.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.svg", bbox_inches="tight")


def generate_mechanism_overview_figure(annotated_df: pd.DataFrame, class_metrics: pd.DataFrame, output_dir: Path) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    mapped = annotated_df[annotated_df["match_status"] == "matched"].copy()
    mapped = mapped.sort_values("mae", ascending=True)

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    sns.barplot(data=mapped, x="mae", y="DRUG_NAME", hue="compound_class", dodge=False, ax=axes[0])
    axes[0].set_title("A. Drug-level benchmark error by mechanism class")
    axes[0].set_xlabel("MAE")
    axes[0].set_ylabel("Drug")
    axes[0].legend(loc="lower right", fontsize=10, title="Class")

    sns.scatterplot(
        data=mapped,
        x="target_count",
        y="mae",
        hue="compound_class",
        size="mean_signed_error",
        sizes=(50, 250),
        ax=axes[1],
    )
    axes[1].set_title("B. Polypharmacology context vs benchmark error")
    axes[1].set_xlabel("Annotated target count")
    axes[1].set_ylabel("MAE")

    class_plot = class_metrics.sort_values("mean_mae", ascending=True)
    sns.barplot(data=class_plot, x="mean_mae", y="compound_class", color="#2C7FB8", ax=axes[2])
    axes[2].set_title("C. Mean benchmark error by mechanism class")
    axes[2].set_xlabel("Mean MAE")
    axes[2].set_ylabel("Mechanism class")

    fig.suptitle("Mechanism-aware annotation of the preserved benchmark drugs", fontsize=20, y=1.03)
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_mechanism_overview")
    plt.close(fig)


def write_note(output_dir: Path, summary: dict) -> None:
    note = f"""# Mechanism Figure Set

## Included figures

- `legacy_benchmark_mechanism_overview.(png|svg)`: drug-level and class-level benchmark behavior viewed through mechanism annotations

## Figure-safe messages

- The mechanism-aware pass currently maps {summary['mapped_benchmark_drugs']} of {summary['total_benchmark_drugs']} benchmark drugs to the verified merged compound-target table.
- The worst benchmark MAE among mapped drugs is `{summary['worst_mae_drug']['drug_name']}` with class `{summary['worst_mae_drug']['compound_class']}`.
- Polypharmacology is visible in the benchmark overlap, but target breadth alone should not be presented as a causal explanation of performance.
- This analysis should be framed as a mechanism-aware annotation layer for interpretation and prioritization, not as proof of mechanistic validity.
"""
    (output_dir / "mechanism_figure_set_note.md").write_text(note, encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    annotated_df = pd.read_csv(input_dir / "mechanism_annotated_drug_metrics.tsv", sep="\t")
    class_metrics = pd.read_csv(input_dir / "mechanism_class_metrics.tsv", sep="\t")
    summary = json.loads((input_dir / "mechanism_analysis_summary.json").read_text(encoding="utf-8"))
    generate_mechanism_overview_figure(annotated_df, class_metrics, output_dir)
    write_note(output_dir, summary)
    print("summary:")
    print(f"generated: {output_dir / 'legacy_benchmark_mechanism_overview.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_mechanism_overview.svg'}")
    print(f"generated: {output_dir / 'mechanism_figure_set_note.md'}")


if __name__ == "__main__":
    main()
