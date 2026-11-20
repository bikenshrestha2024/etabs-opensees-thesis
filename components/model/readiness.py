"""Project workflow controls for stability checks and damped-outrigger studies.

NBC 105:2025 is the governing Nepal seismic basis. NBC clauses require P-Delta
effects in analysis but do not prescribe a numerical theta stability limit in
the retrieved 2025 text. IS 16700:2023 clause 7.3.10 gives theta <= 0.20 for
its tall-building scope; this module labels that check supplementary and does
not claim that IS 16700 governs a Nepal project.
"""
from __future__ import annotations

__release__ = '134'

import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Source registry used by the project workflow; the full annotated bibliography
# and learning-resource notes are in REFERENCES_AND_LEARNING_RESOURCES_V116.md.
# NBC 105 governs the Nepal seismic basis. IS 16700 P-Delta load case selection
# is a project-required supplemental initial-analysis basis; its stability
# coefficient remains supplemental unless adopted by the approving authority.
PROJECT_REFERENCES = {
    "NBC105_2025": "https://www.dudbc.gov.np/pages/24231978/",
    "IS16700_2023": "https://www.services.bis.gov.in/tmp/CED20920094_14092023_1.pdf",
    "OPENSEES_DOCS": "https://opensees.github.io/OpenSeesDocumentation/",
    "OPENSEES_GITHUB": "https://github.com/OpenSees/OpenSees",
    "OPENSEESPY_GITHUB": "https://github.com/zhuminjie/OpenSeesPy",
    "ESFI_MVLEM_3D_PAPER": "https://doi.org/10.1016/j.engstruct.2023.116700",
    "ESFI_MVLEM_3D_DOCS": "https://kkolozvari.github.io/E-SFI-MVLEM-3D/",
    "OPENSEES_FVD_EXAMPLE": "https://opensees.berkeley.edu/wiki/index.php/Dynamic_Analyses_of_1-Story_Moment_Frame_with_Viscous_Dampers",
    "OPENSEES_FVD_MATERIAL": "https://opensees.berkeley.edu/wiki/index.php/ViscousDamper_Material",
    "YOUTUBE_NLTHA": "https://www.youtube.com/watch?v=s-AneO9KjgA",
}

IS16700_THETA_LIMIT = 0.20

STUDY_CASES = (
    ("C0_BASELINE_SHS", "Reference model: all mapped outrigger/belt/cap-truss braces remain SHS."),
    ("C1_PARTIAL_FVD", "Replace only the explicitly listed SHS objects with calibrated FVD devices."),
    ("C2_ALL_FVD", "Replace all eligible listed SHS brace objects with FVD devices."),
    ("C3_PARTIAL_BRB", "Replace only the explicitly listed SHS objects with calibrated BRB elements."),
    ("C4_ALL_BRB", "Replace all eligible listed SHS brace objects with BRBs."),
    ("C5_MIXED_FVD_BRB_SHS", "Use explicit object lists for FVD, BRB, and retained SHS in one model."),
)

REQUIRED_MODEL_COVERAGE = {
    "rc_beams_columns": "Review section/material mapping, offsets, releases, local axes and connection assumptions.",
    "core_walls_with_openings": "Model wall piers, spandrels/coupling beams and opening geometry; audit wall-shell or validated macro-element formulation.",
    "floor_slab_and_openings": "Create area/shell elements or another justified diaphragm/floor representation; account for openings, mass, stiffness and load transfer.",
    "rigid_diaphragm": "Use only where in-plane rigidity is justified; retain distinct ETABS diaphragm groups and all connected structural nodes.",
    "shs_braces_outrigger_belt_cap": "Map brace section properties, orientation, end connectivity, gussets/rigid arms, and tension/compression behavior.",
    "mass_and_gravity": "Close story mass and gravity ledgers including slab, wall, frame, cladding/equipment and device self-weight as applicable.",
    "fvd_brb_devices": "Use cited/certified device or test parameters; define location, axial direction, connection/series stiffness, stroke and force limits.",
    "nonlinear_model_validation": "Validate component laws and 3D model response before record runs; keep baseline and each replacement case comparable.",
}


