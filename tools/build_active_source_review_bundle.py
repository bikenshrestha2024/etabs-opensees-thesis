"""Make a code-only, read-only source review bundle from an existing Git checkout.

Explicit whitelist: tracked Python files in root, components/, src/, tools/ and
tests/, plus three public governance Markdown files. No EDB, XLSX, accelerogram,
model JSON, private configuration, archived snapshot or generated analysis output.
The Git index must be clean; the bundle is a temporary GitHub Actions artifact,
not a new source-file commit. It is NOT a claim of semantic review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

_SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(_SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SOURCE_ROOT))

ALLOWED_TREES = frozenset(("components", "src", "tools", "tests"))
GOVERNANCE = frozenset((
    "AGENTS.md",
    "engineering/rules/CORE_RULES.md",
    "engineering/rules/ENGINEERING_GATES.md",
))


def _tracked(root: Path) -> list[str]:
    raw = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z"])
    return sorted(x.decode("utf-8", "surrogateescape")
                  for x in raw.split(b"\0") if x)


def select_paths(root: Path) -> list[str]:
    root = Path(root).resolve(strict=True)
    paths = []
    for rel in _tracked(root):
        parts = Path(rel).parts
        accepted = (rel in GOVERNANCE
                    or (rel.endswith(".py")
                        and (len(parts) == 1 or parts[0] in ALLOWED_TREES)))
        if not accepted:
            continue
        file = root / rel
        # Fail closed for ANY linked path component: the snapshot must
        # represent actual tracked code within the selected checkout.
        if any(p.is_symlink() for p in (file, *file.parents)):
            raise ValueError("Linked source file/ancestor blocks review bundle: " + rel)
        if not file.is_file():
            raise ValueError("Missing selected tracked source: " + rel)
        paths.append(rel)
    return paths


def build(root: Path, destination: Path) -> dict:
    root = Path(root).resolve(strict=True)
    if subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain",
             "--untracked-files=no"]):
        raise ValueError("Tracked source differs from Git HEAD; refuse ambiguous review snapshot")
    destination = Path(destination).expanduser()
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError("Linked source-review destination is forbidden")
    if destination.exists():
        raise FileExistsError("Refusing to overwrite existing review bundle")
    # The existing public-tree scanner is redacted: do not upload candidate
    # tokens to CI artifacts if patterns suggest possible credentials.
    from tools.security_audit import audit as scan_secrets
    candidates, _ = scan_secrets(root)
    if candidates:
        raise ValueError("Possible secrets found in tracked tree; no source bundle created")
    selection = select_paths(root)
    head = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        text=True).strip()
    entries = []
    payloads = []
    for rel in selection:
        raw = (root / rel).read_bytes()
        entries.append({
            "path": rel,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "review_status": "SOURCE_PRESENT_NOT_SEMANTICALLY_REVIEWED",
        })
        payloads.append((rel, raw))
    manifest = {
        "schema": "ACTIVE_PUBLIC_SOURCE_REVIEW_SNAPSHOT_V1",
        "git_head": head,
        "file_count": len(entries),
        "scope": "TRACKED_ACTIVE_PYTHON_PLUS_EXPLICIT_GOVERNANCE_ONLY",
        "non_code_data_included": False,
        "semantic_review_completed": False,
        "native_engineering_validation": "NOT_PERFORMED",
        "files": entries,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as arc:
        for rel, raw in payloads:
            arc.writestr("SOURCE/" + rel, raw)
        arc.writestr("REVIEW_MANIFEST.json",
                     json.dumps(manifest, indent=2, ensure_ascii=False))
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path,
                        default=Path("audit/source_review/ACTIVE_SOURCE_REVIEW.zip"))
    args = parser.parse_args(argv)
    manifest = build(args.repo, args.output)
    print(json.dumps({k: manifest[k] for k in (
        "git_head", "file_count", "scope", "semantic_review_completed")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
