from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "models" / "legacy-pic50-benchmark-config.json"
DEFAULT_ARTIFACT_MANIFEST_PATH = REPO_ROOT / "configs" / "models" / "legacy-pic50-artifacts.json"


@dataclass(frozen=True)
class BenchmarkPaths:
    legacy_root: Path
    output_dir: Path
    gdsc_response_path: Path
    ccle_vector_path: Path
    prepared_ccle_response_path: Path
    raw_ccle_response_path: Path
    artifact_manifest_path: Path


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_token(value: Any) -> str:
    return "".join(character for character in str(value).lower() if character.isalnum())


def require_existing(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing required {label}: {path}")


def resolve_output_dir(preferred_path: Path, override: str | None = None) -> Path:
    if override:
        output_dir = Path(override).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    try:
        preferred_path.mkdir(parents=True, exist_ok=True)
        return preferred_path
    except OSError:
        fallback_dir = Path("/tmp/pharmacoprofiler_outputs/legacy_pic50_baseline").resolve()
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir


def resolve_benchmark_paths(
    config: dict[str, Any],
    config_root: Path = REPO_ROOT,
    output_dir_override: str | None = None,
) -> BenchmarkPaths:
    legacy_root = Path(config["legacy_root"]).resolve()
    preferred_output_dir = (config_root / config["output_dir"]).resolve()
    return BenchmarkPaths(
        legacy_root=legacy_root,
        output_dir=resolve_output_dir(preferred_output_dir, output_dir_override),
        gdsc_response_path=(legacy_root / config["gdsc_response_path"]).resolve(),
        ccle_vector_path=(legacy_root / config["ccle_vector_path"]).resolve(),
        prepared_ccle_response_path=(legacy_root / config["prepared_ccle_response_path"]).resolve(),
        raw_ccle_response_path=(legacy_root / config["raw_ccle_response_path"]).resolve(),
        artifact_manifest_path=(config_root / config["artifact_manifest"]).resolve(),
    )


def resolve_manifest_artifacts(manifest_path: Path) -> dict[str, Path]:
    manifest = load_json(manifest_path)
    source_root = Path(manifest["source_root"]).resolve()
    resolved: dict[str, Path] = {}
    for artifact in manifest["artifacts"]:
        relative_dir = artifact.get("relative_dir", ".")
        resolved[artifact["name"]] = (source_root / relative_dir / artifact["filename"]).resolve()
    return resolved


def fingerprint_map_from_gdsc(gdsc_df: Any) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for _, row in gdsc_df[["DRUG_NAME", "DRUG_NAME_edited", "FINGERPRINT"]].dropna().iterrows():
        fingerprint = str(row["FINGERPRINT"])
        if len(fingerprint) != 1024:
            continue
        for source_value in (row["DRUG_NAME"], row["DRUG_NAME_edited"]):
            key = normalize_token(source_value)
            if key and key not in mapping:
                mapping[key] = fingerprint
    return mapping
