from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "configs" / "models" / "legacy-pic50-artifacts.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    source_root = Path(manifest["source_root"])
    print(f"artifact_set: {manifest['artifact_set']}")
    print(f"source_root: {source_root}")

    failed = False
    for artifact in manifest["artifacts"]:
        relative_dir = artifact.get("relative_dir", ".")
        path = source_root / relative_dir / artifact["filename"]
        print(f"\n[{artifact['name']}]")
        print(f"path: {path}")
        if not path.exists():
            print("status: missing")
            failed = True
            continue
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        print(f"size_bytes: {actual_size}")
        print(f"sha256: {actual_hash}")
        print(f"expected_sha256: {artifact['sha256']}")
        print(f"expected_size_bytes: {artifact['size_bytes']}")
        if actual_size != artifact["size_bytes"] or actual_hash != artifact["sha256"]:
            print("status: mismatch")
            failed = True
        else:
            print("status: verified")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
