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
DEFAULT_POSITIONING_MATRIX = DEFAULT_OUTPUT_DIR / "platform_positioning_matrix.tsv"
DEFAULT_LEAKAGE_SAFE_COMPARISON = REPO_ROOT / "models" / "evaluation" / "leakage_safe_regimes" / "ridge_regime_comparison.tsv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate manuscript-quality figures from legacy benchmark artifacts.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing canonical legacy benchmark artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated manuscript figure assets.",
    )
    parser.add_argument(
        "--positioning-matrix",
        type=Path,
        default=DEFAULT_POSITIONING_MATRIX,
        help="TSV describing the competitive-positioning matrix for the strategic figure.",
    )
    parser.add_argument(
        "--leakage-safe-comparison",
        type=Path,
        default=DEFAULT_LEAKAGE_SAFE_COMPARISON,
        help="TSV describing the staged ridge leakage-safe regime comparison.",
    )
    return parser.parse_args()


def load_artifacts(input_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict, dict]:
    predictions = pd.read_csv(input_dir / "ccle_predictions.tsv", sep="\t")
    tissue_metrics = pd.read_csv(input_dir / "tissue_metrics.tsv", sep="\t")
    potency_bins = pd.read_csv(input_dir / "potency_bin_metrics.tsv", sep="\t")
    top_errors = pd.read_csv(input_dir / "top_error_examples.tsv", sep="\t")
    summary = json.loads((input_dir / "subgroup_analysis_summary.json").read_text(encoding="utf-8"))
    benchmark_summary = json.loads((input_dir / "benchmark_summary.json").read_text(encoding="utf-8"))
    return predictions, tissue_metrics, potency_bins, top_errors, summary, benchmark_summary


def add_error_columns(predictions: pd.DataFrame) -> pd.DataFrame:
    df = predictions.copy()
    df["signed_error"] = df["pIC50_Pred"] - df["pIC50_True"]
    df["absolute_error"] = df["signed_error"].abs()
    return df


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.svg", bbox_inches="tight")


def generate_overview_figure(
    predictions: pd.DataFrame,
    tissue_metrics: pd.DataFrame,
    potency_bins: pd.DataFrame,
    summary: dict,
    output_dir: Path,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    scatter_ax = axes[0, 0]
    scatter_ax.hexbin(
        predictions["pIC50_True"],
        predictions["pIC50_Pred"],
        gridsize=42,
        cmap="YlGnBu",
        mincnt=1,
    )
    lim_min = min(predictions["pIC50_True"].min(), predictions["pIC50_Pred"].min())
    lim_max = max(predictions["pIC50_True"].max(), predictions["pIC50_Pred"].max())
    scatter_ax.plot([lim_min, lim_max], [lim_min, lim_max], linestyle="--", color="#444444", linewidth=1.5)
    scatter_ax.set_title("A. Predicted vs true pIC50")
    scatter_ax.set_xlabel("True pIC50")
    scatter_ax.set_ylabel("Predicted pIC50")
    metrics = summary["global_metrics"]
    calibration = summary["calibration"]
    scatter_ax.text(
        0.03,
        0.97,
        (
            f"n = {metrics['rows']}\n"
            f"Pearson r = {metrics['pearson_r']:.3f}\n"
            f"RMSE = {metrics['rmse']:.3f}\n"
            f"R² = {metrics['r_squared']:.3f}\n"
            f"Slope = {calibration['global_slope']:.3f}"
        ),
        transform=scatter_ax.transAxes,
        va="top",
        ha="left",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.9, "edgecolor": "#cccccc"},
    )

    potency_ax = axes[0, 1]
    potency_plot_df = potency_bins.copy()
    potency_plot_df["potency_bin"] = potency_plot_df["potency_bin"].astype(str)
    sns.barplot(data=potency_plot_df, x="potency_bin", y="mae", color="#2C7FB8", ax=potency_ax)
    potency_ax.set_title("B. Error rises with stronger responses")
    potency_ax.set_xlabel("Observed pIC50 bin")
    potency_ax.set_ylabel("MAE")
    for idx, row in potency_plot_df.iterrows():
        potency_ax.text(idx, row["mae"] + 0.03, f"{row['mean_signed_error']:.2f}", ha="center", va="bottom", fontsize=10)
    potency_ax.text(
        0.02,
        0.98,
        "Labels show mean signed error",
        transform=potency_ax.transAxes,
        va="top",
        ha="left",
        fontsize=10,
    )

    tissue_ax = axes[1, 0]
    tissue_plot_df = tissue_metrics[tissue_metrics["n"] >= 50].nlargest(12, "mae").sort_values("mae", ascending=True)
    sns.barplot(data=tissue_plot_df, x="mae", y="TISSUE_DISPLAY", color="#D95F0E", ax=tissue_ax)
    tissue_ax.set_title("C. Tissue-level heterogeneity")
    tissue_ax.set_xlabel("MAE")
    tissue_ax.set_ylabel("Normalized tissue group")

    bias_ax = axes[1, 1]
    sns.histplot(predictions["signed_error"], bins=40, color="#756BB1", ax=bias_ax)
    bias_ax.axvline(0, linestyle="--", color="#444444", linewidth=1.5)
    bias_ax.axvline(metrics["mean_signed_error"], linestyle="-", color="#D95F0E", linewidth=2)
    bias_ax.set_title("D. Error distribution is left-shifted")
    bias_ax.set_xlabel("Signed error (predicted - true)")
    bias_ax.set_ylabel("Count")
    bias_ax.text(
        0.03,
        0.97,
        (
            f"Mean signed error = {metrics['mean_signed_error']:.3f}\n"
            f"Underpredict share = {metrics['underpredict_share']:.1%}\n"
            f"Overpredict share = {metrics['overpredict_share']:.1%}"
        ),
        transform=bias_ax.transAxes,
        va="top",
        ha="left",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.9, "edgecolor": "#cccccc"},
    )

    fig.suptitle("Legacy GDSC-to-CCLE baseline benchmark overview", fontsize=20, y=1.02)
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_overview")
    plt.close(fig)