def stability_coefficient_is16700(P_i: float, delta_i: float, V_i: float, h_i: float, R: float) -> float:
    """IS 16700:2023 §7.3.10 diagnostic: theta=P*Delta/(V*h*R).

    Use consistent force and length units; delta_i is the design inter-storey
    drift quantity entered for that clause. Positive magnitudes are required.
    This routine does not compute Delta from nodal displacements or determine
    code load factors; those quantities must come from a reviewed analysis.
    """
    vals = [float(P_i), float(delta_i), float(V_i), float(h_i), float(R)]
    if not all(math.isfinite(v) for v in vals):
        raise ValueError("P_i, delta_i, V_i, h_i and R must be finite")
    P_i, delta_i, V_i, h_i, R = vals
    if P_i < 0 or delta_i < 0 or V_i <= 0 or h_i <= 0 or R <= 0:
        raise ValueError("Use P_i >= 0, delta_i >= 0, and positive V_i, h_i, R")
    return P_i * delta_i / (V_i * h_i * R)


def evaluate_stability_rows(rows: List[Dict[str, Any]], theta_limit: float = IS16700_THETA_LIMIT) -> List[Dict[str, Any]]:
    """Evaluate dict rows with storey, axis, case, P_i, delta_i, V_i, h_i, R."""
    limit = float(theta_limit)
    if not math.isfinite(limit) or limit <= 0:
        raise ValueError("theta_limit must be positive and finite")
    result = []
    for row in rows:
        theta = stability_coefficient_is16700(row["P_i"], row["delta_i"], row["V_i"], row["h_i"], row["R"])
        result.append({**row, "theta_is16700": theta, "supplemental_limit": limit,
                       "status": "WITHIN SUPPLEMENTAL LIMIT" if theta <= limit else "EXCEEDS SUPPLEMENTAL LIMIT - REVIEW"})
    return result


def read_stability_csv(path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Read required columns from a user-reviewed per-storey force/drift CSV."""
    required = {"storey", "axis", "case", "P_i", "delta_i", "V_i", "h_i", "R"}
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Stability CSV missing columns: " + ", ".join(sorted(missing)))
        parsed_rows: List[Dict[str, Any]] = []
        numeric_columns = ("P_i", "delta_i", "V_i", "h_i", "R")
        for line_num, row in enumerate(reader, start=2):
            for column in numeric_columns:
                try:
                    row[column] = float(row[column])
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Invalid value in CSV row {line_num}, column '{column}': {row.get(column)!r}; "
                        "enter a numeric value."
                    ) from exc
            parsed_rows.append(row)
        return parsed_rows


def write_stability_report(input_csv: Union[str, Path], output_csv: Union[str, Path], building_height_m: Optional[float] = None) -> Dict[str, Any]:
    """Write the supplemental IS theta results and applicability statement."""
    rows = evaluate_stability_rows(read_stability_csv(input_csv))
    height = None if building_height_m in (None, "") else float(building_height_m)
    is_scope_note = ("IS 16700 tall-building scope (50 m < H <= 250 m): applicability appears met; confirm building/system scope."
                    if height is not None and 50.0 < height <= 250.0 else
                    "IS 16700 tall-building scope not established (scope states RC buildings >50 m and <=250 m); treat theta as diagnostic only.")
    p = Path(output_csv)
    p.parent.mkdir(parents=True, exist_ok=True)
    fields = ["storey", "axis", "case", "P_i", "delta_i", "V_i", "h_i", "R", "theta_is16700", "supplemental_limit", "status"]
    with p.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return {"report_csv": str(p), "rows": len(rows), "scope_note": is_scope_note,
            "governing_basis_note": "NBC 105:2025 requires P-Delta effects in analysis; this IS 16700 theta check is supplementary, not an NBC pass/fail criterion."}


def write_stability_input_template(path: Union[str, Path]) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["storey", "axis", "case", "P_i", "delta_i", "V_i", "h_i", "R"])
        writer.writerow(["REPLACE_WITH_STOREY", "X", "REPLACE_WITH_LOAD_CASE", "", "", "", "", ""])
    return str(p)


def write_case_matrix(path: Union[str, Path], base_model_path: Union[str, Path, None] = None,
                      results_root: Union[str, Path, None] = None) -> str:
    """Create a case register; each variant should branch from frozen baseline files."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    base = "" if base_model_path is None else str(base_model_path)
    root = "" if results_root is None else Path(results_root)
    with p.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["case_id", "study_description", "base_model_path", "results_dir",
                         "etabs_brace_object_ids", "device_or_shs_parameters_source", "run_status"])
        for case_id, description in STUDY_CASES:
            case_dir = "" if not root else str(root / case_id)
            writer.writerow([case_id, description, base, case_dir, "", "",
                             "NOT CONFIGURED - enter reviewed object IDs and source parameters"])
    return str(p)


