"""Read-only, tracked-file repository layout audit and relocation preflight.

No changes to source paths, ETABS exports or engineering results. Requires git.
Run: python tools/audit_repository_layout.py --output audit/repository_layout.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

READABLE = {".py", ".md", ".json", ".csv", ".toml", ".yaml", ".yml",
            ".ini", ".txt", ".cfg", ".bat", ".ps1"}
IMMOVABLE = {"README.md", "AGENTS.md", "CLAUDE.md", "SECURITY.md",
             "START_HERE.md", "00_READ_FIRST_RUN_ORDER.md"}
SCANNABLE_LIMIT = 2_000_000
NUMBERED = re.compile(r"^(\d\d)_.+\.py$", re.I)


def tracked_paths(root: Path) -> list[str]:
    command = ["git", "-C", str(root), "ls-files", "-z", "--cached"]
    completed = subprocess.run(command, capture_output=True, check=True)
    return sorted(x.decode("utf-8", "surrogateescape")
                  for x in completed.stdout.split(b"\0") if x)


def candidate_category(name: str) -> str:
    suffix = Path(name).suffix.lower()
    if name in IMMOVABLE or suffix == ".py":
        return "PINNED_COMPATIBILITY_OR_LAUNCHER"
    if suffix in {".json", ".csv", ".log"}:
        return "REVIEW_DATA_CHECK_REFERENCES"
    if suffix == ".md":
        return "DOCUMENT_CHECK_REFERENCES"
    return "MANUAL_REVIEW"


def audit(root: Path) -> dict:
    paths = tracked_paths(root)
    root_names = [p for p in paths if "/" not in p]
    numbered: dict[str, list[str]] = defaultdict(list)
    for name in root_names:
        match = NUMBERED.match(name)
        if match:
            numbered[match.group(1)].append(name)

    # A filename reference is a relocation blocker, not necessarily an import.
    # Search tracked text files only; source contents and secrets never enter JSON.
    references: dict[str, list[str]] = defaultdict(list)
    skipped = []
    targets = [name for name in root_names
               if candidate_category(name) not in
               {"PINNED_COMPATIBILITY_OR_LAUNCHER", "MANUAL_REVIEW"}]
    for rel in paths:
        path = root / rel
        if path.suffix.lower() not in READABLE:
            continue
        try:
            # Never follow tracked symlinks, including links leaving the checkout.
            # An audit must not read private local files outside its tracked tree.
            if path.is_symlink() or not path.is_file():
                skipped.append(rel)
                continue
            if path.stat().st_size > SCANNABLE_LIMIT:
                skipped.append(rel)
                continue
            data = path.read_text(encoding="utf-8-sig", errors="strict")
        except (OSError, UnicodeError):
            skipped.append(rel)
            continue
        for target in targets:
            if rel != target and target in data:
                references[target].append(rel)

    root_files = []
    for name in root_names:
        category = candidate_category(name)
        blockers = references.get(name, [])
        root_files.append({
            "path": name,
            "classification": category,
            "reference_file_count": len(blockers),
            "reference_files": blockers,
            "relocation_status": (
                "PINNED" if category == "PINNED_COMPATIBILITY_OR_LAUNCHER"
                else "HOLD_REVIEW_REQUIRED" if blockers or skipped
                else "CANDIDATE_NOT_APPROVED"
            ),
        })
    return {
        "schema_version": 1,
        "scope": "TRACKED_FILES_STATIC_ONLY",
        "total_tracked_files": len(paths),
        "root_file_count": len(root_names),
        "root_by_extension": dict(sorted(Counter(
            Path(p).suffix.lower() or "(none)" for p in root_names).items())),
        "duplicate_numbered_prefixes": {
            k: v for k, v in sorted(numbered.items()) if len(v) > 1},
        "skipped_text_files": skipped,
        "skipped_text_file_count": len(skipped),
        "source_changes_performed": False,
        "file_moves_approved": False,
        "root_files": root_files,
        "limitations": [
            "Static exact-name scans cannot detect constructed paths, imports or GUI callbacks.",
            "Untracked local and ignored files are excluded.",
            "Tracked symlinks and malformed or oversized text files are skipped; any skips block relocation approval.",
            "All relocation candidates require runtime consumer tests before a move.",
            "No native ETABS/OpenSees run, engineering check, or semantic code review.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = audit(args.root.resolve())
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        dest = args.output.expanduser().resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered, encoding="utf-8")
        print(f"Layout inventory: {dest}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