def generate_drug_heatmap_figure(output_dir: Path, input_dir: Path) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    drug_metrics = pd.read_csv(input_dir / "drug_metrics.tsv", sep="\t")
    plot_df = drug_metrics.sort_values("mae", ascending=True)
    fig, ax = plt.subplots(figsize=(11, 8))
    sns.barplot(data=plot_df, x="mae", y="DRUG_NAME", color="#238B45", ax=ax)
    ax.set_title("Legacy cross-domain benchmark by compound")
    ax.set_xlabel("MAE")
    ax.set_ylabel("Drug")
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_drug_mae")
    plt.close(fig)


def generate_ci_summary_figure(summary: dict, benchmark_summary: dict, output_dir: Path) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    ci_summary = summary["bootstrap_ci_95"]
    metric_order = ["pearson_r", "spearman_r", "mae", "rmse", "r_squared"]
    metric_labels = {
        "pearson_r": "Pearson r",
        "spearman_r": "Spearman r",
        "mae": "MAE",
        "rmse": "RMSE",
        "r_squared": "R²",
    }
    rows = []
    for metric in metric_order:
        rows.append(
            {
                "metric": metric_labels[metric],
                "mean": ci_summary[metric]["mean"],
                "low": ci_summary[metric]["ci95_low"],
                "high": ci_summary[metric]["ci95_high"],
            }
        )
    ci_df = pd.DataFrame(rows)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    corr_df = ci_df.iloc[:2].copy()
    err_df = ci_df.iloc[2:].copy()

    axes[0].errorbar(
        x=corr_df["mean"],
        y=corr_df["metric"],
        xerr=[corr_df["mean"] - corr_df["low"], corr_df["high"] - corr_df["mean"]],
        fmt="o",
        color="#1F78B4",
        ecolor="#1F78B4",
        elinewidth=2,
        capsize=4,
    )
    axes[0].set_title("A. Correlation metrics with bootstrap 95% CI")
    axes[0].set_xlabel("Metric value")
    axes[0].set_ylabel("")
    axes[0].set_xlim(0.55, 0.80)

    axes[1].errorbar(
        x=err_df["mean"],
        y=err_df["metric"],
        xerr=[err_df["mean"] - err_df["low"], err_df["high"] - err_df["mean"]],
        fmt="o",
        color="#D95F0E",
        ecolor="#D95F0E",
        elinewidth=2,
        capsize=4,
    )
    axes[1].set_title("B. Error metrics with bootstrap 95% CI")
    axes[1].set_xlabel("Metric value")
    axes[1].set_ylabel("")

    fig.suptitle(
        (
            "Benchmark confidence intervals and evaluation scope\n"
            f"{benchmark_summary['dataset_summary']['evaluated_ccle_rows']} CCLE rows, "
            f"{benchmark_summary['dataset_summary']['evaluated_ccle_drugs']} drugs, "
            f"{benchmark_summary['dataset_summary']['evaluated_ccle_cell_lines']} cell lines"
        ),
        fontsize=18,
        y=1.03,
    )
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_confidence_intervals")
    plt.close(fig)


