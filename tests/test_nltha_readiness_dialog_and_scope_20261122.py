"""Regression: NLTHA blocked-readiness UX and 0-second full history output scope.

No native OpenSees or GUI display needed. This is not an engineering approval.
"""
import ast
import copy
from pathlib import Path

from components.model.readiness import format_readiness_review

ROOT=Path(__file__).resolve().parents[1]


def _scope_function():
    source=(ROOT/"components/nonlinear_time_history/runner_and_gui.py").read_text(encoding="utf-8")
    tree=ast.parse(source)
    function=next(n for n in tree.body
                  if isinstance(n,ast.FunctionDef) and n.name=="_nltha_output_scope")
    # AST extraction isolates GUI logic; preserve module math binding explicitly.
    import math
    ns={"math":math}
    exec(compile(ast.Module([function],type_ignores=[]),"nltha_scope_test","exec"),ns)
    return ns["_nltha_output_scope"]


def test_full_duration_zero_must_be_suite_not_trial():
    scope=_scope_function()
    assert scope({"trial_duration_s":0.0})=="Suite"
    assert scope({"trial_duration_s":None})=="Suite"


def test_positive_diagnostic_duration_must_be_trial():
    scope=_scope_function()
    assert scope({"trial_duration_s":0.005})=="Trial"
    assert scope({"trial_duration_s":0.1})=="Trial"
    assert scope({"trial_duration_s":0.0,"preliminary_selection":True})=="Trial"


def test_readiness_report_groups_20_blockers_and_never_approves():
    checks=[{
        "code":f"check_false:check_{i}",
        "message":f"Review {i} not confirmed",
        "fix":"Supply actual reviewed evidence"} for i in range(16)]
    diagnosis={"ready":False, "blockers":[
        {"code":"not_approved","message":"Not approved",
         "fix":"Human reviewer sign-off required"},
        *checks,
        {"code":"material_file_missing","message":"No material file",
         "fix":"Review material schedule"},
        {"code":"wall_fsam_tags_empty","message":"No wall map",
         "fix":"Supply FSAM region mapping"},
        {"code":"parameters_not_reviewed","message":"No reviewed parameters",
         "fix":"Project-specific validation"}
    ]}
    original=copy.deepcopy(diagnosis)
    result=format_readiness_review(diagnosis)
    assert "20 unresolved" in result
    for t in ["MODEL MATERIALS","ENGINEERING CHECKLIST","HUMAN APPROVAL",
              "material_file_missing","wall_fsam_tags_empty",
              "check_false:check_0","not_approved","NOT A NATIVE SOLVER FAILURE"]:
        assert t in result
    assert result.count("check_false:")==16
    assert diagnosis==original
    assert "approved_for_nltha=True" not in result


def test_readiness_error_uses_scrollable_review_dialog_not_massive_messagebox():
    text=(ROOT/"components/nonlinear_time_history/runner_and_gui.py").read_text(encoding="utf-8")
    tree=ast.parse(text)
    gui=next(n for n in tree.body
             if isinstance(n,ast.ClassDef) and n.name=="NonlinearTimeHistoryGUI")
    methods={n.name:n for n in gui.body if isinstance(n,ast.FunctionDef)}
    assert "_open_readiness_blockers_dialog" in methods
    scope=methods["_run"]
    assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
               and n.func.attr=="_open_readiness_blockers_dialog"
               for n in ast.walk(scope))
