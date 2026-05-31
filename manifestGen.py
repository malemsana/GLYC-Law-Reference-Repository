import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# Repository root = folder where this script lives
REPO_ROOT = Path(__file__).parent.resolve()

IGNORE_FILES = {
    "manifest.json",
    "manifestGen.py"
}

IGNORE_DIRS = {
    ".git",
    "__pycache__"
}


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


generated_at = (
    datetime.now(timezone.utc)
    .isoformat()
    .replace("+00:00", "Z")
)

manifest = {
    "manifest_version": 1,
    "generated_at": generated_at,
    "hash_algorithm": "sha256",
    "files": {}
}

for file_path in REPO_ROOT.rglob("*"):

    if not file_path.is_file():
        continue

    if file_path.name in IGNORE_FILES:
        continue

    if any(
        part in IGNORE_DIRS
        for part in file_path.parts
    ):
        continue

    relative_path = (
        file_path
        .relative_to(REPO_ROOT)
        .as_posix()
    )

    print(f"Hashing: {relative_path}")

    manifest["files"][relative_path] = {
        "sha256": sha256_file(file_path),
        "size": file_path.stat().st_size
    }

output_path = REPO_ROOT / "manifest.json"

with open(
    output_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        manifest,
        f,
        indent=2,
        ensure_ascii=False
    )

print()
print(f"Manifest written to: {output_path}")
print(f"Generated at: {generated_at}")
print(f"Files indexed: {len(manifest['files'])}")