def write_readiness_checklist(path: Union[str, Path], format: str = "json") -> str:
    """Export REQUIRED_MODEL_COVERAGE as JSON or Markdown for review/sign-off."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fmt = format.lower()
    if fmt not in {"json", "md", "markdown"}:
        raise ValueError("format must be 'json' or 'markdown'")
    if fmt == "json":
        checklist = {
            "project_status": "NOT READY UNTIL REVIEWED AND SIGNED OFF",
            "instructions": "Record evidence and reviewer/date for each item. Do not infer readiness from successful execution.",
            "governing_basis": "NBC 105:2025; IS 16700:2023 initial P-Delta case basis as project-required supplemental input.",
            "requirements": {key: {"description": description, "evidence": "", "reviewer": "", "date": "", "status": "PENDING"}
                             for key, description in REQUIRED_MODEL_COVERAGE.items()},
        }
        with p.open("w", encoding="utf-8") as stream:
            json.dump(checklist, stream, indent=2)
    else:
        lines = ["# OpenSees model readiness checklist (V116)", "",
                 "> Status: **NOT READY UNTIL REVIEWED AND SIGNED OFF**. A run completing is not model validation.", "",
                 "Basis: NBC 105:2025 governs seismic design. The project-required IS 16700:2023 P-Delta initial load cases are tracked separately; the IS stability check is supplemental.", "",
                 "| Coverage item | Required review | Evidence / file / ETABS check | Reviewer / date | Status |",
                 "|---|---|---|---|---|"]
        for key, description in REQUIRED_MODEL_COVERAGE.items():
            lines.append(f"| `{key}` | {description} |  |  | PENDING |")
        lines += ["", "See [annotated references and learning resources](REFERENCES_AND_LEARNING_RESOURCES_V116.md)."]
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p)



# ---------------------------------------------------------------------------
# Structured NLTHA readiness diagnosis (non-GUI). Read-only: this never writes
# a manifest and never sets approved_for_nltha or any checks[*] to True.
# Keep this tuple identical to the literal tuple in
# components/nonlinear_time_history/runner_and_gui.py::_require_nonlinear_readiness
# (readiness_gui.prepare reads that literal; a test enforces equality).
# ---------------------------------------------------------------------------
READINESS_CHECK_KEYS = (
    "etabs_topology_and_story_mapping_reviewed", "wall_opening_and_coupling_beam_mesh_reviewed",
    "wall_nonlinear_materials_and_reinforcement_cited_calibrated", "frame_concrete_and_rebar_materials_reviewed",
    "slab_and_diaphragm_idealization_compatible", "area_and_frame_gravity_loads_reconciled_to_etabs",
    "seismic_mass_reconciled_to_etabs_by_storey", "support_conditions_and_foundation_assumptions_reviewed",
    "is16700_initial_pdelta_plus_minus_cases_completed", "p_delta_and_gravity_preload_completed",
    "modal_periods_modes_and_mass_participation_reviewed",
    "brace_fvd_brb_case_matches_selected_scenario", "device_properties_cited_calibrated_or_devices_disabled",
    "rayleigh_damping_and_device_damping_not_double_counted", "single_element_and_wall_benchmark_checks_passed",
    "record_pair_units_scales_and_nbc_limits_reviewed",
)

_MODEL_CONFIG_NAME = "OpenSees_Complete_Model_Config_V118.json"


def _blocker(code: str, message: str, fix: str) -> Dict[str, str]:
    return {"code": code, "message": message, "fix": fix}


BINDING_FIELDS = ("model_config_sha256", "nonlinear_materials_file_sha256",
                  "nonlinear_wall_fsam_tags_sha256")
# Blocker codes the run gate raises on when a recorded binding no longer matches.
BINDING_MISMATCH_CODES = ("model_config_changed", "material_file_changed", "wall_fsam_tags_changed")
# Contradictions the run gate raises on only for an approved manifest.
APPROVED_CONTRADICTION_CODES = ("material_file_missing", "material_file_not_found", "wall_fsam_tags_empty")


def _file_sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_fsam_tags_hash(tags: Any) -> Optional[str]:
    """SHA-256 of the canonical JSON of the wall FSAM tag mapping (key order ignored).

    Returns None for an empty or absent mapping.
    """
    import hashlib
    if not tags:
        return None
    payload = json.dumps(tags, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _model_options(model: Path, config: Dict[str, Any]):
    """Return ``(config_path, opt)``; ``opt(key)`` prefers run config, else the model config file."""
    mcfg: Dict[str, Any] = {}
    mcfg_path = model.with_name(_MODEL_CONFIG_NAME)
    if mcfg_path.is_file():
        try:
            loaded = json.loads(mcfg_path.read_text(encoding="utf-8-sig"))
            mcfg = loaded if isinstance(loaded, dict) else {}
        except (OSError, ValueError):
            mcfg = {}

    def opt(key: str) -> Any:
        return config[key] if key in config else mcfg.get(key)
    return mcfg_path, opt


def _resolved_material_path(model: Path, material: Any) -> Optional[Path]:
    if not material:
        return None
    mp = Path(str(material)).expanduser()
    return mp if mp.is_absolute() else model.parent / mp


def current_binding(model_script: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> Dict[str, Optional[str]]:
    """Current SHA-256 binding values for a model (None when the item is absent/unconfigured).

    Keys: the three ``BINDING_FIELDS`` plus ``nonlinear_materials_file_resolved``
    (informational only; never compared).
    """
    model = Path(model_script).expanduser().resolve()
    cfg_path, opt = _model_options(model, config or {})
    mp = _resolved_material_path(model, opt("nonlinear_materials_file"))
    return {
        "model_config_sha256": _file_sha256(cfg_path) if cfg_path.is_file() else None,
        "nonlinear_materials_file_resolved": str(mp) if mp else None,
        "nonlinear_materials_file_sha256": _file_sha256(mp) if mp and mp.is_file() else None,
        "nonlinear_wall_fsam_tags_sha256": canonical_fsam_tags_hash(opt("nonlinear_wall_fsam_tags")),
    }


def record_binding(data: Dict[str, Any], model_script: Union[str, Path],
                   config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Record the current binding hashes into manifest ``data`` (in place) and return it.

    Only writes hash fields; never touches approval or any check.
    """
    data.update(current_binding(model_script, config))
    return data


