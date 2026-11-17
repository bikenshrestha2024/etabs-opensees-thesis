"""Repository-wide tracked-file provenance, Python dependencies and semantic triage.

[REF docs/source/tools/audit_repository_semantics.py.md]
This is static evidence collection. It is NOT native ETABS/OpenSees analysis,
NBC 105:2025 acceptance, software security certification, or a complete
human line-by-line code review. No source files are moved or executed.

    python tools/audit_repository_semantics.py --output audit/repository_semantics.json
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = (
    "Saved_Project_", "Worked_Example_", "Verification_", "archive/",
    "Research_Components/", "Recovered_", "Regression_", "Viewer_",
    "Reproducibility_Checks_", "Diagnostic_Evidence/",
    "Calibration_Steel02/", "Material_Validation_Results_",
    "Wall_Validation_", "Input_Records_",
)
RUNTIME_DIRS = frozenset(("components", "src", "tools"))
ANALYSIS_DIRS = frozenset(("tests",))
# The root python launcher and named runtime facades remain active even if a
# versioned snapshot of a similar name exists elsewhere.
SCOPE = "STATIC_REPOSITORY_DEPENDENCY_AND_RISK_TRIAGE_NOT_NATIVE_ENGINEERING_VALIDATION"


def tracked_entries(root: Path) -> list[dict]:
    """[REF docs/source/tools/audit_repository_semantics.py.md] Git index, not user files."""
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "-z"],
        capture_output=True, check=True)
    entries = []
    for item in proc.stdout.split(b"\0"):
        if not item:
            continue
        metadata, path_bytes = item.split(b"\t", 1)
        mode, blob, stage = metadata.decode("ascii").split()
        if stage != "0":
            # Active index conflicts are never a clean audit.
            raise ValueError("Unmerged Git index entry")
        rel = path_bytes.decode("utf-8", "surrogateescape")
        entries.append(dict(path=rel, mode=mode, git_blob_sha=blob))
    return sorted(entries, key=lambda x: x["path"])


def category(path: str) -> str:
    """[REF docs/source/tools/audit_repository_semantics.py.md] File role."""
    if path.startswith(HISTORICAL):
        return "HISTORICAL_SNAPSHOT"
    if not path.endswith(".py"):
        return "TRACKED_NONPYTHON"
    if "/" not in path:
        return "ACTIVE_RUNTIME"
    first = path.partition("/")[0]
    if first in RUNTIME_DIRS:
        return "ACTIVE_RUNTIME"
    if first in ANALYSIS_DIRS:
        return "TEST"
    return "OTHER_PYTHON_PROVENANCE"


def _module_name(path: str) -> str:
    name = path[:-3].replace("/", ".")
    return name[:-9] if name.endswith(".__init__") else name


def _read_python(path: Path):
    if path.is_symlink() or not path.is_file():
        raise OSError("Linked or missing tracked Python source")
    raw = path.read_bytes()
    source = raw.decode("utf-8-sig", "strict")
    tree = ast.parse(source, filename=path.as_posix())
    compile(tree, path.as_posix(), "exec", dont_inherit=True)
    return tree, hashlib.sha256(raw).hexdigest(), len(source.splitlines())


def _calls(tree, path, candidates):
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            body = [x for x in node.body if not (
                isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant)
                and isinstance(x.value.value, str))]
            if body and all(isinstance(x, ast.Pass) for x in body):
                candidates.append(dict(path=path, line=node.lineno,
                    code="SWALLOWED_EXCEPTION", priority="REVIEW",
                    note="Except handler contains only pass; check failure propagation"))
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            called = node.func.id
        elif isinstance(node.func, ast.Attribute):
            called = node.func.attr
        else:
            called = ""
        if called in {"eval", "exec"} and isinstance(node.func, ast.Name):
            candidates.append(dict(path=path, line=node.lineno,
                code="DYNAMIC_EXECUTION", priority="REVIEW",
                note="Review caller trust boundary and inputs; no exploit inferred"))
        if called in ("run", "Popen", "call", "check_output", "check_call"):
            if any(k.arg == "shell" and isinstance(k.value, ast.Constant)
                   and k.value.value is True for k in node.keywords):
                candidates.append(dict(path=path, line=node.lineno,
                    code="SHELL_TRUE_SUBPROCESS", priority="REVIEW",
                    note="Inspect argument provenance; shell invocation may be intended"))


def _imports(tree):
    """[REF docs/source/tools/audit_repository_semantics.py.md] Nested import graph."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((alias.name, node.lineno, "direct", 0)
                           for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((node.module, node.lineno, "from", node.level))
            # 'from package import symbol' cannot prove symbol is a module.
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == "__import__":
                typ = "literal_dynamic"
            elif (isinstance(fn, ast.Attribute)
                  and fn.attr == "import_module"
                  and isinstance(fn.value, ast.Name)
                  and fn.value.id == "importlib"):
                typ = "literal_dynamic"
            else:
                continue
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(
                    node.args[0].value, str):
                imports.append((node.args[0].value, node.lineno, typ, 0))
    return imports


