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
        bound_ok = False
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
    mcfg: Dict[str, Any] = {}
    mcfg_path = model.with_name(_MODEL_CONFIG_NAME)
    if mcfg_path.is_file():
        try:
            loaded = json.loads(mcfg_path.read_text(encoding="utf-8-sig"))
            mcfg = loaded if isinstance(loaded, dict) else {}
        except (OSError, ValueError):
            mcfg = {}
    def _opt(key: str) -> Any:
        return config[key] if key in config else mcfg.get(key)
    material = _opt("nonlinear_materials_file")
    if not material:
        blockers.append(_blocker(
            "material_file_missing", "nonlinear_materials_file is not configured.",
            f"Set nonlinear_materials_file in {_MODEL_CONFIG_NAME} to the reviewed project material definitions; do not copy literature specimen values."))
    else:
        mp = Path(str(material)).expanduser()
        if not mp.is_absolute():
            mp = model.parent / mp
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
    return {"ready": not blockers, "blockers": blockers}


def format_readiness_blockers(diagnosis: Dict[str, Any]) -> str:
    """Plain-text blocker list for exception messages."""
    lines = [f"  {i}. [{b['code']}] {b['message']} Fix: {b['fix']}"
             for i, b in enumerate(diagnosis.get("blockers", []), 1)]
    return "\n".join(lines)


_NON_GATE_BLOCKER_CODES = ("material_file_missing", "material_file_not_found",
                           "wall_fsam_tags_empty", "parameters_not_reviewed")


def material_prerequisite_notice(diagnosis: Dict[str, Any]) -> str:
    """Text for blockers the run gate does not itself enforce (materials, FSAM, review).

    Empty string when none apply. Display only; never changes any approval state.
    """
    items = [b for b in diagnosis.get("blockers", []) if b.get("code") in _NON_GATE_BLOCKER_CODES]
    if not items:
        return ""
    lines = ["Material/model prerequisites still open (reported by the diagnosis; the run gate "
             "does not raise on these, so resolve them before relying on a gate pass):"]
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
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(out)
    return out
