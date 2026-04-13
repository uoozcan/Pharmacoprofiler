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
    parser = argparse.ArgumentParser(
        description="Generate uncertainty and applicability figures from legacy benchmark analysis outputs."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing uncertainty/applicability analysis outputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated figure assets.",
    )
    return parser.parse_args()


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.svg", bbox_inches="tight")


def generate_uncertainty_figure(
    predictions: pd.DataFrame,
    uncertainty_bins: pd.DataFrame,
    summary: dict,
    output_dir: Path,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    sample_df = predictions.sample(min(len(predictions), 2500), random_state=2)
    sns.scatterplot(
        data=sample_df,
        x="prediction_std",
        y="absolute_error",
        alpha=0.25,
        s=28,
        color="#1F78B4",
        edgecolor="none",
        ax=axes[0],
    )
    sns.regplot(
        data=sample_df,
        x="prediction_std",
        y="absolute_error",
        scatter=False,
        color="#D95F0E",
        line_kws={"linewidth": 2.5},
        ax=axes[0],
    )
    axes[0].set_title("A. Ensemble spread tracks larger benchmark error")
    axes[0].set_xlabel("Per-sample tree prediction SD")
    axes[0].set_ylabel("Absolute error")
    axes[0].text(
        0.03,
        0.97,
        (
            f"Pearson r = {summary['global']['uncertainty_vs_absolute_error_pearson']:.3f}\n"
            f"Mean SD = {summary['global']['mean_prediction_std']:.3f}"
        ),
        transform=axes[0].transAxes,
        va="top",
        ha="left",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.9, "edgecolor": "#cccccc"},
    )

    bin_df = uncertainty_bins.copy()
    sns.barplot(data=bin_df, x="uncertainty_bin", y="mae", color="#756BB1", ax=axes[1])
    axes[1].set_title("B. Higher uncertainty bins show worse error and weak coverage")
    axes[1].set_xlabel("Prediction uncertainty quintile")
    axes[1].set_ylabel("MAE")
    coverage_ax = axes[1].twinx()
    coverage_ax.plot(
        range(len(bin_df)),
        bin_df["interval_coverage_90"],
        color="#D95F0E",
        marker="o",
        linewidth=2.5,
    )
    coverage_ax.axhline(0.90, linestyle="--", color="#444444", linewidth=1.5)
    coverage_ax.set_ylabel("Empirical 90% interval coverage")
    coverage_ax.set_ylim(0.0, 1.05)

    fig.suptitle("Uncertainty behavior of the legacy Random Forest baseline", fontsize=18, y=1.03)
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_uncertainty")
    plt.close(fig)


def generate_applicability_figure(
    cell_line_metrics: pd.DataFrame,
    applicability_bins: pd.DataFrame,
    summary: dict,
    output_dir: Path,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    sample_df = cell_line_metrics.sample(min(len(cell_line_metrics), 250), random_state=2)
    sns.scatterplot(
        data=sample_df,
        x="nearest_train_cosine",
        y="mae",
        size="n",
        sizes=(30, 170),
        color="#238B45",
        alpha=0.75,
        ax=axes[0],
    )
    sns.regplot(
        data=sample_df,
        x="nearest_train_cosine",
        y="mae",
        scatter=False,
        color="#D95F0E",
        line_kws={"linewidth": 2.5},
        ax=axes[0],
    )
    axes[0].set_title("A. Cell lines farther from GDSC tend to have worse error")
    axes[0].set_xlabel("Nearest GDSC cell-line cosine similarity")
    axes[0].set_ylabel("Cell-line MAE")
    axes[0].text(
        0.03,
        0.97,
        f"Pearson r = {summary['global']['cell_line_similarity_vs_mae_pearson']:.3f}",
        transform=axes[0].transAxes,
        va="top",
        ha="left",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.9, "edgecolor": "#cccccc"},
    )

    bin_df = applicability_bins.copy()
    sns.barplot(data=bin_df, x="applicability_bin", y="mae", color="#2C7FB8", ax=axes[1])
    axes[1].set_title("B. Lower applicability bins carry higher error and uncertainty")
    axes[1].set_xlabel("Applicability quintile")
    axes[1].set_ylabel("MAE")
    uncertainty_ax = axes[1].twinx()
    uncertainty_ax.plot(
        range(len(bin_df)),
        bin_df["mean_prediction_std"],
        color="#B2182B",
        marker="o",
        linewidth=2.5,
    )
    uncertainty_ax.set_ylabel("Mean prediction SD")

    fig.suptitle("Applicability proxy from CCLE-to-GDSC cell-line similarity", fontsize=18, y=1.03)
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_applicability")
    plt.close(fig)