def _resolve_import(source_module, imported, level, modules, namespace_heads,
                    *, is_package_init=False):
    if level:
        components = source_module.split(".")
        # A package __init__.py denotes the package itself, not a child module.
        parent = components if is_package_init else components[:-1]
        up = level - 1
        if up > len(parent):
            return None, "BAD_RELATIVE_IMPORT"
        prefix = parent[:len(parent)-up] if up else parent
        imported = ".".join(prefix + ([imported] if imported else []))
    if not imported:
        return None, "AMBIGUOUS"
    if imported in modules:
        return modules[imported], "RESOLVED"
    # Python 3 namespace packages may have no __init__.py. The caller
    # can legitimately import their root package without a local .py.
    if imported in namespace_heads:
        return None, "NAMESPACE_PACKAGE"
    first = imported.split(".")[0]
    if first not in namespace_heads:
        return None, "EXTERNAL"
    # Dynamic modules that are descendants of a known package are unresolved.
    return None, "MISSING_LOCAL"


def audit_repository(root: Path = DEFAULT_ROOT) -> dict:
    """[REF docs/source/tools/audit_repository_semantics.py.md] Reproducible tracked audit."""
    root = Path(root).resolve()
    entries = tracked_entries(root)
    modules = {
        _module_name(item["path"]): item["path"]
        for item in entries
        if item["path"].endswith(".py") and
        category(item["path"]) in ("ACTIVE_RUNTIME", "TEST")
    }
    namespace_heads = set(RUNTIME_DIRS | ANALYSIS_DIRS)
    namespace_heads.update(name for name in modules if "." not in name)
    # Namespace packages are importable without __init__.py (PEP 420).
    # Every parent directory containing tracked active/test Python belongs
    # to the local Python package path, but a nonexistent child does not.
    for name in modules:
        parts=name.split(".")
        namespace_heads.update(".".join(parts[:i])
                               for i in range(1,len(parts)))
    runtime, errors, edges, missing, candidates = [], [], [], [], []
    tops, groups = Counter(), Counter()
    for item in entries:
        path = item["path"]
        role = category(path)
        item["category"] = role
        top = path.partition("/")[0]
        tops[top] += 1
        groups[role] += 1
        if role not in ("ACTIVE_RUNTIME", "TEST"):
            continue
        mod = _module_name(path)
        try:
            tree, sha256, count = _read_python(root / path)
        except (OSError, UnicodeError, SyntaxError, ValueError) as exc:
            errors.append(dict(path=path, code="ACTIVE_SOURCE_INVALID",
                               error_type=type(exc).__name__,
                               line=getattr(exc, "lineno", None)))
            runtime.append(dict(path=path, sha256=None, line_count=None,
                                parse_status="ERROR"))
            continue
        runtime.append(dict(path=path, sha256=sha256, line_count=count,
                            parse_status="OK"))
        _calls(tree, path, candidates)
        seen = set()
        for imported, line, kind, level in _imports(tree):
            key = (imported, line, kind, level)
            if key in seen:
                continue
            seen.add(key)
            target, reason = _resolve_import(
                mod, imported, level, modules, namespace_heads,
                is_package_init=path.endswith("/__init__.py"))
            if reason == "RESOLVED":
                if target != path:
                    edges.append(dict(source=path, target=target,
                                      line=line, kind=kind))
            elif reason in ("MISSING_LOCAL", "BAD_RELATIVE_IMPORT"):
                missing.append(dict(source=path, imported=imported, line=line,
                                    kind=kind, reason=reason))
    # Do not allow CI to confuse advisory code patterns with confirmed errors.
    errors.sort(key=lambda x: (x["path"], x.get("line") or 0))
    missing.sort(key=lambda x: (x["source"], x["line"], x["imported"]))
    edges.sort(key=lambda x: (x["source"], x["target"], x["line"]))
    candidates.sort(key=lambda x: (x["path"], x["line"], x["code"]))
    return dict(
        schema="THESIS_REPOSITORY_SEMANTIC_DISCOVERY_V1",
        scope=SCOPE,
        status=("BLOCKED_STATIC" if errors or missing else "STATIC_TRIAGE_ONLY"),
        summary=dict(tracked_files=len(entries),
                     runtime_python=groups["ACTIVE_RUNTIME"],
                     test_python=groups["TEST"],
                     historical_files=groups["HISTORICAL_SNAPSHOT"],
                     nonpython_files=groups["TRACKED_NONPYTHON"],
                     other_python=groups["OTHER_PYTHON_PROVENANCE"],
                     active_errors=len(errors),
                     unresolved_local_imports=len(missing),
                     local_dependency_edges=len(edges),
                     review_candidates=len(candidates)),
        top_level_counts=dict(sorted(tops.items())),
        tracked_files=entries,
        active_python=runtime,
        active_source_errors=errors,
        unresolved_local_dependencies=missing,
        local_dependency_edges=edges,
        review_candidates=candidates,
        engineering_gates={
            "G0_TRACKED_TREE": "COVERED_BY_GIT_INDEX_NOT_PRIVATE_LOCAL_FILES",
            "G1_STATIC": "PASS" if not errors and not missing else "FAIL",
            "G2_GUI_EXPORT_INTEGRATION": "REQUIRES_RUNTIME_TESTS",
            "G3_GRAVITY_32_76_97": "UNVERIFIED_NATIVE_ETABS_OPENSEES",
            "G4_NBC_DYNAMIC_AND_NONLINEAR": "UNVERIFIED_NATIVE_SOLVER",
            "G5_PUBLIC_OUTPUT_SECURITY": "REQUIRES_SEPARATE_CONTENT_SCAN",
            "G6_THESIS_ACCEPTANCE": "NOT_A_STRUCTURAL_CERTIFICATE"
        },
        limitations=[
            "AST import graph includes function-local and literal dynamic imports but "
            "does not prove lazy UI callback or native DLL behavior.",
            "From-package imported names may be attributes rather than modules; "
            "they are not called missing module errors.",
            "An absent module may be an intentionally optional plugin. Review "
            "each unresolved import before classifying a production defect.",
            "Historical snapshots retain Git blob IDs only: no runtime parsing "
            "or automatic moving/deleting/renaming of historical evidence.",
            "Review candidates are heuristics, not confirmed security bugs.",
            "No native ETABS/OpenSees, gravity reaction, modal, ESM, MRSM, LTHA "
            "or NLTHA numerical comparison was executed."
        ]
    )


def main(argv=None):
    """[REF docs/source/tools/audit_repository_semantics.py.md] CLI gate."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path,
                        default=Path("audit/repository_semantics.json"))
    parser.add_argument("--fail-on-active-errors", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    report = audit_repository(root)
    path = args.output if args.output.is_absolute() else root / args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False)
                    + "\n", encoding="utf-8")
    print(json.dumps(dict(status=report["status"],
                          summary=report["summary"],
                          unresolved_local_dependencies=report[
                              "unresolved_local_dependencies"][:30],
                          active_source_errors=report["active_source_errors"][:20]),
                     indent=2))
    return 1 if (args.fail_on_active_errors and
                 (report["active_source_errors"]
                  or report["unresolved_local_dependencies"])) else 0


if __name__ == "__main__":
    raise SystemExit(main())
