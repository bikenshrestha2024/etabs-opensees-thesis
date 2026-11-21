"""NBC 105:2025 sentence-level normative register: loader, validator and fail-closed gate.

[REF NBC105-2025 normative register, docs/nbc105/NORMATIVE_REGISTER_GUIDE.md]
The register lists every normative unit of the standard (clauses 1 to 10,
Annexes A to C: sentences, equations, tables, table rows, notes, footnotes and
figures) with a source locator, a hash of the normalised unit and exactly one
disposition. This module reads it, checks its structure and reports counts.

It never certifies anything. The gate returns BLOCKED_NOT_CERTIFIED while any
row is unreviewed, UNVERIFIED_GAP, invalid or points at a missing symbol. When
every row is dispositioned it returns REGISTER_REVIEWED_EXTERNAL_GATES_OPEN:
that is a statement about the review of the text, not about any building.
Independent human sign-off, native ETABS/OpenSees evidence and the project
wall and connection designs remain external gates in every case.
"""
from __future__ import annotations

import ast
import csv
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path

__all__ = [
    "REGISTER_COLUMNS", "DISPOSITIONS", "EXTERNAL_GATES", "CLAUSE_ORDER",
    "register_path", "manifest_path", "load_register", "validate_register",
    "summarize_register", "normative_register_gate",
]

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER_DIR = REPO_ROOT / "docs" / "nbc105" / "normative_register"
REGISTER_CSV = REGISTER_DIR / "NORMATIVE_REGISTER.csv"
MANIFEST_JSON = REGISTER_DIR / "EXTRACTION_MANIFEST.json"

REGISTER_COLUMNS = (
    "id", "clause", "subclause", "printed_page", "kind", "locator", "sha256",
    "topic", "inherited_kind", "disposition", "implementation_ref", "test_ref",
    "evidence_note", "finding", "rule",
)
DISPOSITIONS = (
    "IMPLEMENTED_AND_TESTED", "IMPLEMENTED_UNTESTED", "MANUAL_PROJECT_CHECK",
    "PROJECT_NOT_APPLICABLE", "DEFINITION_ONLY", "EXTERNAL_DATA_REQUIRED",
    "UNVERIFIED_GAP",
)
CLAUSE_ORDER = tuple(str(i) for i in range(1, 11)) + ("A", "B", "C")
# Dispositions that still depend on something outside this repository's unit tests.
_OPEN_EXTERNAL = ("MANUAL_PROJECT_CHECK", "EXTERNAL_DATA_REQUIRED", "IMPLEMENTED_UNTESTED")
_NEEDS_NOTE = ("MANUAL_PROJECT_CHECK", "PROJECT_NOT_APPLICABLE",
               "EXTERNAL_DATA_REQUIRED", "UNVERIFIED_GAP")
EXTERNAL_GATES = (
    "INDEPENDENT_HUMAN_SIGNOFF_OF_THE_REGISTER_AND_THE_DESIGN",
    "NATIVE_ETABS_OPENSEES_EVIDENCE",
    "PROJECT_WALL_AND_CONNECTION_DESIGNS",
)
_SHA = re.compile(r"^[0-9a-f]{64}$")


def register_path():
    """Path of the committed register CSV. [REF NBC105-2025 normative register]"""
    return REGISTER_CSV


def manifest_path():
    """Path of the extraction manifest. [REF NBC105-2025 normative register]"""
    return MANIFEST_JSON


