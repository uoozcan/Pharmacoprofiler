# Model Evaluation Outputs

This directory stores canonical, versioned benchmark outputs generated from the current repository.

The first benchmark target is the verified legacy GDSC-to-CCLE pIC50 baseline configured in:
- `configs/models/legacy-pic50-benchmark-config.json`
- `scripts/evaluate/run_legacy_benchmark_baseline.py`

That workflow writes outputs to `models/evaluation/legacy_pic50_baseline/` when executed in an environment that includes `joblib`, `scikit-learn`, `pandas`, `numpy`, and `scipy`.
