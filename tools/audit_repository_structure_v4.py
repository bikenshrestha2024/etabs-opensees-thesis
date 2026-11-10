"""Read-only repository inventory for the ETABS–OpenSees V4 migration.

Run from any directory:
    python tools/audit_repository_structure_v4.py --output docs/architecture/generated

Only tracked files are examined. The script never imports project modules or
executes engineering analyses. Outputs are reports, not engineering validation.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADERS = [
    "relative_path", "extension", "size_bytes", "sha256", "git_status",
    "purpose_hint", "owner_hint", "classification", "imports",
    "imported_by", "duplicate_group", "migration_risk", "review_required",
]


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached"],
        check=True, capture_output=True,
    )
    return sorted({
        item.decode("utf-8", errors="surrogateescape")
        for item in result.stdout.split(b"\0") if item
    })


def safe_classification(path: str) -> tuple[str, str]:
    parts = Path(path).parts
    first = parts[0] if parts else ""
    if first.startswith("Saved_Project_") or first.startswith("Worked_Example_"):
        return "historical_candidate", "HIGH"
    if first in {"components", "Research_Components", "src"}:
        return "active_or_experimental_review", "HIGH"
    if first in {"tests", "tools"}:
        return "verification_or_tool", "MEDIUM"
    if first == "docs":
        return "documentation", "LOW"
    if len(parts) == 1 and path.endswith(".py"):
        return "launcher_or_legacy_review", "HIGH"
    return "unclassified_review", "MEDIUM"


def imports_of(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (OSError, SyntaxError, UnicodeError):
        return []
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add("." * node.level + (node.module or ""))
    return sorted(names)


def module_candidates(rel: str) -> set[str]:
    if not rel.endswith(".py"):
        return set()
    name = rel[:-3].replace("/", ".").replace("\\\\", ".")
    candidates = {name}
    if name.endswith(".__init__"):
        candidates.add(name[:-9])
    return candidates



def inspect_gui_and_dynamic(path: Path, rel: str) -> tuple[list[dict], list[dict]]:
    """Report possible GUI action bindings and dynamic loads; never execute source.

    A static hint is not proof a widget exists or a callback is reachable.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (OSError, SyntaxError, UnicodeError):
        return [], []
    actions: list[dict] = []
    dynamic: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = ast.unparse(node.func)
        last = target.rsplit(".", 1)[-1]
        if last in {"Button", "CTkButton", "ttk.Button", "QPushButton", "add_command"} or target.endswith(".Button"):
            kws = {kw.arg: kw.value for kw in node.keywords if kw.arg}
            callbacks = [kw for kw in ("command", "callback", "clicked") if kw in kws]
            if callbacks:
                actions.append({
                    "source_file": rel, "line": node.lineno,
                    "widget_constructor": target,
                    "label_expression": ast.unparse(kws.get("text", kws.get("label"))) if ("text" in kws or "label" in kws) else "",
                    "callback_expression": "; ".join(ast.unparse(kws[x]) for x in callbacks),
                    "classification": "STATIC_CANDIDATE_NEEDS_RUNTIME_REVIEW",
                })
        if last in {"import_module", "__import__", "exec", "eval", "runpy", "getattr", "load_source"}:
            dynamic.append({
                "source_file": rel, "line": node.lineno,
                "expression": ast.unparse(node)[:600],
                "classification": "DYNAMIC_OR_REFLECTIVE_CALL_REVIEW",
            })
    return actions, dynamic