def load_register(path=None):
    """Read the register rows as a list of dicts (UTF-8, any line ending).

    [REF NBC105-2025 normative register]
    Raises ValueError when the header is not the expected column set.
    """
    file = REGISTER_CSV if path is None else Path(path)
    with open(file, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REGISTER_COLUMNS:
            raise ValueError("normative register header does not match the expected columns")
        return [dict(row) for row in reader]


def _symbol_names(file, cache):
    """Top-level and nested function, class and assigned names of a Python file (no import)."""
    if file not in cache:
        tree = ast.parse(file.read_text(encoding="utf-8-sig"), filename=str(file))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names.add(node.target.id)
            elif isinstance(node, ast.Assign):
                names.update(t.id for t in node.targets if isinstance(t, ast.Name))
        cache[file] = names
    return cache[file]


def _reference_problem(ref, repo_root, cache):
    """Return a short problem text for one 'path::name' reference, or None when it resolves."""
    path_text, _, name = ref.partition("::")
    posix = Path(path_text.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts:
        return "unsafe path " + path_text
    file = (repo_root / posix).resolve()
    try:
        file.relative_to(repo_root.resolve())
    except ValueError:
        return "path outside repository " + path_text
    if not file.is_file():
        return "missing file " + path_text
    if not name:
        return None
    if file.suffix != ".py":
        return "symbol reference into a non-Python file " + path_text
    try:
        names = _symbol_names(file, cache)
    except SyntaxError:
        return "unparseable file " + path_text
    if not all(part in names for part in name.split(".")):
        return "missing symbol " + ref
    return None


def validate_register(rows, repo_root=None, check_references=True):
    """Structural validation. Returns a dict of problem lists; empty lists mean no finding.

    [REF NBC105-2025 normative register]
    Checks: unique ids, 64-hex hashes, known clause and kind, a disposition on
    every row, a known disposition value, references on implemented rows and a
    note on manual, not-applicable, external and gap rows, and (optionally)
    that every implementation/test reference resolves to a real file and symbol.
    """
    root = Path(repo_root) if repo_root is not None else REPO_ROOT
    problems = OrderedDict((k, []) for k in (
        "duplicate_id", "bad_hash", "unknown_clause", "unreviewed", "invalid_disposition",
        "missing_reference", "missing_note", "unresolved_reference"))
    seen = set()
    cache = {}
    for row in rows:
        rid = row.get("id", "")
        if rid in seen or not rid:
            problems["duplicate_id"].append(rid)
        seen.add(rid)
        if not _SHA.match(row.get("sha256", "")):
            problems["bad_hash"].append(rid)
        if row.get("clause") not in CLAUSE_ORDER:
            problems["unknown_clause"].append(rid)
        disp = (row.get("disposition") or "").strip()
        if not disp:
            problems["unreviewed"].append(rid)
            continue
        if disp not in DISPOSITIONS:
            problems["invalid_disposition"].append(rid)
            continue
        impl = (row.get("implementation_ref") or "").strip()
        test = (row.get("test_ref") or "").strip()
        if disp == "IMPLEMENTED_AND_TESTED" and not (impl and test):
            problems["missing_reference"].append(rid)
        if disp == "IMPLEMENTED_UNTESTED" and not impl:
            problems["missing_reference"].append(rid)
        if disp in _NEEDS_NOTE and not (row.get("evidence_note") or "").strip():
            problems["missing_note"].append(rid)
        if check_references:
            for ref in filter(None, (x.strip() for x in (impl + ";" + test).split(";"))):
                if _reference_problem(ref, root, cache):
                    problems["unresolved_reference"].append(rid + ": " + _reference_problem(ref, root, cache))
                    break
    return dict(problems)


def summarize_register(rows):
    """Counts: total, per disposition, per clause and per clause and disposition.

    [REF NBC105-2025 normative register]
    A blank disposition is counted under the key '(blank)'.
    """
    total = Counter((r.get("disposition") or "").strip() or "(blank)" for r in rows)
    by_clause = OrderedDict()
    for clause in CLAUSE_ORDER:
        sub = [r for r in rows if r.get("clause") == clause]
        counts = Counter((r.get("disposition") or "").strip() or "(blank)" for r in sub)
        by_clause[clause] = {"rows": len(sub), **{k: counts[k] for k in sorted(counts)}}
    return {
        "rows": len(rows),
        "disposition_counts": {k: total[k] for k in sorted(total)},
        "by_clause": by_clause,
        "kind_counts": dict(sorted(Counter(r.get("kind", "") for r in rows).items())),
    }


def _manifest_rows(manifest_file):
    try:
        data = json.loads(Path(manifest_file).read_text(encoding="utf-8"))
        return int(data["rows"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def normative_register_gate(rows=None, repo_root=None, check_references=True):
    """Fail-closed gate over the register. Never returns a certified status.

    [REF NBC105-2025 normative register]
    status BLOCKED_NOT_CERTIFIED: a row is unreviewed or UNVERIFIED_GAP, a row is
    invalid, a reference does not resolve, the register is unreadable, or the row
    count differs from the extraction manifest.
    status REGISTER_REVIEWED_EXTERNAL_GATES_OPEN: every row has a valid
    disposition. 'certified' is False in both cases.
    """
    reasons = []
    problems = {}
    summary = {"rows": 0, "disposition_counts": {}, "by_clause": {}, "kind_counts": {}}
    try:
        data = load_register() if rows is None else list(rows)
    except (OSError, ValueError, UnicodeDecodeError, csv.Error) as exc:
        data = []
        reasons.append("register unreadable: " + str(exc))
    if not data and not reasons:
        reasons.append("register has no rows")
    if data:
        problems = validate_register(data, repo_root=repo_root, check_references=check_references)
        summary = summarize_register(data)
        counts = summary["disposition_counts"]
        if counts.get("(blank)", 0):
            reasons.append(f"{counts['(blank)']} unreviewed row(s)")
        if counts.get("UNVERIFIED_GAP", 0):
            reasons.append(f"{counts['UNVERIFIED_GAP']} UNVERIFIED_GAP row(s)")
        for key, found in problems.items():
            if found and key != "unreviewed":
                reasons.append(f"{len(found)} row(s) with {key}")
        if rows is None:
            manifest_rows = _manifest_rows(MANIFEST_JSON)
            if manifest_rows is not None and manifest_rows != len(data):
                reasons.append(f"register has {len(data)} rows but the manifest lists {manifest_rows}")
    counts = summary["disposition_counts"]
    status = "BLOCKED_NOT_CERTIFIED" if reasons else "REGISTER_REVIEWED_EXTERNAL_GATES_OPEN"
    return {
        "standard": "NBC 105:2025",
        "status": status,
        "certified": False,
        "blocking_reasons": reasons,
        "rows": summary["rows"],
        "unreviewed_rows": counts.get("(blank)", 0),
        "unverified_gap_rows": counts.get("UNVERIFIED_GAP", 0),
        "disposition_counts": counts,
        "open_external_rows": {k: counts.get(k, 0) for k in _OPEN_EXTERNAL},
        "by_clause": summary["by_clause"],
        "problem_counts": {k: len(v) for k, v in problems.items()},
        "external_gates": list(EXTERNAL_GATES),
        "note": ("A disposition is a source-to-code review note, not engineering acceptance. "
                 "Solver or unit-test PASS is not code compliance of any building."),
    }
