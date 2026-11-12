"""Offline 5W1H knowledge-card integrity checker for the thesis repository.

[REF KNOWLEDGE_BASE/README.md; engineering/rules/CORE_RULES.md]
Checks local canonical source/guide paths, card IDs and required fields.
This is a documentation link audit, NOT structural or solver validation.
Standard-library only, compatible with Python 3.12 / Spyder. No network.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
CARD_FILE = Path("KNOWLEDGE_BASE/01_WORKFLOWS/WORKFLOW_CARDS.csv")
MANDATORY = (
    "ID", "Title", "When", "Why", "How", "Where_Canonical_Source",
    "Which_Inputs", "Who_Accountable_Roles", "Acceptance_Gate", "Guide", "Priority",
)


def audit_knowledge_cards(root):
    """Return link/ownership coverage without executing any engineering model.

    [REF KNOWLEDGE_BASE/01_WORKFLOWS/WORKFLOW_CARDS.csv]
    """
    root = Path(root).resolve()
    manifest = root / CARD_FILE
    if not manifest.is_file():
        return {"status": "INVALID", "cards": 0,
                "errors": [f"Missing knowledge-card register: {CARD_FILE}"]}
    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        missing_fields = [name for name in MANDATORY if name not in fields]
        rows = list(reader)
    errors = [f"Missing mandatory CSV field: {name}" for name in missing_fields]
    seen = set()
    missing_paths = []
    for line, row in enumerate(rows, 2):
        key = (row.get("ID") or "").strip()
        if key in seen:
            errors.append(f"Duplicate workflow ID at line {line}: {key}")
        seen.add(key)
        for name in MANDATORY:
            if not (row.get(name) or "").strip():
                errors.append(f"Empty {name} in row {line} ({key or 'NO_ID'})")
        for field in ("Where_Canonical_Source", "Guide"):
            value = (row.get(field) or "").strip()
            if not value:
                continue
            rel = Path(value)
            # Canonical knowledge links are repo-relative, not source machine
            # absolute private paths or a way to traverse outside repository.
            if rel.is_absolute() or ".." in rel.parts or "\\" in value:
                errors.append(f"Unsafe {field} path at line {line}: {value}")
                continue
            if not (root / rel).is_file():
                missing_paths.append(dict(id=key, field=field, path=value))
                errors.append(f"Missing referenced {field} at row {line}: {value}")
    return dict(
        status="PASS_NAVIGATION_ONLY" if not errors else "INVALID",
        cards=len(rows), distinct_ids=len(seen), missing_paths=missing_paths,
        errors=errors, limitations=(
            "A card with correct links is not code-semantic review, "
            "material calibration, native OpenSees convergence or NBC acceptance."
        ),
    )


def main(argv=None):
    """Command-line audit with optional local JSON report.

    [REF KNOWLEDGE_BASE/README.md]
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--json-out", type=Path, default=None,
                        help="Optional local summary path; never required for audit.")
    args = parser.parse_args(argv)
    result = audit_knowledge_cards(args.root)
    if args.json_out is not None:
        dest = args.json_out.resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS_NAVIGATION_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
