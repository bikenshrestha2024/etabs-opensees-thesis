"""Source-mapped first-step NLTHA transition diagnostics (no FEM changes).

[REF docs/source/components/nonlinear_time_history/first_step_transition.py.md]
Records focused E-SFI-MVLEM-3D and node mass/response snapshots around
gravity -> eigenanalysis -> excitation -> first accepted transient step.
No solver configuration, static load, element parameter, material, mesh or
record is altered. A transition bracket is NOT a proven initiating cause.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

from components.inputs.output_contract import atomic_json
from components.nonlinear_time_history.failure_evidence import (
    snapshot_selected_state, _focus_tags
)

STAGES = (
    "GRAVITY_FROZEN",
    "AFTER_EIGEN",
    "BEFORE_EXCITATION",
    "FIRST_ACCEPTED_STEP",
)


def diagnostic_focus_tags(config):
    """[REF docs/source/components/nonlinear_time_history/first_step_transition.py.md]
    Preserve exact positive element tags (default 110280), never reinterpret
    floats, booleans or source ETABS IDs as OpenSees element tags.
    """
    if not isinstance(config, dict):
        raise TypeError("Diagnostic configuration must be an object")
    tags = config.get("first_step_focus_tags", [110280])
    if not isinstance(tags, (list, tuple)):
        raise ValueError("first_step_focus_tags must be a list of exact element tags")
    return _focus_tags(tags)


def capture_transition(ops, path, *, stage, focus_tags,
                       source_model_sha256=None):
    """[REF docs/source/components/nonlinear_time_history/first_step_transition.py.md]
    Capture read-only focused wall forces and connected-node translational
    mass at an explicitly named solver stage. Never assume unsupported=zero.
    """
    if stage not in STAGES:
        raise ValueError("Unknown first-step diagnostic stage: " + str(stage))
    tags = _focus_tags(focus_tags)
    if source_model_sha256 is not None and (
            not isinstance(source_model_sha256, str)
            or not re.fullmatch(r"[0-9a-fA-F]{64}", source_model_sha256)):
        raise ValueError("source_model_sha256 must be a 64-digit SHA256 or None")
    target = Path(path)
    state = snapshot_selected_state(
        ops, target, suspect_tags=tags, stage=stage)
    state["stage"] = stage
    state["source_model_sha256"] = source_model_sha256
    state["solver_state_modified"] = False
    state["mass_audit"] = {}
    element_nodes = sorted({
        int(node["tag"])
        for item in state["elements"]
        for node in item.get("nodes", [])
    })
    for node in element_nodes:
        entry = {"status": "UNSUPPORTED_OR_ERROR"}
        try:
            mass = [float(ops.nodeMass(node, dof)) for dof in (1, 2, 3)]
            if len(mass) != 3 or any(not math.isfinite(v) for v in mass):
                entry = {"status": "NONFINITE", "values": [str(x) for x in mass]}
            elif any(v < 0 for v in mass):
                entry = {"status": "NEGATIVE", "values": mass}
            else:
                entry = {"status": "FINITE", "values": mass}
        except (AttributeError, TypeError, ValueError, RuntimeError,
                OverflowError) as exc:
            entry = {"status": "UNSUPPORTED_OR_ERROR",
                     "error_type": type(exc).__name__}
        state["mass_audit"][str(node)] = entry
    nonfinite = any(
        record.get("status") == "NONFINITE"
        for item in state["elements"]
        for record in (
            [*item.get("responses", {}).values()]
            + [value for node in item.get("nodes", [])
               for value in (
                   node.get("nodeCoord", {}),
                   node.get("nodeDisp", {}),
                   node.get("nodeVel", {}),
                   node.get("nodeAccel", {}))]
        )
    )
    invalid_mass = any(v["status"] in ("NONFINITE", "NEGATIVE")
                       for v in state["mass_audit"].values())
    if state.get("missing_tags"):
        state["status"] = "FOCUSED_ELEMENT_ABSENT"
    elif nonfinite or invalid_mass:
        state["status"] = "NONFINITE_FOCUSED_RESPONSE"
    else:
        state["status"] = "FINITE_WITH_UNSUPPORTED_CHANNELS"
    state["diagnostic_limitations"] = [
        "Snapshot of selected OpenSees element tags, not the complete model.",
        "Unsupported material, element or nodal mass channels are not zeros.",
        "A nonfinite response brackets a symptom, not its initiating cause.",
        "No gravity equilibrium, element calibration or code compliance is certified.",
    ]
    atomic_json(target, state)
    return state


def compare_first_step_stages(files, output_path):
    """[REF docs/source/components/nonlinear_time_history/first_step_transition.py.md]
    Compare stored snapshots in supplied chronological order; no solver calls.
    """
    if not isinstance(files, (list, tuple)) or not files:
        raise ValueError("At least one existing transition snapshot is required")
    seen = []
    first_model_sha = None
    source_identity_seen = False
    last_stage_index = -1
    for file in files:
        path = Path(file)
        state = json.loads(path.read_text(encoding="utf-8-sig"))
        if state.get("status") not in (
                "NONFINITE_FOCUSED_RESPONSE",
                "FINITE_WITH_UNSUPPORTED_CHANNELS",
                "FOCUSED_ELEMENT_ABSENT"):
            raise ValueError("Unrecognized focused-stage evidence in " + str(path))
        if state.get("stage") not in STAGES and state.get("status") not in STAGES:
            raise ValueError("Missing/unknown diagnostic stage: " + str(path))
        stage = state.get("stage", state.get("status"))
        if stage not in STAGES:
            raise ValueError("Missing/unknown diagnostic stage: " + str(path))
        position = STAGES.index(stage)
        if position <= last_stage_index:
            raise ValueError("Diagnostic stage files must be strictly chronological")
        last_stage_index = position
        digest = state.get("source_model_sha256")
        if digest is not None and (
                not isinstance(digest, str)
                or not re.fullmatch(r"[0-9a-fA-F]{64}", digest)):
            raise ValueError("Invalid source model SHA256 in " + str(path))
        if not source_identity_seen:
            first_model_sha = digest
            source_identity_seen = True
        elif digest != first_model_sha:
            raise ValueError("Diagnostic snapshots refer to different source model hashes")
        seen.append({"stage": stage, "status": state["status"],
                     "source": str(path)})
    last_finite = None
    first_bad = None
    for item in seen:
        if item["status"] == "NONFINITE_FOCUSED_RESPONSE":
            first_bad = item["stage"]
            break
        if item["status"] == "FINITE_WITH_UNSUPPORTED_CHANNELS":
            last_finite = item["stage"]
    outcome = ("ONSET_BRACKET_REQUIRES_NATIVE_REVIEW" if first_bad
               else "FOCUSED_ELEMENT_ABSENT" if any(
                   x["status"] == "FOCUSED_ELEMENT_ABSENT" for x in seen)
               else "NO_NONFINITE_IN_SAMPLED_STAGES")
    result = {
        "status": outcome,
        "last_finite_stage": last_finite,
        "first_nonfinite_stage": first_bad,
        "stages": seen,
        "engineering_root_cause_proven": False,
        "native_solver_executed_by_comparison": False,
        "warning": "Stage-onset association is not causal identification.",
    }
    atomic_json(output_path, result)
    return result
