"""Read-only AST inventory of possible live output writers and legacy paths.

This is NOT a code-compliance check, a native ETABS/OpenSees run, or proof
that a function writes any particular file. A syntax-only static inventory is
meant to guide manual writer/reader migration across a large repository.

Usage:
  python tools/audit_live_output_writers.py --repo .
  python tools/audit_live_output_writers.py --repo . --export "D:\\Thesis Opensees\\ETABS 11-14-2026\\3" --write
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Direct `python tools/...py` execution must resolve the repository packages,
# including when invoked from another working directory on Windows.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

LEGACY_MARKERS = (
    "opensees_analysis_results", "06_linear_th", "07_nonlinear_th",
    "gravity_reaction_diagnostic", "esm_runner_status",
    "organized_results", "design_checks_v135",
)
CANONICAL_MARKERS = (
    "01_etabs_export", "02_model", "02_gravity", "03_esm",
    "04_modal", "05_mrsm", "06_linear_time_history",
    "07_nonlinear_time_history", "08_etabs_comparisons",
    "09_software_diagnostics", "90_upload_packages",
)
WRITE_METHODS = frozenset({
    "write_text", "write_bytes", "mkdir", "save", "savefig",
    "to_excel", "to_csv", "to_json", "dump",
    "writestr", "write", "copyfile", "copy2", "replace",
})
# Potential readers need to be paired with producers during migration;
# this is a conservative AST search, not proof of a runtime file dependency.
READ_METHODS = frozenset({
    "read_text", "read_bytes", "read_csv", "read_excel", "read_json",
    "load_workbook", "loadtxt", "genfromtxt", "read_parquet",
    "read_pickle", "from_json", "load",
})
ROOT_SCRIPTS = (".py",)
SOURCE_FOLDERS = ("components", "src", "tools")


def source_files(repo):
    """Enumerate active Python source; exclude tests, history and generated caches."""
    repo = Path(repo).resolve(strict=True)
    for path in sorted(repo.glob("*.py")):
        if path.is_file() and not path.is_symlink():
            yield path
    for folder in SOURCE_FOLDERS:
        base = repo / folder
        if not base.is_dir() or base.is_symlink():
            continue
        for path in sorted(base.rglob("*.py")):
            if (path.is_file() and not path.is_symlink()
                    and not any(part in ("__pycache__", ".pytest_cache")
                                for part in path.parts)):
                yield path


def _text_literal(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(piece.value for piece in node.values
                       if isinstance(piece, ast.Constant)
                       and isinstance(piece.value, str))
    return ""


def scan_source(repo):
    """Parse potential writes and literal path markers, never execute the code."""
    root = Path(repo).resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    records = []
    problems = []
    totals = {"files": 0, "possible_write_calls": 0,
              "legacy_literal_occurrences": 0, "canonical_literal_occurrences": 0,
              "legacy_docstring_occurrences": 0,
              "legacy_executable_literal_occurrences": 0,
              "possible_read_calls": 0}
    for path in source_files(root):
        rel = path.relative_to(root).as_posix()
        totals["files"] += 1
        try:
            source = path.read_text(encoding="utf-8-sig")
            tree = ast.parse(source, filename=rel)
        except (UnicodeError, OSError, SyntaxError) as exc:
            problems.append({"path": rel, "error": type(exc).__name__,
                             "line": getattr(exc, "lineno", None)})
            continue
        # Distinguish descriptive docstrings from literals present in code.
        # Neither proves an executed writer, but counting documentation as
        # an operational migration target hides the meaningful review queue.
        docstrings=set()
        for owner in ast.walk(tree):
            if isinstance(owner,(ast.Module,ast.ClassDef,
                                 ast.FunctionDef,ast.AsyncFunctionDef)):
                if (owner.body and isinstance(owner.body[0],ast.Expr)
                    and isinstance(owner.body[0].value,ast.Constant)
                    and isinstance(owner.body[0].value.value,str)):
                    docstrings.add(id(owner.body[0].value))
        occurrences = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                value = _text_literal(node).casefold()
                if not value:
                    continue
                legacy = sorted(m for m in LEGACY_MARKERS if m in value)
                canonical = sorted(m for m in CANONICAL_MARKERS if m in value)
                if legacy or canonical:
                    context=("DOCSTRING_REFERENCE" if id(node) in docstrings
                             else "CODE_LITERAL_REVIEW")
                    occurrences.append({
                        "line": getattr(node, "lineno", 0),
                        "kind": "LITERAL_PATH_MARKER",
                        "markers": legacy + canonical,
                        "legacy": bool(legacy),
                        "literal_context": context,
                    })
                    totals["legacy_literal_occurrences"] += len(legacy)
                    totals[("legacy_docstring_occurrences" if
                            context=="DOCSTRING_REFERENCE" else
                            "legacy_executable_literal_occurrences")]+=len(legacy)
                    totals["canonical_literal_occurrences"] += len(canonical)
            elif isinstance(node, ast.Call):
                func = node.func
                method = (func.attr if isinstance(func, ast.Attribute)
                          else func.id if isinstance(func, ast.Name) else "")
                if method in READ_METHODS:
                    occurrences.append({
                        "line": getattr(node, "lineno", 0),
                        "kind": "POTENTIAL_READ_CALL",
                        "method": method,
                    })
                    totals["possible_read_calls"] += 1
                    continue
                if method not in WRITE_METHODS and method != "open":
                    continue
                mode_status = None
                if method == "open":
                    # Builtin open(path, mode) and Path.open(mode) place their
                    # positional mode arguments at different indices.
                    positional_index = (0 if isinstance(func, ast.Attribute) else 1)
                    mode_node = (node.args[positional_index]
                                 if len(node.args) > positional_index else None)
                    keyword_modes = [k.value for k in node.keywords if k.arg == "mode"]
                    if keyword_modes:
                        mode_node = keyword_modes[-1]
                    if mode_node is None:
                        mode = "r"  # Both open APIs default to a read-only mode.
                        mode_status = "DEFAULT_READ_ONLY"
                    elif isinstance(mode_node, ast.Constant) and isinstance(mode_node.value, str):
                        mode = mode_node.value
                        mode_status = "STATIC_MODE"
                    else:
                        # A dynamic mode must be examined, not silently
                        # classified as read-only and omitted from the audit.
                        mode = ""
                        mode_status = "DYNAMIC_MODE_REVIEW_REQUIRED"
                    if mode_status != "DYNAMIC_MODE_REVIEW_REQUIRED":
                        if not any(flag in mode for flag in "wax+"):
                            occurrences.append({
                                "line": getattr(node, "lineno", 0),
                                "kind": "POTENTIAL_READ_CALL",
                                "method": "open",
                                "mode_classification": mode_status,
                            })
                            totals["possible_read_calls"] += 1
                            continue
                occurrence = {
                    "line": getattr(node, "lineno", 0),
                    "kind": "POTENTIAL_WRITE_CALL",
                    "method": method,
                }
                if mode_status is not None:
                    occurrence["mode_classification"] = mode_status
                occurrences.append(occurrence)
                totals["possible_write_calls"] += 1
        if occurrences:
            records.append({
                "source": rel,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "occurrences": sorted(occurrences, key=lambda x: (x["line"], x["kind"])),
            })
    candidates = []
    for item in records:
        legacy_lines = [ref["line"] for ref in item["occurrences"]
                        if ref["kind"] == "LITERAL_PATH_MARKER"
                        and ref.get("legacy")]
        if legacy_lines:
            executable = [ref for ref in item["occurrences"]
                          if ref["kind"]=="LITERAL_PATH_MARKER"
                          and ref.get("legacy") and
                          ref.get("literal_context")=="CODE_LITERAL_REVIEW"]
            candidates.append({
                "source": item["source"], "legacy_markers": len(legacy_lines),
                "legacy_executable_markers":len(executable),
                "legacy_docstring_markers":len(legacy_lines)-len(executable),
                "first_lines": legacy_lines[:8],
                "potential_write_calls": sum(
                    ref["kind"] == "POTENTIAL_WRITE_CALL"
                    for ref in item["occurrences"]),
                "classification": ("DOCUMENTATION_ONLY_STATIC_REFERENCE"
                    if not executable else "REVIEW_ONLY_CALLER_READER_TRACE_REQUIRED"),
            })
    candidates.sort(key=lambda item: (-item["legacy_executable_markers"],
                                      -item["legacy_markers"], item["source"]))
    return {
        "schema": "THESIS_STATIC_OUTPUT_WRITER_AUDIT_V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "assessment": "STATIC_SOURCE_REVIEW_ONLY_NOT_EXECUTED_WRITER_OR_ETABS_EQUIVALENCE",
        "repository": str(root),
        "totals": totals,
        "files": records,
        "top_legacy_candidates": candidates[:25],
        "reader_writer_files": sorted([
            {"source": item["source"],
             "read_calls": sum(x["kind"]=="POTENTIAL_READ_CALL"
                               for x in item["occurrences"]),
             "write_calls": sum(x["kind"]=="POTENTIAL_WRITE_CALL"
                                for x in item["occurrences"]),
             "legacy_markers": sum(x["kind"]=="LITERAL_PATH_MARKER" and
                                  x.get("legacy",False)
                                  for x in item["occurrences"])}
            for item in records
            if any(x["kind"] in ("POTENTIAL_READ_CALL","POTENTIAL_WRITE_CALL")
                   for x in item["occurrences"])
        ], key=lambda row:row["source"]),
        "parse_errors": problems,
        "next_action": "Prioritize live code literals and verified writer/reader pairs; preserve documented legacy read aliases and historical results.",
    }


def save_local_report(report, export_root):
    """Save JSON/CSV/README together under a new canonical diagnostics run."""
    from components.inputs.output_layout import export_root_for
    from components.inputs.output_contract import safe_component
    root = export_root_for(export_root)
    if not root.is_dir():
        raise NotADirectoryError(root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    parent = root / "09_SOFTWARE_DIAGNOSTICS" / "WRITER_AUDITS" / "RUNS"
    if any(p.is_symlink() for p in (
            root / "09_SOFTWARE_DIAGNOSTICS",
            parent.parent, parent)):
        raise ValueError("Refusing linked output audit directory")
    run = parent / safe_component(stamp)
    run.mkdir(parents=True, exist_ok=False)
    for name in ("JSON", "CSV", "REPORT"):
        (run / name).mkdir()
    local = dict(report, repository="<LOCAL_REPOSITORY_PATH>")
    (run / "JSON" / "Writer_Audit.json").write_text(
        json.dumps(local, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (run / "CSV" / "Writer_References.csv").open(
            "w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("Source", "Line", "Kind", "Method", "Markers", "Legacy"))
        for item in report["files"]:
            for ref in item["occurrences"]:
                writer.writerow((item["source"], ref["line"], ref["kind"],
                                 ref.get("method", ""),
                                 ";".join(ref.get("markers", [])),
                                 ref.get("legacy", "")))
    (run / "REPORT" / "READ_FIRST.md").write_text(
        "# Static source writer inventory\n\n"
        "No solver executed. A write call may only be a helper or a diagnostic.\n"
        "Legacy path string may be documentation/compatibility rather than an active writer.\n"
        "Do not move any source EDB, workbook, historical output or solver file "
        "based on this inventory alone. Trace callers, manifests, readers, GUI links "
        "and regression tests before migration.\n", encoding="utf-8")
    return run


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--export", help="Selected ETABS export root for optional local report")
    parser.add_argument("--write", action="store_true",
                        help="Save JSON/CSV/README under canonical diagnostics")
    args = parser.parse_args(argv)
    if args.write and not args.export:
        parser.error("--write requires explicit --export")
    result = scan_source(args.repo)
    print(json.dumps({"assessment": result["assessment"],
                      "totals": result["totals"],
                      "top_legacy_candidates": result["top_legacy_candidates"][:12],
                      "parse_errors": len(result["parse_errors"])}, indent=2))
    if args.write:
        print("Local report:", save_local_report(result, args.export))
    return 0 if not result["parse_errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