def generate_uncertainty_calibration_figure(
    calibration_metrics: pd.DataFrame,
    subgroup_metrics: pd.DataFrame,
    summary: dict,
    output_dir: Path,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    fig, axes = plt.subplots(1, 3, figsize=(22, 7))

    calibration_df = calibration_metrics.copy()
    sns.lineplot(
        data=calibration_df,
        x="nominal_coverage",
        y="raw_empirical_coverage",
        marker="o",
        linewidth=2.5,
        color="#B2182B",
        label="Raw tree interval",
        ax=axes[0],
    )
    sns.lineplot(
        data=calibration_df,
        x="nominal_coverage",
        y="conformal_empirical_coverage",
        marker="o",
        linewidth=2.5,
        color="#1F78B4",
        label="Split conformal",
        ax=axes[0],
    )
    axes[0].plot([0.5, 0.96], [0.5, 0.96], linestyle="--", color="#444444", linewidth=1.5)
    axes[0].set_title("A. Split conformal brings empirical coverage closer to nominal")
    axes[0].set_xlabel("Nominal central interval coverage")
    axes[0].set_ylabel("Empirical benchmark coverage")
    axes[0].set_xlim(0.48, 0.97)
    axes[0].set_ylim(0.45, 1.0)
    axes[0].legend(loc="lower right", frameon=True)

    width_df = calibration_df.melt(
        id_vars=["nominal_coverage"],
        value_vars=["raw_mean_interval_width", "conformal_mean_interval_width"],
        var_name="interval_type",
        value_name="mean_interval_width",
    )
    width_df["interval_type"] = width_df["interval_type"].map(
        {
            "raw_mean_interval_width": "Raw tree interval",
            "conformal_mean_interval_width": "Split conformal",
        }
    )
    sns.barplot(data=width_df, x="nominal_coverage", y="mean_interval_width", hue="interval_type", ax=axes[1])
    axes[1].set_title("B. Calibrated coverage trades off against wider intervals")
    axes[1].set_xlabel("Nominal central interval coverage")
    axes[1].set_ylabel("Mean interval width")
    axes[1].legend(loc="upper left", frameon=True)

    potency_df = subgroup_metrics[subgroup_metrics["subgroup_type"] == "potency_bin"].copy()
    potency_df = potency_df.melt(
        id_vars=["subgroup_label"],
        value_vars=["raw_interval_coverage_90", "conformal_interval_coverage_90"],
        var_name="interval_type",
        value_name="empirical_coverage",
    )
    potency_df["interval_type"] = potency_df["interval_type"].map(
        {
            "raw_interval_coverage_90": "Raw tree interval",
            "conformal_interval_coverage_90": "Split conformal",
        }
    )
    sns.barplot(data=potency_df, x="subgroup_label", y="empirical_coverage", hue="interval_type", ax=axes[2])
    axes[2].axhline(0.90, linestyle="--", color="#444444", linewidth=1.5)
    axes[2].set_title("C. Calibrated 90% coverage across potency bins")
    axes[2].set_xlabel("Observed pIC50 bin")
    axes[2].set_ylabel("Empirical 90% coverage")
    axes[2].set_ylim(0.0, 1.05)
    axes[2].legend(loc="lower right", frameon=True)

    posthoc = summary["posthoc_interval_calibration_90"]
    axes[2].text(
        0.03,
        0.97,
        (
            f"Raw 90% gap = {summary['global']['tree_interval_90_coverage_gap']:.3f}\n"
            f"Conformal 90% gap = {summary['global']['conformal_interval_90_coverage_gap']:.3f}\n"
            f"Post hoc inflation = {posthoc['inflation_factor']:.3f}"
        ),
        transform=axes[2].transAxes,
        va="top",
        ha="left",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.9, "edgecolor": "#cccccc"},
    )

    axes[1].text(
        0.03,
        0.97,
        (
            f"Calibration rows = {summary['calibration_reference']['selected_rows']}\n"
            f"Coverage target = {summary['conformal_interval_calibration_90']['nominal_coverage']:.2f}\n"
            f"Conformal q = {summary['conformal_interval_calibration_90']['conformal_quantile']:.3f}"
        ),
        transform=axes[1].transAxes,
        va="top",
        ha="left",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.9, "edgecolor": "#cccccc"},
    )

    fig.suptitle("Split-conformal interval calibration for the legacy Random Forest baseline", fontsize=18, y=1.03)
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_uncertainty_calibration")
    plt.close(fig)


