"""Static guard: non-GUI core modules never import tkinter at module level.

conftest.py turns a missing-module ``tkinter`` failure into a SKIP, so a new
top-level ``import tkinter`` in a core module would silently skip the headless
tests that exercise it. This test is pure AST analysis, imports none of the
modules, and cannot be skipped by the conftest hook (it never raises
ModuleNotFoundError). Function-local imports remain allowed.

[REF docs/superpowers/plans/2026-11-20-binding-ci-audit.md Global Constraints]
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_MODULES = (
    "components/model/readiness.py",
    "components/validation/gravity_etabs_direct.py",
    "components/model/assembly.py",
    "components/model/nonlinear_preflight.py",
    "tools/audit_literature_code_map.py",
)
GUI_ROOTS = {"tkinter", "_tkinter"}
EXPECTED_SKIP_MODULES = {"tkinter", "_tkinter", "plotly", "comtypes", "win32com", "pythoncom", "pywintypes"}


def toplevel_gui_imports(source):
    """Names of tkinter imports executed at module import time (not inside def/class-method bodies)."""
    found = []

    def visit(statements):
        for node in statements:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue  # function-local imports are allowed
            if isinstance(node, ast.Import):
                found.extend(a.name for a in node.names if a.name.split(".")[0] in GUI_ROOTS)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and (node.module or "").split(".")[0] in GUI_ROOTS:
                    found.append(node.module)
            else:
                for field in ("body", "orelse", "finalbody", "handlers"):
                    inner = getattr(node, field, None)
                    if isinstance(inner, list):
                        visit([h for h in inner])
                if isinstance(node, ast.ClassDef):
                    visit(node.body)
    visit(ast.parse(source).body)
    return found


def test_detector_flags_module_level_and_ignores_function_local():
    assert toplevel_gui_imports("import tkinter as tk\n") == ["tkinter"]
    assert toplevel_gui_imports("from tkinter import ttk\n") == ["tkinter"]
    assert toplevel_gui_imports("try:\n    import tkinter\nexcept ImportError:\n    tkinter = None\n") == ["tkinter"]
    assert toplevel_gui_imports("if True:\n    from tkinter.ttk import Frame\n") == ["tkinter.ttk"]
    assert toplevel_gui_imports("def f():\n    import tkinter\n") == []
    assert toplevel_gui_imports("import json\n") == []


def test_core_modules_have_no_toplevel_tkinter_import():
    for rel in CORE_MODULES:
        path = ROOT / rel
        assert path.is_file(), rel
        assert toplevel_gui_imports(path.read_text(encoding="utf-8-sig")) == [], rel


def test_conftest_skip_is_limited_to_missing_optional_modules():
    source = (ROOT / "conftest.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    optional = next(
        n for n in tree.body if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "OPTIONAL_MODULES" for t in n.targets))
    names = {e.value for e in ast.walk(optional.value) if isinstance(e, ast.Constant)}
    assert names == EXPECTED_SKIP_MODULES
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    body = ast.dump(funcs["_optional_name"])
    assert "ModuleNotFoundError" in body and "OPTIONAL_MODULES" in body
    assert "ImportError" not in body.replace("ModuleNotFoundError", "")
    # the only place an outcome is turned into a skip is gated by those helpers
    for hook in ("pytest_runtest_makereport", "pytest_make_collect_report"):
        text = ast.dump(funcs[hook])
        assert "_strict" in text and ("_optional_name" in text or "_collect_message_name" in text)