def generate_top_error_figure(top_errors: pd.DataFrame, output_dir: Path) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plot_df = top_errors.head(12).copy().iloc[::-1]
    plot_df["label"] = plot_df["CELL_LINE_NAME"].str.upper() + " | " + plot_df["DRUG_NAME"]
    fig, ax = plt.subplots(figsize=(14, 8))
    palette = ["#B2182B" if value < 0 else "#2166AC" for value in plot_df["signed_error"]]
    ax.barh(plot_df["label"], plot_df["signed_error"], color=palette)
    ax.axvline(0, linestyle="--", color="#444444", linewidth=1.5)
    ax.set_title("Largest benchmark errors are dominated by strong underprediction")
    ax.set_xlabel("Signed error (predicted - true)")
    ax.set_ylabel("Cell line | drug")
    for idx, row in enumerate(plot_df.itertuples(index=False)):
        ax.text(
            row.signed_error - 0.05 if row.signed_error < 0 else row.signed_error + 0.05,
            idx,
            f"{row.TISSUE_DISPLAY}",
            va="center",
            ha="right" if row.signed_error < 0 else "left",
            fontsize=10,
        )
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_top_errors")
    plt.close(fig)


def generate_calibration_detail_figure(predictions: pd.DataFrame, summary: dict, output_dir: Path) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    df = predictions.copy()
    df["observed_decile"] = pd.qcut(df["pIC50_True"], q=10, duplicates="drop")
    grouped = (
        df.groupby("observed_decile", observed=False)
        .agg(
            true_mean=("pIC50_True", "mean"),
            pred_mean=("pIC50_Pred", "mean"),
            signed_error=("signed_error", "mean"),
        )
        .reset_index(drop=True)
    )

    calibration = summary["calibration"]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    axes[0].scatter(df["pIC50_True"], df["pIC50_Pred"], s=8, alpha=0.12, color="#1F78B4", edgecolor="none")
    axes[0].plot(grouped["true_mean"], grouped["pred_mean"], marker="o", color="#D95F0E", linewidth=2.5)
    lim_min = min(df["pIC50_True"].min(), df["pIC50_Pred"].min())
    lim_max = max(df["pIC50_True"].max(), df["pIC50_Pred"].max())
    axes[0].plot([lim_min, lim_max], [lim_min, lim_max], linestyle="--", color="#444444", linewidth=1.5)
    fit_x = pd.Series([lim_min, lim_max])
    fit_y = calibration["global_slope"] * fit_x + calibration["global_intercept"]
    axes[0].plot(fit_x, fit_y, color="#756BB1", linewidth=2)
    axes[0].set_title("A. Calibration curve and fitted line")
    axes[0].set_xlabel("Observed pIC50")
    axes[0].set_ylabel("Predicted pIC50")

    axes[1].bar(range(len(grouped)), grouped["signed_error"], color="#B2182B")
    axes[1].axhline(0, linestyle="--", color="#444444", linewidth=1.5)
    axes[1].set_xticks(range(len(grouped)))
    axes[1].set_xticklabels([f"D{i+1}" for i in range(len(grouped))])
    axes[1].set_title("B. Mean signed error by observed decile")
    axes[1].set_xlabel("Observed pIC50 decile")
    axes[1].set_ylabel("Mean signed error")

    fig.suptitle("Calibration detail for the legacy cross-domain baseline", fontsize=18, y=1.02)
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_calibration")
    plt.close(fig)