def approval_binding_problems(model_script: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> List[str]:
    """Reasons an approval cannot be bound (missing material file / FSAM tags). Display/save-time only."""
    model = Path(model_script).expanduser().resolve()
    b = current_binding(model, config)
    problems: List[str] = []
    if b["nonlinear_materials_file_resolved"] is None:
        problems.append("nonlinear_materials_file is not configured (material file required for approval)")
    elif b["nonlinear_materials_file_sha256"] is None:
        problems.append("nonlinear_materials_file does not exist: " + str(b["nonlinear_materials_file_resolved"]))
    if b["nonlinear_wall_fsam_tags_sha256"] is None:
        problems.append("nonlinear_wall_fsam_tags is empty (FSAM tag mapping required for approval)")
    return problems


def _binding_blockers(data: Dict[str, Any], model: Path, config: Dict[str, Any]) -> List[Dict[str, str]]:
    missing = [f for f in BINDING_FIELDS if f not in data]
    out: List[Dict[str, str]] = []
    if missing:
        out.append(_blocker(
            "binding_not_recorded",
            "Manifest does not record SHA-256 binding for: " + ", ".join(missing) +
            ". Edits to the model config, material file or wall FSAM tags are not detected for those items.",
            "Save the checklist from Prepare / inspect readiness (or rebind the draft) to record the current hashes, then re-review."))
    now = current_binding(model, config)
    labels = {
        "model_config_sha256": ("model_config_changed", _MODEL_CONFIG_NAME, "model config"),
        "nonlinear_materials_file_sha256": ("material_file_changed", "nonlinear_materials_file", "material file"),
        "nonlinear_wall_fsam_tags_sha256": ("wall_fsam_tags_changed", "nonlinear_wall_fsam_tags", "wall FSAM tags"),
    }
    for field, (code, name, label) in labels.items():
        if field in data and data[field] != now[field]:
            out.append(_blocker(
                code, f"The {label} ({name}) differs from the version recorded at readiness review (SHA-256 mismatch or item removed).",
                f"Review the changed {label} and save a new model-specific checklist; approval does not carry over."))
    return out


def gate_binding_blockers(diagnosis: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Subset of a diagnosis the run gate raises on, for a manifest that passed every older gate check.

    Recorded-hash mismatches always count; missing material file / empty FSAM tags
    count only when ``data['approved_for_nltha']`` is True (contradictory approval).
    ``binding_not_recorded`` (legacy manifest) never raises.
    """
    codes = set(BINDING_MISMATCH_CODES)
    if data.get("approved_for_nltha") is True:
        codes |= set(APPROVED_CONTRADICTION_CODES)
    return [b for b in diagnosis.get("blockers", []) if b.get("code") in codes]


# ---------------------------------------------------------------------------
# Stale runtime-copy detection (read-only). A "runtime copy" is a frozen copy of
# the code tree (for example Saved_Project_V156/OpenSees_Runtime_V118/) that can
# run the nonlinear workflow with an older readiness gate. This only reads files;
# it never edits a runtime copy.
#
# Rule. The runtime root for a path is the nearest folder, starting at the path
# (or its parent, for a file) and walking up, that is named ``OpenSees_Runtime_V<digits>*``
# or contains ``components/nonlinear_time_history/runner_and_gui.py``. The copy is STALE
# when any of these hold:
#   runner_source_missing                runner_and_gui.py absent
#   runner_lacks_active_gate             runner text lacks any ACTIVE_GATE_RUNNER_MARKERS
#   readiness_module_missing             components/model/readiness.py absent
#   readiness_module_lacks_fingerprint   that file lacks any ACTIVE_GATE_MODULE_MARKERS
# The markers are the active gate's blocker-list call, binding check and key tuple, so a
# copy that predates the gate (or the input-binding check) is stale. This is a text
# fingerprint, not proof that two files are identical.
# ---------------------------------------------------------------------------
ACTIVE_GATE_RUNNER_MARKERS = ("diagnose_nonlinear_readiness", "format_readiness_blockers", "gate_binding_blockers")
ACTIVE_GATE_MODULE_MARKERS = ("READINESS_CHECK_KEYS", "def diagnose_nonlinear_readiness", "def gate_binding_blockers")
_RUNNER_REL = ("components", "nonlinear_time_history", "runner_and_gui.py")
_READINESS_REL = ("components", "model", "readiness.py")


def _is_runtime_dir_name(name: str) -> bool:
    import re
    return re.match(r"^OpenSees_Runtime_V\d+", name, re.IGNORECASE) is not None


def _check_runtime_root(root: Path) -> Dict[str, Any]:
    reasons: List[str] = []
    runner = root.joinpath(*_RUNNER_REL)
    mod = root.joinpath(*_READINESS_REL)

    def _text(p: Path) -> Optional[str]:
        try:
            return p.read_text(encoding="utf-8-sig", errors="replace") if p.is_file() else None
        except OSError:
            return None
    rtext, mtext = _text(runner), _text(mod)
    if rtext is None:
        reasons.append("runner_source_missing")
    elif any(m not in rtext for m in ACTIVE_GATE_RUNNER_MARKERS):
        reasons.append("runner_lacks_active_gate")
    if mtext is None:
        reasons.append("readiness_module_missing")
    elif any(m not in mtext for m in ACTIVE_GATE_MODULE_MARKERS):
        reasons.append("readiness_module_lacks_fingerprint")
    return {"runtime_root": str(root), "stale": bool(reasons), "reasons": reasons}


def detect_stale_runtime(path: Union[str, Path], include_children: bool = False) -> Dict[str, Any]:
    """Report whether ``path`` (a file or folder) lives in a runtime copy that predates the active gate.

    Returns ``{stale, runtime_root, reasons, copies}``. ``copies`` lists every runtime
    root examined (``runtime_root``/``stale``/``reasons``); the top-level fields describe the
    first stale copy, else the first copy, else ``None``/``[]``. With ``include_children`` the
    ``OpenSees_Runtime_V*`` folders directly inside the path's own folder are also examined
    (a project folder whose packaged runtime is old). Read-only; works for paths that do not exist.
    """
    p = Path(path).expanduser().resolve()
    start = p if p.is_dir() else p.parent
    copies: List[Dict[str, Any]] = []
    for d in [start, *start.parents]:
        if _is_runtime_dir_name(d.name) or d.joinpath(*_RUNNER_REL).is_file():
            copies.append(_check_runtime_root(d))
            break
    if include_children and start.is_dir():
        try:
            kids = sorted(c for c in start.iterdir() if c.is_dir() and _is_runtime_dir_name(c.name))
        except OSError:
            kids = []
        copies.extend(_check_runtime_root(c.resolve()) for c in kids)
    chosen = next((c for c in copies if c["stale"]), copies[0] if copies else None)
    return {"stale": any(c["stale"] for c in copies),
            "runtime_root": chosen["runtime_root"] if chosen else None,
            "reasons": list(chosen["reasons"]) if chosen else [],
            "copies": copies}


def runtime_copy_notice(model_script: Union[str, Path]) -> str:
    """Loud warning text when the model sits in, or beside, a stale runtime copy; else ''. Display only."""
    r = detect_stale_runtime(model_script, include_children=True)
    stale = [c for c in r["copies"] if c["stale"]]
    if not stale:
        return ""
    lines = ["WARNING: stale runtime copy. A runtime copy predates the active readiness gate; it may run an "
             "older gate without the blocker list or input-hash binding, and may open the ETABS EDB in place. "
             "Do not run it for NLTHA; use the active components/ code (the copy is immutable evidence and is not edited):"]
    lines += [f"  - {c['runtime_root']} ({', '.join(c['reasons'])})" for c in stale]
    return "\n".join(lines)


def diagnose_nonlinear_readiness(config: Dict[str, Any]) -> Dict[str, Any]:
    """Return ``{ready, blockers:[{code,message,fix}]}`` for an NLTHA run config.

    Covers the manifest/binding conditions, every required check key, and the
    project material, wall-FSAM and parameter-review prerequisites. Material
    values are read from ``config`` when present, else from
    ``OpenSees_Complete_Model_Config_V118.json`` beside the model script.
    """
    import hashlib
    blockers: List[Dict[str, str]] = []
    model_value = config.get("model_script")
    if not model_value:
        return {"ready": False, "blockers": [_blocker(
            "model_script_missing", "No nonlinear model script is selected.",
            "Select the exact OpenSees_Complete_Nonlinear_Model.py to run.")]}
    model = Path(model_value).expanduser().resolve()
    path = Path(config.get("model_readiness_json") or
                model.with_name("OpenSees_Model_Readiness_V116.json")).expanduser().resolve()
    data: Optional[Dict[str, Any]] = None
    bound_ok = False
    if not path.is_file():
        blockers.append(_blocker(
            "manifest_missing", f"Readiness manifest not found: {path}",
            "Open Prepare / inspect readiness checklist to create an UNAPPROVED model-bound draft beside the model script."))
    else:
        try:
            loaded = json.loads(path.read_text(encoding="utf-8-sig"))
            data = loaded if isinstance(loaded, dict) else None
        except (OSError, ValueError):
            data = None
        if data is None:
            blockers.append(_blocker(
                "manifest_unreadable", f"Readiness manifest is not a readable JSON object: {path}",
                "Re-create the draft from Prepare / inspect readiness checklist."))
    if data is not None:
        recorded = str(data.get("model_script", "")).strip()
        if not recorded or "absolute path to" in recorded.lower():
            blockers.append(_blocker(
                "template_unbound", "The manifest is an uncompleted readiness TEMPLATE (model_script is blank or a placeholder).",
                "Open Prepare / inspect readiness checklist and save its model-bound UNAPPROVED draft."))
        else:
            bound = Path(recorded).expanduser()
            if not bound.is_absolute():
                bound = path.parent / bound
            if bound.resolve() != model:
                blockers.append(_blocker(
                    "bound_to_other_model", f"Manifest is bound to {bound.resolve()} but the selected model is {model}.",
                    "Select the matching model or prepare a new UNAPPROVED draft; approval cannot be transferred."))
            else:
                bound_ok = True
        if bound_ok and data.get("model_script_sha256") and model.is_file():
            if data["model_script_sha256"] != hashlib.sha256(model.read_bytes()).hexdigest():
                blockers.append(_blocker(
                    "model_sha_mismatch", "Model script changed after readiness review (SHA-256 differs).",
                    "Review the changed model and save a new model-specific checklist."))
        if data.get("approved_for_nltha") is not True:
            blockers.append(_blocker(
                "not_approved", "approved_for_nltha is not True.",
                "Complete evidenced review of every item; approval is a human decision recorded in the manifest."))
        checks = data.get("checks", {})
        if not isinstance(checks, dict):
            checks = {}
        for key in READINESS_CHECK_KEYS:
            if checks.get(key) is not True:
                blockers.append(_blocker(
                    "check_false:" + key, "Check not confirmed: " + key.replace("_", " "),
                    "Attach evidence and mark it reviewed in the readiness checklist only after verification."))
    # Project material prerequisites (same conditions as components.model.nonlinear_preflight.inventory).
    mcfg_path, _opt = _model_options(model, config)
    material = _opt("nonlinear_materials_file")
    if not material:
        blockers.append(_blocker(
            "material_file_missing", "nonlinear_materials_file is not configured.",
            f"Set nonlinear_materials_file in {_MODEL_CONFIG_NAME} to the reviewed project material definitions; do not copy literature specimen values."))
    else:
        mp = _resolved_material_path(model, material)
        if not mp.is_file():
            blockers.append(_blocker(
                "material_file_not_found", f"Configured nonlinear_materials_file does not exist: {mp}",
                "Correct the path or provide the reviewed material file."))
    if not _opt("nonlinear_wall_fsam_tags"):
        blockers.append(_blocker(
            "wall_fsam_tags_empty", "nonlinear_wall_fsam_tags is empty (no wall property-to-FSAM region mapping).",
            f"Provide reviewed wall property-to-FSAM mappings in {_MODEL_CONFIG_NAME}."))
    if _opt("nonlinear_parameters_reviewed") is not True:
        blockers.append(_blocker(
            "parameters_not_reviewed", "nonlinear_parameters_reviewed is not True.",
            "Review reinforcement, confinement and cyclic parameters, then record the review in the model config."))
    if data is not None and bound_ok:
        blockers.extend(_binding_blockers(data, model, config))
    stale = detect_stale_runtime(model)
    if stale["stale"]:
        blockers.append(_blocker(
            "stale_runtime_copy",
            f"The model script is inside a runtime copy that predates the active readiness gate: {stale['runtime_root']} "
            f"({', '.join(stale['reasons'])}).",
            "Do not run from this copy. Use the active components/ code and a model script outside the stale runtime; "
            "the saved runtime is immutable evidence and is not edited."))
    return {"ready": not blockers, "blockers": blockers}


def format_readiness_blockers(diagnosis: Dict[str, Any]) -> str:
    """Plain-text blocker list for exception messages."""
    lines = [f"  {i}. [{b['code']}] {b['message']} Fix: {b['fix']}"
             for i, b in enumerate(diagnosis.get("blockers", []), 1)]
    return "\n".join(lines)


_NON_GATE_BLOCKER_CODES = ("material_file_missing", "material_file_not_found",
                           "wall_fsam_tags_empty", "parameters_not_reviewed", "binding_not_recorded")


def material_prerequisite_notice(diagnosis: Dict[str, Any]) -> str:
    """Text for blockers the run gate does not itself enforce on an unapproved/legacy manifest
    (materials, FSAM, parameter review, unrecorded binding).

    Empty string when none apply. Display only; never changes any approval state.
    """
    items = [b for b in diagnosis.get("blockers", []) if b.get("code") in _NON_GATE_BLOCKER_CODES]
    if not items:
        return ""
    lines = ["Material/model prerequisites still open (reported by the diagnosis; the run gate "
             "does not raise on these for an unapproved or legacy manifest, so resolve them before relying on a gate pass):"]
    lines += [f"  - [{b['code']}] {b['message']}" for b in items]
    return "\n".join(lines)


def bind_readiness_draft(template_path: Union[str, Path], model_script: Union[str, Path],
                         out_path: Union[str, Path, None] = None) -> Path:
    """Write (or keep) a model-bound UNAPPROVED readiness draft and return its path.

    The draft copies the template, binds the absolute ``model_script`` and its
    SHA-256, sets every check False, ``approved_for_nltha`` False and status
    ``UNAPPROVED DRAFT``. Nothing is ever set True. Default location is
    ``OpenSees_Model_Readiness_Draft_<model stem>_V134.json`` beside the model.

    An existing file already bound to this model path and hash is returned
    unchanged, approved or not (idempotent; human-saved evidence is kept). An
    existing file that would otherwise be replaced raises ``RuntimeError`` and
    is left untouched when it has ``approved_for_nltha`` True (stale hash or
    other model) or cannot be read, so approval cannot be ruled out. A
    stale unapproved draft (other model or changed hash) is rebuilt all-False.
    """
    import hashlib
    model = Path(model_script).expanduser().resolve()
    if not model.is_file():
        raise FileNotFoundError("Select an existing nonlinear model-builder script first")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    out = (Path(out_path).expanduser() if out_path is not None
           else model.with_name("OpenSees_Model_Readiness_Draft_" + model.stem + "_V134.json"))
    if out.exists():
        try:
            existing = json.loads(out.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise RuntimeError(f"Existing readiness file is unreadable and was not overwritten: {out}") from exc
        if not isinstance(existing, dict):
            raise RuntimeError(f"Existing readiness file is not a JSON object and was not overwritten: {out}")
        recorded = str(existing.get("model_script", "")).strip()
        if (recorded and Path(recorded).expanduser().resolve() == model
                and existing.get("model_script_sha256") == digest):
            return out  # current for this model: returned unchanged, approved or not
        if existing.get("approved_for_nltha") is True:
            raise RuntimeError(f"Refusing to overwrite an approved readiness file (approved_for_nltha is True): {out}")
    data = json.loads(Path(template_path).read_text(encoding="utf-8-sig"))
    data["model_script"] = str(model)
    data["model_script_sha256"] = digest
    data["approved_for_nltha"] = False
    data["status"] = "UNAPPROVED DRAFT"
    data["checks"] = dict.fromkeys(READINESS_CHECK_KEYS, False)
    data.setdefault("evidence", {})
    record_binding(data, model)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(out)
    return out