def write_note(output_dir: Path, summary: dict) -> None:
    note = f"""# Uncertainty and Applicability Figure Set

## Included figures

- `legacy_benchmark_uncertainty.(png|svg)`: relationship between ensemble spread, error, and empirical interval behavior
- `legacy_benchmark_applicability.(png|svg)`: relationship between nearest-train cell-line similarity, benchmark error, and uncertainty
- `legacy_benchmark_uncertainty_calibration.(png|svg)`: raw-versus-conformal interval coverage, width tradeoff, and potency-bin calibration summary

## Figure-safe messages

- The preserved Random Forest baseline already exposes a usable uncertainty proxy through per-tree prediction spread.
- Higher ensemble spread is associated with larger absolute benchmark error, with Pearson `r = {summary['global']['uncertainty_vs_absolute_error_pearson']:.3f}`.
- The nominal 90% tree interval should be presented as an internal uncertainty heuristic rather than as a fully calibrated predictive interval.
- Split conformal on a deterministic GDSC calibration reference split improves 90% empirical coverage from `{summary['global']['tree_interval_90_coverage']:.3f}` to `{summary['global']['conformal_interval_90_coverage']:.3f}` on the reconstructed CCLE benchmark.
- Tree-quantile intervals under-cover across nominal coverage levels, with a 90% coverage gap of `{summary['global']['tree_interval_90_coverage_gap']:.3f}`, while the split-conformal 90% gap is `{summary['global']['conformal_interval_90_coverage_gap']:.3f}`.
- The post hoc 90% width inflation factor is `{summary['posthoc_interval_calibration_90']['inflation_factor']:.3f}`, which is descriptive of current miscalibration and not a deployment-ready calibration method.
- A simple applicability proxy based on nearest GDSC cell-line cosine similarity shows that CCLE cell lines farther from the GDSC training manifold tend to have worse benchmark error, with Pearson `r = {summary['global']['cell_line_similarity_vs_mae_pearson']:.3f}`.

## Canonical artifact source

All values and plots in this figure set are generated directly from `models/evaluation/legacy_pic50_baseline/`.
"""
    (output_dir / "uncertainty_figure_set_note.md").write_text(note, encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    predictions = pd.read_csv(input_dir / "ccle_predictions_with_uncertainty.tsv", sep="\t")
    uncertainty_bins = pd.read_csv(input_dir / "uncertainty_bin_metrics.tsv", sep="\t")
    applicability_bins = pd.read_csv(input_dir / "applicability_bin_metrics.tsv", sep="\t")
    cell_line_metrics = pd.read_csv(input_dir / "cell_line_applicability_metrics.tsv", sep="\t")
    calibration_metrics = pd.read_csv(input_dir / "conformal_interval_calibration_metrics.tsv", sep="\t")
    subgroup_metrics = pd.read_csv(input_dir / "conformal_subgroup_interval_metrics.tsv", sep="\t")
    summary = json.loads((input_dir / "uncertainty_applicability_summary.json").read_text(encoding="utf-8"))

    generate_uncertainty_figure(predictions, uncertainty_bins, summary, output_dir)
    generate_applicability_figure(cell_line_metrics, applicability_bins, summary, output_dir)
    generate_uncertainty_calibration_figure(calibration_metrics, subgroup_metrics, summary, output_dir)
    write_note(output_dir, summary)

    print("summary:")
    print(f"input_dir: {input_dir}")
    print(f"output_dir: {output_dir}")
    print(f"generated: {output_dir / 'legacy_benchmark_uncertainty.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_uncertainty.svg'}")
    print(f"generated: {output_dir / 'legacy_benchmark_applicability.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_applicability.svg'}")
    print(f"generated: {output_dir / 'legacy_benchmark_uncertainty_calibration.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_uncertainty_calibration.svg'}")
    print(f"generated: {output_dir / 'uncertainty_figure_set_note.md'}")


if __name__ == "__main__":
    main()