def generate_subgroup_variability_figure(
    tissue_metrics: pd.DataFrame,
    input_dir: Path,
    output_dir: Path,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    drug_metrics = pd.read_csv(input_dir / "drug_metrics.tsv", sep="\t")
    tissue_plot_df = tissue_metrics.nlargest(12, "n").sort_values("mae", ascending=True)
    drug_plot_df = drug_metrics.sort_values("mean_signed_error", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    sns.barplot(data=tissue_plot_df, x="mae", y="TISSUE_DISPLAY", color="#2C7FB8", ax=axes[0])
    axes[0].set_title("A. Largest tissue groups by MAE")
    axes[0].set_xlabel("MAE")
    axes[0].set_ylabel("Normalized tissue group")

    palette = ["#B2182B" if value < 0 else "#2166AC" for value in drug_plot_df["mean_signed_error"]]
    axes[1].barh(drug_plot_df["DRUG_NAME"], drug_plot_df["mean_signed_error"], color=palette)
    axes[1].axvline(0, linestyle="--", color="#444444", linewidth=1.5)
    axes[1].set_title("B. Drug-level bias is mostly underprediction")
    axes[1].set_xlabel("Mean signed error")
    axes[1].set_ylabel("Drug")

    fig.suptitle("Subgroup variability in the preserved cross-domain overlap", fontsize=18, y=1.02)
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_subgroup_variability")
    plt.close(fig)


def generate_positioning_figure(positioning_matrix_path: Path, output_dir: Path) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    matrix = pd.read_csv(positioning_matrix_path, sep="\t")
    plot_df = matrix.set_index("tool")
    rename_map = {
        "cross_resource_harmonization": "Cross-resource\nharmonization",
        "public_inference_serving": "Public inference\nserving",
        "metadata_rich_outputs": "Metadata-rich\noutputs",
        "benchmark_transparency": "Benchmark\ntransparency",
        "single_agent_prediction_focus": "Single-agent\nprediction",
        "combination_analysis_focus": "Combination\nanalysis",
        "model_method_innovation": "Model-method\ninnovation",
    }
    plot_df = plot_df.rename(columns=rename_map)
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(
        plot_df,
        annot=True,
        fmt=".0f",
        cmap=sns.color_palette(["#F7F7F7", "#A6CEE3", "#1F78B4"], as_cmap=True),
        cbar=False,
        linewidths=0.5,
        linecolor="white",
        ax=ax,
    )
    ax.set_title("Competitive positioning matrix from verified project scope", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    save_figure(fig, output_dir, "platform_positioning_comparison")
    plt.close(fig)


def generate_leakage_safe_regime_figure(leakage_safe_path: Path, output_dir: Path) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    regime_df = pd.read_csv(leakage_safe_path, sep="\t")
    order = ["pair_random", "cell_line_holdout", "compound_holdout", "double_cold_start"]
    label_map = {
        "pair_random": "Pair-random",
        "cell_line_holdout": "Cell-line holdout",
        "compound_holdout": "Compound holdout",
        "double_cold_start": "Double cold start",
    }
    plot_df = regime_df.copy()
    plot_df["regime_name"] = pd.Categorical(plot_df["regime_name"], categories=order, ordered=True)
    plot_df = plot_df.sort_values("regime_name").copy()
    plot_df["regime_label"] = plot_df["regime_name"].map(label_map)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    performance_df = plot_df.melt(
        id_vars=["regime_label"],
        value_vars=["mean_mae", "mean_rmse"],
        var_name="metric",
        value_name="value",
    )
    performance_df["metric"] = performance_df["metric"].map({"mean_mae": "MAE", "mean_rmse": "RMSE"})
    sns.barplot(
        data=performance_df,
        x="value",
        y="regime_label",
        hue="metric",
        palette=["#D95F0E", "#756BB1"],
        ax=axes[0],
    )
    axes[0].set_title("A. Error rises under leakage-safe regimes")
    axes[0].set_xlabel("Metric value")
    axes[0].set_ylabel("")
    axes[0].legend(title="")

    correlation_df = plot_df.melt(
        id_vars=["regime_label"],
        value_vars=["mean_pearson_r", "mean_r_squared"],
        var_name="metric",
        value_name="value",
    )
    correlation_df["metric"] = correlation_df["metric"].map({"mean_pearson_r": "Pearson r", "mean_r_squared": "R²"})
    sns.barplot(
        data=correlation_df,
        x="value",
        y="regime_label",
        hue="metric",
        palette=["#1F78B4", "#33A02C"],
        ax=axes[1],
    )
    axes[1].axvline(0, linestyle="--", color="#444444", linewidth=1.3)
    axes[1].set_title("B. Correlation and explained variance collapse for unseen compounds")
    axes[1].set_xlabel("Metric value")
    axes[1].set_ylabel("")
    axes[1].legend(title="")

    fig.suptitle("Leakage-safe ridge benchmark comparison across saved GDSC split regimes", fontsize=18, y=1.03)
    fig.tight_layout()
    save_figure(fig, output_dir, "legacy_benchmark_leakage_safe_regimes")
    plt.close(fig)


def write_figure_note(output_dir: Path, summary: dict) -> None:
    metrics = summary["global_metrics"]
    calibration = summary["calibration"]
    note = f"""# Benchmark Figure Set

## Included figures

- `legacy_benchmark_overview.(png|svg)`: four-panel summary of the canonical GDSC-to-CCLE legacy baseline
- `legacy_benchmark_drug_mae.(png|svg)`: compound-level MAE ranking across the preserved overlap set
- `legacy_benchmark_confidence_intervals.(png|svg)`: bootstrap 95% confidence intervals for the core benchmark metrics
- `legacy_benchmark_top_errors.(png|svg)`: largest failure cases across the preserved CCLE overlap set
- `legacy_benchmark_calibration.(png|svg)`: detailed calibration view with observed-decile residual structure
- `legacy_benchmark_subgroup_variability.(png|svg)`: tissue-level error and drug-level bias summary
- `legacy_benchmark_leakage_safe_regimes.(png|svg)`: staged ridge comparison across pair-random, cell-line-holdout, compound-holdout, and double-cold-start regimes
- `platform_positioning_comparison.(png|svg)`: strategic positioning heatmap derived from the verified competitive analysis

## Figure-safe messages

- The legacy baseline shows strong correlation but incomplete explanatory strength: Pearson `r = {metrics['pearson_r']:.3f}`, Spearman `r = {metrics['spearman_r']:.3f}`, and `R² = {metrics['r_squared']:.3f}`.
- Errors are systematically left-shifted, with mean signed error `{metrics['mean_signed_error']:.3f}` and underprediction in `{metrics['underpredict_share']:.1%}` of benchmark rows.
- Calibration is compressed rather than ideal, with fitted slope `{calibration['global_slope']:.3f}` and intercept `{calibration['global_intercept']:.3f}`.
- Error worsens at higher observed pIC50 values, which should be framed as a key limitation rather than hidden in aggregate metrics.

## Canonical artifact source

All values and plots in this figure set are generated directly from `models/evaluation/legacy_pic50_baseline/`.
"""
    (output_dir / "benchmark_figure_set_note.md").write_text(note, encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    positioning_matrix_path = args.positioning_matrix.resolve()
    leakage_safe_path = args.leakage_safe_comparison.resolve()
    predictions, tissue_metrics, potency_bins, top_errors, summary, benchmark_summary = load_artifacts(input_dir)
    predictions = add_error_columns(predictions)
    generate_overview_figure(predictions, tissue_metrics, potency_bins, summary, output_dir)
    generate_drug_heatmap_figure(output_dir, input_dir)
    generate_ci_summary_figure(summary, benchmark_summary, output_dir)
    generate_top_error_figure(top_errors, output_dir)
    generate_calibration_detail_figure(predictions, summary, output_dir)
    generate_subgroup_variability_figure(tissue_metrics, input_dir, output_dir)
    generate_leakage_safe_regime_figure(leakage_safe_path, output_dir)
    generate_positioning_figure(positioning_matrix_path, output_dir)
    write_figure_note(output_dir, summary)
    print("summary:")
    print(f"input_dir: {input_dir}")
    print(f"output_dir: {output_dir}")
    print(f"generated: {output_dir / 'legacy_benchmark_overview.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_overview.svg'}")
    print(f"generated: {output_dir / 'legacy_benchmark_drug_mae.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_drug_mae.svg'}")
    print(f"generated: {output_dir / 'legacy_benchmark_confidence_intervals.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_confidence_intervals.svg'}")
    print(f"generated: {output_dir / 'legacy_benchmark_top_errors.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_top_errors.svg'}")
    print(f"generated: {output_dir / 'legacy_benchmark_calibration.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_calibration.svg'}")
    print(f"generated: {output_dir / 'legacy_benchmark_subgroup_variability.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_subgroup_variability.svg'}")
    print(f"generated: {output_dir / 'legacy_benchmark_leakage_safe_regimes.png'}")
    print(f"generated: {output_dir / 'legacy_benchmark_leakage_safe_regimes.svg'}")
    print(f"generated: {output_dir / 'platform_positioning_comparison.png'}")
    print(f"generated: {output_dir / 'platform_positioning_comparison.svg'}")
    print(f"generated: {output_dir / 'benchmark_figure_set_note.md'}")


if __name__ == "__main__":
    main()
