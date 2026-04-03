from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from ._common import DEFAULT_ARTIFACT_MANIFEST_PATH
except ImportError:
    from _common import DEFAULT_ARTIFACT_MANIFEST_PATH


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the preserved legacy prediction artifacts.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_MANIFEST_PATH,
        help="Artifact manifest JSON describing the expected legacy files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_root = Path(manifest["source_root"]).resolve()
    print(f"artifact_set: {manifest['artifact_set']}")
    print(f"manifest_path: {manifest_path}")
    print(f"source_root: {source_root}")

    verified = 0
    missing = 0
    mismatched = 0
    for artifact in manifest["artifacts"]:
        relative_dir = artifact.get("relative_dir", ".")
        path = source_root / relative_dir / artifact["filename"]
        print(f"\n[{artifact['name']}]")
        print(f"path: {path}")
        if not path.exists():
            print("status: missing")
            missing += 1
            continue
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        print(f"size_bytes: {actual_size}")
        print(f"sha256: {actual_hash}")
        print(f"expected_sha256: {artifact['sha256']}")
        print(f"expected_size_bytes: {artifact['size_bytes']}")
        if actual_size != artifact["size_bytes"] or actual_hash != artifact["sha256"]:
            print("status: mismatch")
            mismatched += 1
        else:
            print("status: verified")
            verified += 1

    print("\nsummary:")
    print(f"verified: {verified}")
    print(f"missing: {missing}")
    print(f"mismatched: {mismatched}")
    print(f"result: {'pass' if missing == 0 and mismatched == 0 else 'fail'}")

    if missing or mismatched:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
