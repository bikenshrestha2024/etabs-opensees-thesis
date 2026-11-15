"""Integrated, read-only repository coverage and source-dependency audit.

A tracked-file inventory is NOT a line-by-line semantic engineering review.
No ETABS API, OpenSees solver, GUI, source workbook or model export is executed.
Outputs are local CI artifacts under audit/, never a published user-data upload.

Usage: python tools/audit_repository_integrated.py --output audit/integrated
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Support direct 'python tools/audit_repository_integrated.py' invocation on Windows.
_SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(_SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SOURCE_ROOT))

from tools.audit_active_repository import inventory
from tools.audit_live_output_writers import scan_source
from tools.audit_repository_layout import tracked_paths
from tools.security_audit import audit as security_audit

ACTIVE_TOP = frozenset(("components", "src", "tools", "tests"))
HISTORICAL = ("archive/", "Saved_Project_", "Worked_Example_",
              "Verification_", "Research_Components/", "Recovered_",
              "Regression_", "Viewer_")
SCHEMA = "THESIS_INTEGRATED_REPOSITORY_AUDIT_V1"


def classify_file(path: str) -> str:
    """Classify every tracked entry without mistaking a snapshot for active code."""
    if "/" not in path and path.endswith(".py"):
        return "ACTIVE_ROOT_LAUNCHER_OR_HELPER"
    top = path.split("/", 1)[0]
    if top in ACTIVE_TOP and path.endswith(".py"):
        return "ACTIVE_SOURCE_OR_TEST"
    if path.startswith(HISTORICAL):
        return "ARCHIVE_OR_RESEARCH_SNAPSHOT_METADATA_ONLY"
    if path.startswith(("docs/", "LITERATURE/", "KNOWLEDGE_BASE/")):
        return "DOCUMENTATION_OR_LITERATURE_METADATA_ONLY"
    if path.startswith((".github/", "engineering/", "REVIEW_MAIN/")):
        return "GOVERNANCE_OR_WORKFLOW_METADATA_ONLY"
    return "OTHER_TRACKED_FILE_METADATA_ONLY"


def as_module(rel: str) -> str | None:
    if not rel.endswith(".py"):
        return None
    parts = Path(rel).with_suffix("").parts
    if any(not part.isidentifier() for part in parts):
        return None
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else None


def import_graph(root: Path, source_entries: list[dict]) -> dict:
    """Inspect direct Python import references without importing any module.

    'Unresolved' is an inspection candidate, not automatically a runtime bug:
    optional generated plugins, conditional imports and namespace packages exist.
    """
    paths = {entry["path"] for entry in source_entries}
    module_to_path = {
        module: rel for rel in paths
        if (module := as_module(rel)) is not None
    }
    roots = {name for name in ACTIVE_TOP}
    edges: set[tuple[str, str]] = set()
    eager_edges: set[tuple[str, str]] = set()
    deferred_edges: set[tuple[str, str]] = set()
    unresolved = []
    dynamic = []
    parse_skipped = []
    for entry in source_entries:
        rel = entry["path"]
        if entry["parse_status"] != "OK":
            parse_skipped.append(rel)
            continue
        source = root / rel
        try:
            parsed = ast.parse(source.read_text(encoding="utf-8-sig"))
        except (UnicodeError, OSError, SyntaxError):
            parse_skipped.append(rel)
            continue
        current = as_module(rel)
        package = (current.split(".")[:-1]
                   if current and Path(rel).name != "__init__.py"
                   else current.split(".") if current else [])
        parent = {child: node for node in ast.walk(parsed)
                  for child in ast.iter_child_nodes(node)}

        def is_deferred(node):
            ancestor = parent.get(node)
            while ancestor is not None:
                if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef,
                                         ast.Lambda)):
                    return True
                ancestor = parent.get(ancestor)
            return False

        for node in ast.walk(parsed):
            if isinstance(node, ast.Import):
                requests = [(alias.name, node.lineno) for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    if node.level > len(package):
                        unresolved.append({"source": rel, "line": node.lineno,
                                           "import": "." * node.level + (node.module or ""),
                                           "reason": "RELATIVE_IMPORT_ABOVE_PACKAGE"})
                        continue
                    base = package[:len(package) - node.level + 1]
                    name = ".".join([*base, *([node.module] if node.module else [])])
                else:
                    name = node.module or ""
                # 'from package import name' may import a symbol rather than a
                # submodule; inspect only its explicitly stated module target.
                requests = [(name, node.lineno)] if name else []
            elif isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else (
                    node.func.attr if isinstance(node.func, ast.Attribute) else "")
                if name in ("__import__", "import_module"):
                    dynamic.append({"source": rel, "line": node.lineno,
                                    "kind": "DYNAMIC_IMPORT_REVIEW"})
                continue
            else:
                continue
            for name, line in requests:
                if name.split(".", 1)[0] not in roots:
                    continue
                target = module_to_path.get(name)
                if target is None:
                    # Some packages omit __init__.py; a present child is an
                    # implicit namespace package, not a missing import.
                    candidate = root / name.replace(".", "/")
                    if candidate.is_dir() and any(candidate.glob("*.py")):
                        continue
                    # 'from components import thing' may use a symbol from an
                    # __init__ module; only flag explicit multi-part imports.
                    if "." in name:
                        unresolved.append({"source": rel, "line": line,
                                           "import": name,
                                           "reason": "NO_TRACKED_LOCAL_MODULE"})
                elif current and target != rel:
                    edge = (rel, target)
                    edges.add(edge)
                    (deferred_edges if is_deferred(node) else eager_edges).add(edge)

    def cyclic_groups(selected_edges):
        # Strongly connected components of the selected directed graph.
        adjacent = defaultdict(set)
        for origin, target in selected_edges:
            adjacent[origin].add(target)
        order = 0
        index, low, stack, onstack, cycles = {}, {}, [], set(), []

        def visit(node):
            nonlocal order
            index[node] = order
            low[node] = order
            order += 1
            stack.append(node)
            onstack.add(node)
            for child in sorted(adjacent[node]):
                if child not in index:
                    visit(child)
                    low[node] = min(low[node], low[child])
                elif child in onstack:
                    low[node] = min(low[node], index[child])
            if low[node] == index[node]:
                group = []
                while True:
                    child = stack.pop()
                    onstack.remove(child)
                    group.append(child)
                    if child == node:
                        break
                if len(group) > 1:
                    cycles.append(sorted(group))

        for node in sorted({part for edge in selected_edges for part in edge}):
            if node not in index:
                visit(node)
        return sorted(cycles)

    return {
        "source_modules_with_imports_checked": len(source_entries) - len(parse_skipped),
        "direct_local_edges": [{"from": a, "to": b} for a, b in sorted(edges)],
        "potential_import_cycles": cyclic_groups(edges),
        "eager_import_cycles": cyclic_groups(eager_edges),
        "eager_import_edges": len(eager_edges),
        "deferred_import_edges": len(deferred_edges),
        "unresolved_explicit_local_imports": sorted(
            unresolved, key=lambda x: (x["source"], x["line"], x["import"])),
        "dynamic_import_review": sorted(
            dynamic, key=lambda x: (x["source"], x["line"])),
        "source_files_unparsed": sorted(set(parse_skipped)),
        "limitations": [
            "Relative and local dotted imports are checked statically; generated/optional modules can create false positives.",
            "Reflection, plugin registration, GUI callbacks and import-time behavior are not executed.",
            "Import edges alone cannot establish numerical model correctness or performance.",
        ],
    }


def audit(root: Path) -> dict:
    root = Path(root).resolve(strict=True)
    paths = tracked_paths(root)
    source = inventory(root)
    writers = scan_source(root)
    secret_candidates, secret_skipped = security_audit(root)
    source_entries = source["active_python_modules"]
    source_by_path = {item["path"]: item for item in source_entries}
    missing_src_guides = sorted(item["path"] for item in source_entries
        if item["path"].startswith("src/") and not
        (root / "docs" / "source" / (item["path"] + ".md")).is_file())
    by_kind = Counter()
    file_register = []
    for rel in paths:
        kind = classify_file(rel)
        by_kind[kind] += 1
        entry = source_by_path.get(rel)
        if entry:
            state = ("STATIC_PARSED_NOT_SEMANTICALLY_REVIEWED"
                     if entry["parse_status"] == "OK"
                     else "BLOCKED_SOURCE_PARSE_OR_READ")
        else:
            state = "METADATA_INVENTORIED_NOT_SEMANTICALLY_REVIEWED"
        file_register.append({
            "path": rel, "classification": kind, "audit_state": state,
            "parse_status": entry["parse_status"] if entry else "NOT_APPLICABLE",
        })
    graph = import_graph(root, source_entries)
    findings = []
    if secret_candidates:
        findings.append({"id": "P0_PUBLIC_TREE_SECRET_CANDIDATES",
                         "priority": "P0", "status": "REVIEW_REQUIRED",
                         "count": len(secret_candidates),
                         "evidence": [dict(path=path, line=line, category=category)
                                      for path, line, category in secret_candidates][:25],
                         "gate": "Privately inspect/rotate confirmed secrets; audit Git history separately."})
    if source["syntax_errors"]:
        findings.append({"id": "P0_SOURCE_PARSE_OR_READ",
                         "priority": "P0", "status": "CONFIRMED",
                         "count": len(source["syntax_errors"]),
                         "evidence": [x["path"] for x in source["syntax_errors"]][:30],
                         "gate": "Fix or explicitly exclude each invalid active source."})
    if source["canonical_missing"]:
        findings.append({"id": "P0_MISSING_CANONICAL_LAUNCHER",
                         "priority": "P0", "status": "CONFIRMED",
                         "count": len(source["canonical_missing"]),
                         "evidence": source["canonical_missing"],
                         "gate": "Restore required entry point and run launcher regression."})
    if missing_src_guides:
        findings.append({"id": "P2_SRC_SOURCE_GUIDES_MISSING",
                         "priority": "P2", "status": "REVIEW_REQUIRED",
                         "count": len(missing_src_guides),
                         "evidence": missing_src_guides,
                         "gate": "Document actual opt-in architecture, dependencies, boundaries, and source/test status."})
    if graph["unresolved_explicit_local_imports"]:
        findings.append({"id": "P1_UNRESOLVED_IMPORT_CANDIDATES",
                         "priority": "P1", "status": "REVIEW_REQUIRED",
                         "count": len(graph["unresolved_explicit_local_imports"]),
                         "evidence": graph["unresolved_explicit_local_imports"][:25],
                         "gate": "Trace actual imports and conditional/generated module cases."})
    legacy = writers["totals"]["legacy_literal_occurrences"]
    if legacy:
        findings.append({"id": "P1_LEGACY_OUTPUT_REFERENCE_MIGRATION",
                         "priority": "P1", "status": "REVIEW_REQUIRED",
                         "count": legacy,
                         "evidence": writers["top_legacy_candidates"][:12],
                         "gate": "Migrate producer plus all consumers with native regression."})
    if graph["potential_import_cycles"]:
        findings.append({"id": "P1_STATIC_LOCAL_IMPORT_CYCLES",
                         "priority": "P1", "status": "REVIEW_REQUIRED",
                         "count": len(graph["potential_import_cycles"]),
                         "evidence": {
                             "all_potential": graph["potential_import_cycles"][:25],
                             "eager_only": graph["eager_import_cycles"][:25],
                         },
                         "gate": "Distinguish top-level import initialization from deferred function/GUI imports. Verify native import order before refactoring."})
    if writers["parse_errors"]:
        findings.append({"id": "P0_OUTPUT_WRITER_SCAN_INCOMPLETE",
                         "priority": "P0", "status": "CONFIRMED",
                         "count": len(writers["parse_errors"]),
                         "evidence": writers["parse_errors"][:25],
                         "gate": "Restore a complete AST writer scan."})
    findings.extend([
        {"id": "P0_GRAVITY_SUPPORT_EQUIVALENCE", "priority": "P0",
         "status": "NATIVE_EVIDENCE_REQUIRED",
         "evidence": "engineering/rules/ENGINEERING_GATES.md",
         "gate": "Original 32 reaction-bearing joints; 76/97 mesh sensitivity; ETABS source reactions and mass/weights."},
        {"id": "P0_NLTHA_X_WALL_FIRST_STEP", "priority": "P0",
         "status": "NATIVE_EVIDENCE_REQUIRED",
         "evidence": "engineering/rules/ENGINEERING_GATES.md",
         "gate": "Isolated ZERO/X/Y and full-model material/local-force diagnostics with preserved model SHA."},
        {"id": "P1_NBC_ESM_MRSM_EQUIVALENCE", "priority": "P1",
         "status": "NATIVE_EVIDENCE_REQUIRED",
         "evidence": "engineering/rules/ENGINEERING_GATES.md",
         "gate": "Original Excel Aw/T1 and EDB SHA; ULS/SLS mass, drift, base/shear scaling, PDelta."},
    ])
    return {
        "schema": SCHEMA, "created_utc": datetime.now(timezone.utc).isoformat(),
        "assessment": "TRACKED_FILE_AND_ACTIVE_SOURCE_STATIC_ONLY_NOT_FULL_CODE_REVIEW",
        "tracked_file_count": len(paths),
        "tracked_classification_counts": dict(sorted(by_kind.items())),
        "active_python_count": len(source_entries),
        "active_source_parse_failures": source["syntax_errors"],
        "missing_src_source_guides": missing_src_guides,
        "canonical_missing": source["canonical_missing"],
        "numbered_launcher_aliases": source["numbered_alias_conflicts"],
        "writer_scan_totals": writers["totals"],
        "writer_parse_failures": writers["parse_errors"],
        "tracked_secret_candidate_count": len(secret_candidates),
        "secret_scan_skipped_binary_or_oversized_count": len(secret_skipped),
        "dependency_graph": graph,
        "findings": findings,
        "file_register": file_register,
        "acceptance": {
            "static_audit": "PASS" if not source["syntax_errors"]
                and not source["canonical_missing"] and not writers["parse_errors"]
                else "BLOCKED",
            "import_semantics": "REVIEW_REQUIRED",
            "source_guide_semantics": "NOT_REVIEWED",
            "windows_spyder_gui": "NOT_VERIFIED",
            "etabs_opensees_equivalence": "NOT_VERIFIED",
            "nonlinear_full_record": "NOT_VERIFIED",
            "nbc_105_2025_compliance": "NOT_VERIFIED",
        },
        "limitations": [
            "All tracked paths are inventoried but not all 3000+ files are semantically reviewed.",
            "Active code AST/compile/import scans do not execute models or catch every bug.",
            "Archived snapshots, documentation and binary assets are metadata-classified only.",
            "Full ETABS export, native OpenSees and GUI runs require user-side Windows evidence.",
            "Static writer occurrences are candidates, not proven write operations or load-path errors.",
            "Secret pattern scan covers current tracked text only, not Git history, encrypted/binary content or GitHub-side alerts.",
        ],
    }


def save(report: dict, directory: Path) -> tuple[Path, Path]:
    """Create a stable review package with per-subject outputs, no source mutation.

    Files contain tracked relative paths and summary observations only; user
    EDB/XLSX contents, actual secret values and native solver inputs stay out.
    """
    directory.mkdir(parents=True, exist_ok=True)
    summary = directory / "00_OVERVIEW" / "integrated_audit.json"
    register = directory / "01_TRACKED_FILES" / "tracked_file_register.csv"
    pieces = (
        (directory / "02_DEPENDENCIES" / "import_graph.json",
         report["dependency_graph"]),
        (directory / "03_FINDINGS" / "consolidated_findings.json",
         {"schema": report["schema"], "findings": report["findings"]}),
        (directory / "04_ACCEPTANCE" / "acceptance_gates.json",
         {"schema": report["schema"], "acceptance": report["acceptance"],
          "limitations": report["limitations"]}),
        (directory / "05_OUTPUT_WRITERS" / "writer_summary.json",
         {"schema": report["schema"], "totals": report["writer_scan_totals"],
          "parse_failures": report["writer_parse_failures"]}),
        (directory / "06_SECURITY" / "secret_scan_summary.json",
         {"schema": report["schema"],
          "current_tree_candidate_count": report["tracked_secret_candidate_count"],
          "skipped_binary_or_oversized_count":
              report["secret_scan_skipped_binary_or_oversized_count"],
          "status": "CURRENT_TRACKED_TREE_PATTERN_SCAN_ONLY"}),
    )
    summary.parent.mkdir(parents=True, exist_ok=True)
    register.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    with register.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=("path", "classification", "audit_state", "parse_status"))
        writer.writeheader()
        writer.writerows(report["file_register"])
    for target, data in pieces:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
    (directory / "README.md").write_text(
        "# Static repository audit evidence (not native engineering approval)\n\n"
        "00_OVERVIEW/ — complete integrated JSON, including tracked file register\n"
        "01_TRACKED_FILES/ — one-row-per-tracked-file CSV\n"
        "02_DEPENDENCIES/ — active local import graph and unresolved candidates\n"
        "03_FINDINGS/ — prioritized issues and review obligations\n"
        "04_ACCEPTANCE/ — distinct static and native engineering gates\n"
        "05_OUTPUT_WRITERS/ — potential write calls and legacy reference counts\n"
        "06_SECURITY/ — redacted current-tree pattern-scan summary\n\n"
        "A passing static gate is NOT ETABS/OpenSees equivalence, NBC code "
        "acceptance or a full line-by-line semantic review.\n",
        encoding="utf-8")
    return summary, register


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path,
                        default=Path("audit/integrated"))
    parser.add_argument("--fail-on-static-blockers", action="store_true")
    args = parser.parse_args(argv)
    result = audit(args.repo)
    summary, register = save(result, args.output)
    print(json.dumps({
        "assessment": result["assessment"],
        "tracked_file_count": result["tracked_file_count"],
        "active_python_count": result["active_python_count"],
        "static_gate": result["acceptance"]["static_audit"],
        "unresolved_local_import_candidates": len(
            result["dependency_graph"]["unresolved_explicit_local_imports"]),
        "writer_occurrences": result["writer_scan_totals"],
        "finding_ids": [x["id"] for x in result["findings"]],
        "report": str(summary), "file_register": str(register),
    }, indent=2))
    return (2 if args.fail_on_static_blockers
            and result["acceptance"]["static_audit"] != "PASS" else 0)


if __name__ == "__main__":
    raise SystemExit(main())