def write_table(path: Path, headers: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

def generate(root: Path, output: Path) -> dict:
    paths = tracked_files(root)
    rows: list[dict] = []
    gui_actions: list[dict] = []
    dynamic_calls: list[dict] = []
    by_digest: dict[str, list[str]] = defaultdict(list)
    module_paths: dict[str, set[str]] = defaultdict(set)
    for rel in paths:
        for module in module_candidates(rel):
            module_paths[module].add(rel)
    for rel in paths:
        path = root / rel
        classification, risk = safe_classification(rel)
        if not path.is_file():
            # Git submodules and missing sparse-checkout files are not audited.
            rows.append({
                "relative_path": rel, "extension": Path(rel).suffix,
                "size_bytes": "", "sha256": "", "git_status": "MISSING_LOCAL",
                "purpose_hint": "", "owner_hint": rel.split("/")[0],
                "classification": "unavailable", "imports": [],
                "imported_by": [], "duplicate_group": "",
                "migration_risk": "HIGH", "review_required": "YES",
            })
            continue
        digest = hashlib.file_digest(path.open("rb"), "sha256").hexdigest() if False else ""
        # Stream manually, ensuring the file handle is closed on every platform.
        hasher = hashlib.sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                hasher.update(chunk)
        digest = hasher.hexdigest()
        by_digest[digest].append(rel)
        if path.suffix.lower() == ".py":
            actions, dynamic = inspect_gui_and_dynamic(path, rel)
            gui_actions.extend(actions)
            dynamic_calls.extend(dynamic)
        rows.append({
            "relative_path": rel, "extension": path.suffix.lower(),
            "size_bytes": path.stat().st_size, "sha256": digest,
            "git_status": "TRACKED", "purpose_hint": "",
            "owner_hint": rel.split("/")[0], "classification": classification,
            "imports": imports_of(path) if path.suffix == ".py" else [],
            "imported_by": [], "duplicate_group": "",
            "migration_risk": risk, "review_required": "YES",
        })

    reverse: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        for imp in row["imports"]:
            for candidate, owned_files in module_paths.items():
                if candidate == imp or candidate.startswith(imp + "."):
                    for owned in owned_files:
                        reverse[owned].add(row["relative_path"])
    dup_ids = {
        digest: f"SHA256_{i:04d}"
        for i, digest in enumerate(
            sorted(k for k, v in by_digest.items() if len(v) > 1), 1
        )
    }
    for row in rows:
        row["imported_by"] = sorted(reverse[row["relative_path"]])
        row["duplicate_group"] = dup_ids.get(row["sha256"], "")
    output.mkdir(parents=True, exist_ok=True)
    write_table(
        output / "GUI_ACTION_INVENTORY.csv",
        ["source_file", "line", "widget_constructor", "label_expression",
         "callback_expression", "classification"],
        gui_actions,
    )
    write_table(
        output / "DYNAMIC_REFERENCE_AUDIT.csv",
        ["source_file", "line", "expression", "classification"],
        dynamic_calls,
    )
    with (output / "REPOSITORY_FILE_INVENTORY.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                **row,
                "imports": json.dumps(row["imports"]),
                "imported_by": json.dumps(row["imported_by"]),
            })
    hierarchy: dict = {}
    for rel in paths:
        node = hierarchy
        for part in Path(rel).parts[:-1]:
            node = node.setdefault(part, {})
        node[Path(rel).name] = None
    (output / "REPOSITORY_TREE.json").write_text(
        json.dumps(hierarchy, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output / "REPOSITORY_TREE.txt").write_text(
        "\n".join(paths) + "\n", encoding="utf-8"
    )
    duplicates = [
        {"sha256": sha, "classification": "exact_bytes_only_not_safe_to_delete",
         "paths": sorted(members)}
        for sha, members in sorted(by_digest.items())
        if len(members) > 1
    ]
    (output / "EXACT_DUPLICATE_CANDIDATES.json").write_text(
        json.dumps(duplicates, indent=2) + "\n", encoding="utf-8"
    )
    (output / "IMPORT_GRAPH.json").write_text(
        json.dumps({
            row["relative_path"]: {
                "imports": row["imports"], "imported_by": row["imported_by"]
            } for row in rows if row["extension"] == ".py"
        }, indent=2) + "\n", encoding="utf-8",
    )
    meta = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    summary = {
        "source_commit": meta, "tracked_file_count": len(rows),
        "python_file_count": sum(x["extension"] == ".py" for x in rows),
        "exact_duplicate_groups": len(duplicates),
        "static_gui_candidates": len(gui_actions),
        "dynamic_call_candidates": len(dynamic_calls),
        "missing_local_count": sum(x["git_status"] == "MISSING_LOCAL" for x in rows),
        "limitations": [
            "SHA matches are candidate duplicates; not safe deletion approvals.",
            "Imports are static AST references; dynamic imports, strings, external launchers and runtime paths require manual review.",
            "No ETABS/OpenSees execution or engineering equivalence is tested.",
            "No file is moved, deleted, or rewritten by the audit.",
            "GUI bindings and dynamic calls are conservative static candidates, not complete UI/event coverage.",
        ],
    }
    (output / "AUDIT_SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "docs/architecture/generated"
    )
    args = parser.parse_args()
    print(json.dumps(generate(ROOT, args.output.resolve()), indent=2))


if __name__ == "__main__":
    main()
