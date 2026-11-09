"""Static inventory of the ACTIVE OpenSeesPy thesis research repository.

No native OpenSees execution; never edits/moves/renames model files.
Reads local source filenames, parses AST and compiles without execution. JSON is reproducible,
but source counts are version-specific. Run from the repository root:
    python tools/audit_active_repository.py --output audit/active_inventory.json

Do not confuse executable helpers, preserved V156 copies, and historical
result snapshots with the canonical execution workflow.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = ("components", "tests", "tools")
CANONICAL = {
    1: "01_WORKFLOW_START.py",
    2: "02_INPUT_READINESS.py",
    3: "03_MATERIAL_PARAMETER_SETUP.py",
    4: "04_LITERATURE_MATERIAL_PROFILES.py",
    5: "05_STEEL02_CALIBRATION.py",
    6: "06_MATERIAL_DEVICE_VALIDATION.py",
    7: "07_WALL_VALIDATION.py",
    8: "08_COMPONENT_RESULTS.py",
    9: "09_LITERATURE_COMPONENT_DEMO.py",
    10: "10_GRAVITY.py",
    11: "11_MODAL_ULS_SLS.py",
    12: "12_EQUIVALENT_STATIC.py",
    13: "13_RESPONSE_SPECTRUM.py",
    14: "14_LINEAR_TIME_HISTORY.py",
    15: "15_BUILDING_NONLINEAR_TRIAL.py",
    16: "16_NONLINEAR_REVIEWED_MODEL.py",
    17: "17_BUILDING_FULL_NONLINEAR.py",
    18: "18_NONLINEAR_PERFORMANCE.py",
    19: "19_AUDIT_LOAD_CONNECTIONS.py",
    20: "20_TRACE_FAILED_ELEMENT.py",
    21: "21_NLTHA_TRIAGE.py",
    22: "22_NBC105_INPUT_SYNC.py",
    27: "27_COMPARE_OUTRIGGERS.py",
    29: "29_NATIVE_DEVICE_BENCHMARK.py",
    30: "30_CALIBRATE_FVD_FROM_TEST.py",
    32: "32_NBC105_PAIR_SPECTRUM_AUDIT.py",
    33: "33_NBC105_VERTICAL_APPLICABILITY_REVIEW.py",
    34: "34_NBC105_RC_DUAL_C_D_TARGETS.py",
    35: "35_SOIL_C_NLTHA_PREFLIGHT.py",
    36: "36_SOIL_C_NLTHA_RUN_MATRIX.py",
    37: "37_THESIS_EVIDENCE_DASHBOARD.py",
}
STAGE = [
    ("00", "Target and source provenance", "Target workbook, soil C, Z/I, SeismoMatch SHA"),
    ("01", "ETABS export/input readiness", "Actual geometry/mass, floor diaphragms, openings, rebar register"),
    ("02", "Section/material/device evidence", "RC/steel/FSAM/FVD/BRB coupons and experimental benchmarks"),
    ("03", "Gravity, constraints and P-Delta", "Equilibrium and converged geometric nonlinearity"),
    ("04", "Modal/Tn90/damping", "Participation in X/Y, Rayleigh mode basis and device exclusion"),
    ("05", "ESM, MRSM and linear dynamics", "Cross-model geometry/mass/source response checks"),
    ("06", "Isolated NLTHA diagnostics", "ZERO, X, Y; first nonlinear step wall failure traces"),
    ("07", "Full paired nonlinear inputs", "8 source pairs, XY/YX, all samples, dt + source SHA"),
    ("08", "M0–M6 comparison", "Common model/input invariants and completed ULS/SLS cases"),
    ("09", "Acceptance and thesis results", "Drift, torsion, wall strains, FVD/BRB demands, energy + citations"),
]
HISTORICAL_PREFIXES = ("Saved_Project_", "archive/", "Recovered_", "Regression_",
                       "Verification_", "Worked_Example_", "Viewer_", "Research_Components/")

def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect_one_python(path, root=ROOT):
    """Parse and compile Python syntax and return symbols; never execute it."""
    source = path.read_text(encoding="utf-8-sig", errors="replace")
    rel = path.relative_to(root).as_posix()
    data = dict(path=rel, lines=len(source.splitlines()), sha256=_sha(path),
                parse_status="OK", classes=[], functions=[], imports=[])
    try:
        parsed = ast.parse(source, filename=str(path))
        # AST parsing alone accepts repeated keywords and misplaced break/return.
        # Compilation catches those import failures without running model code.
        compile(parsed, str(path), "exec", dont_inherit=True)
    except SyntaxError as exc:
        data.update(parse_status="SYNTAX_ERROR", syntax_line=exc.lineno,
                    syntax_error=str(exc.msg))
        return data
    for node in parsed.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            data["functions"].append({"name": node.name, "line": node.lineno})
        elif isinstance(node, ast.ClassDef):
            data["classes"].append({"name": node.name, "line": node.lineno})
        elif isinstance(node, ast.Import):
            data["imports"].extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            data["imports"].append(node.module or "<relative>")
    return data

def inventory(root=ROOT):
    root = Path(root)
    entries = []
    entries.extend(inspect_one_python(p, root) for p in sorted(root.glob("*.py")))
    for folder in SOURCE_ROOTS:
        target = root / folder
        if target.exists():
            entries += [inspect_one_python(p, root) for p in sorted(target.rglob("*.py"))
                        if "__pycache__" not in p.parts]
    numbered = defaultdict(list)
    for p in root.glob("*.py"):
        match = re.match(r"^(\d{2})_.+\.py$", p.name)
        if match:
            numbered[match.group(1)].append(p.name)
    duplication = {step: sorted(paths) for step,paths in numbered.items()
                   if len(paths)>1}
    canonical_missing = [name for name in CANONICAL.values() if not (root/name).is_file()]
    docs_missing = [
        e["path"] for e in entries if e["path"].startswith("components/")
        and not (root/"docs"/"source"/(e["path"]+".md")).is_file()
    ]
    important = ("components/model/assembly.py",
                 "components/nonlinear_time_history/building_exploratory.py",
                 "components/nonlinear_time_history/wall_topology.py",
                 "components/nonlinear_time_history/device_recording.py",
                 "components/model/reinforcement_mapping.py",
                 "components/nonlinear_time_history/soil_c_physics_preflight.py")
    important_entries = [e for e in entries if e["path"] in important]
    return {
        "kind": "STATIC_REPOSITORY_REVIEW_NOT_NATIVE_ENGINEERING_VALIDATION",
        "canonical_workflow": [
            dict(step=f"{i:02d}", launch_file=name, exists=(root/name).is_file())
            for i,name in sorted(CANONICAL.items())],
        "numbered_alias_conflicts": duplication,
        "active_python_module_count": len(entries),
        "active_python_modules": entries,
        "missing_source_guides": docs_missing,
        "canonical_missing": canonical_missing,
        "syntax_errors": [e for e in entries if e["parse_status"] != "OK"],
        "high_priority_code_index": important_entries,
        "stages": [{"step": n, "name": name, "evidence": evidence}
                   for n,name,evidence in STAGE],
        "warnings": [
            "Duplicate NN root launchers are compatibility aliases: do not bulk rename.",
            "Static parsing/compilation is not a line-by-line semantic/engineering review.",
            "Archived Saved_Project_ trees are not the currently maintained modules.",
            "First-step X core-wall failure and member experimental calibration remain unresolved.",
            "Do not label a passing source-PGA/spectrum check NBC compliant NLTHA."
        ],
    }

def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, default=Path("audit/active_inventory.json"))
    cli.add_argument("--fail-on-missing-canonical", action="store_true")
    args = cli.parse_args(argv)
    result = inventory()
    path = args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "kind", "active_python_module_count",
        "canonical_missing", "missing_source_guides", "syntax_errors")}, indent=2))
    return 2 if (args.fail_on_missing_canonical and
                 (result["canonical_missing"] or result["syntax_errors"])) else 0

if __name__ == "__main__":
    raise SystemExit(main())
