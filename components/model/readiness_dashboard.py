"""Read-only, model-bound readiness evidence assessment for thesis NLTHA.

Source files are not modified. Presence of a file provides evidence availability,
NEVER a physical calibration pass. Requires explicit reviewed evidence linked to
an unchanged model source. NBC 105:2025 is the seismic context; IS 16700 checks
are separately identified as project-adopted supplemental requirements.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

GROUPS = (
    ("model", "ETABS geometry and topology",
     "Independent comparison of source geometry, story groups, floor/core openings, coupling beams and node mapping",
     ("OpenSees_Complete_Model_Data_V118.json", "OpenSees_Area_Section_Assignment_Audit.json")),
    ("loads", "Loads, mass and diaphragm",
     "Gravity and source mass reconciliation, support conditions, source dead/live load accounting",
     ("OpenSees_Load_Conversion_Audit.json", "OpenSees_Complete_Story_Masters_V118.csv")),
    ("frames", "RC fiber sections and actual reinforcement",
     "Verified frame bar locations/cover/core and validated P-M section response; nominal templates are not enough",
     ("Approved_ETABS_Frame_Reinforcement.csv", "OpenSees_Nonlinear_Fiber_Section_Input_Template.csv")),
    ("walls", "Nonlinear core walls and openings",
     "E-SFI wall panels, openings, boundary confinement and cyclic specimen reproduction",
     ("NLTHA_Wall_Geometry_Preflight.json", "NLTHA_Wall_Opening_Preflight.json")),
    ("materials", "Concrete and steel calibration",
     "Measured cyclic comparisons for ConcreteCM/Concrete01/SteelMPF/Steel02 with source and fit report",
     ("Research_Material_Assignment_V161.json",)),
    ("devices", "FVD / BRB source and demand",
     "Native recorder format, force sign, dissipated energy and manufacturer/experimental device calibration",
     ("Native_Device_Benchmark_Report.json", "Device_Demand_Summary.json")),
    ("gravity_modal", "Gravity, modal and P-Delta",
     "Actual gravity result, model-bound modal evidence, signed P-Delta cases and dynamic initial state",
     ("OpenSees_Complete_Gravity_Check_V118.json", "NBC105_Modal_V111.json")),
    ("transient", "Nonlinear step stability",
     "ZERO/X/Y/XY first-step diagnostics and finite accepted state, including X-only failure",
     ("Accepted_History_Completion_Gate.json", "NLTHA_Wall_Geometry_Preflight.json")),
    ("vertical", "NBC 105:2025 vertical acceleration applicability",
     "Clause 4.3: >=20m spans, >5m cantilevers, prestressed horizontal members, beams supporting columns and base isolation",
     ("NBC105_Vertical_Applicability.json",)),
    ("nbc105", "NBC 105:2025 nonlinear motion compliance screening",
     "Site spectrum C(T)/Omega_u, 0.33..3 component factors, common lower pair factor, Tn90/T1 timestep, XY/YX and reviewed period evidence",
     ("NBC105_2025_NLTHA_Input_Screen.json", "Kobe_Pair_NBC105.json")),
    ("seismomatch", "Eight matched SeismoMatch earthquake pairs",
     "All sixteen matched source fingerprints and conditional PSA matching report; Gorkha duration and Loma Prieta end-time review, original X/Y scaling logs missing",
     ("Matched_Source_Integrity.json", "SeismoMatch_Source_Provenance.json")),
    ("motions", "Paired ground motions and full-duration cases",
     "Record pairing, dt, units, source SHA, ULS/SLS XY/YX and complete duration",
     ("Accepted_History_Completion_Gate.json",)),
)

# Human-approved checklist keys defined by the existing, separately audited
# model-bound readiness form (the single authoritative approval source).
REVIEW_KEYS = {
    "model": ("etabs_topology_and_story_mapping_reviewed",
              "wall_opening_and_coupling_beam_mesh_reviewed"),
    "loads": ("area_and_frame_gravity_loads_reconciled_to_etabs",
              "seismic_mass_reconciled_to_etabs_by_storey",
              "slab_and_diaphragm_idealization_compatible"),
    "frames": ("frame_concrete_and_rebar_materials_reviewed",),
    "walls": ("wall_nonlinear_materials_and_reinforcement_cited_calibrated",),
    "materials": ("frame_concrete_and_rebar_materials_reviewed",
                  "wall_nonlinear_materials_and_reinforcement_cited_calibrated"),
    "devices": ("device_properties_cited_calibrated_or_devices_disabled",
                "rayleigh_damping_and_device_damping_not_double_counted"),
    "gravity_modal": ("p_delta_and_gravity_preload_completed",
                      "modal_periods_modes_and_mass_participation_reviewed",
                      "is16700_initial_pdelta_plus_minus_cases_completed"),
    "transient": ("single_element_and_wall_benchmark_checks_passed",),
    "vertical": ("etabs_topology_and_story_mapping_reviewed",),
    "nbc105": ("record_pair_units_scales_and_nbc_limits_reviewed",),
    "seismomatch": ("record_pair_units_scales_and_nbc_limits_reviewed",),
    "motions": ("record_pair_units_scales_and_nbc_limits_reviewed",),
}


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _candidates(root, name):
    """Search only known project output locations, not unrelated user folders."""
    base = [root / name, root / "OpenSees_Analysis_Results" / name]
    results = root / "OpenSees_Analysis_Results"
    if results.is_dir():
        # Limit work and never traverse archived project copies or other roots.
        for item in sorted(results.glob("*/*/" + name))[:25]:
            base.append(item)
        for item in sorted(results.glob("*/" + name))[:25]:
            base.append(item)
    return [p for p in base if p.is_file()]


def discover_project_model(folder):
    """Find a unique, conventional nonlinear builder inside the selected project.

    Selection is for *inspection only*, never an approval. Do not recursively
    search output folders or choose among multiple candidates automatically.
    A caller must ask the user to select explicitly when more than one exists.
    """
    root = Path(folder).expanduser().resolve()
    names = (
        "OpenSees_Complete_Nonlinear_Model.py",
        "OpenSees_Complete_Gravity_Model.py",
    )
    # Gravity-only model is not a nonlinear builder. It is intentionally not
    # selected or returned as a substitute, even when it exists.
    candidates = [root / names[0]]
    found = [p for p in candidates if p.is_file() and p.parent == root]
    if len(found) == 1:
        return found[0], "UNIQUE_PROJECT_BUILDER_DETECTED_UNREVIEWED"
    return None, "NO_PROJECT_NONLINEAR_BUILDER_FOUND"


def _load_draft(model):
    if model is None or not model.is_file():
        return None, "NO_MODEL_SELECTED"
    draft = model.with_name("OpenSees_Model_Readiness_Draft_" + model.stem + "_V134.json")
    if not draft.is_file():
        return None, "NO_REVIEW_DRAFT"
    try:
        data = json.loads(draft.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            return None, "INVALID_DRAFT"
        if Path(data.get("model_script", "")).resolve() != model.resolve():
            return None, "MODEL_PATH_MISMATCH"
        if data.get("model_script_sha256") != _sha256(model):
            return None, "MODEL_SHA_MISMATCH"
        return data, "MODEL_BOUND_DRAFT_LOADED"
    except (OSError, ValueError, TypeError, KeyError):
        return None, "INVALID_DRAFT"


def audit(folder, model_script=None):
    root = Path(folder).expanduser().resolve()
    model = Path(model_script).expanduser().resolve() if model_script else None
    draft, draft_state = _load_draft(model)
    report = {
        "schema": "NLTHA_READINESS_EVIDENCE_V1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_folder": str(root),
        "model_script": str(model) if model else None,
        "model_sha256": _sha256(model) if model and model.is_file() else None,
        "draft_state": draft_state,
        "approved_for_nltha": False,
        "readiness_level": "DIAGNOSTIC_ONLY",
        "groups": [],
        "limitations": [
            "The presence of a file is not proof that its contents passed engineering validation.",
            "Paper specimen parameters and native smoke tests do not certify project materials.",
            "Reviewer sign-off does not replace physical model convergence or experimental reproduction.",
            "The X-only first-step instability remains unresolved until native solver evidence confirms a fix."
        ],
    }
    all_signed = bool(
        draft and draft.get("approved_for_nltha") is True
        and isinstance(draft.get("checks"), dict)
        and bool(draft["checks"])
        and all(value is True for value in draft["checks"].values())
        and isinstance(draft.get("evidence"), dict)
        and all(isinstance(draft["evidence"].get(key), str)
                and draft["evidence"][key].strip()
                and not draft["evidence"][key].startswith(
                    ("INPUT / REVIEW REQUIRED:", "AVAILABLE FOR REVIEW:"))
                for key in draft["checks"])
    )
    # A human sign-off is reported as a claim, never as verified solver readiness.
    report["approved_for_nltha"] = all_signed
    if all_signed:
        report["readiness_level"] = "MODEL_BOUND_SIGNOFF_RECORDED_NOT_AUTOMATICALLY_VERIFIED"
    for key, label, description, filenames in GROUPS:
        found = []
        for filename in filenames:
            for path in _candidates(root, filename):
                found.append({
                    "path": str(path),
                    "sha256": _sha256(path),
                    "bytes": path.stat().st_size,
                    "meaning": "AVAILABLE_FOR_REVIEW_ONLY"
                })
        keys = REVIEW_KEYS.get(key, ())
        evidence = draft.get("evidence", {}) if draft else {}
        checks = draft.get("checks", {}) if draft else {}
        signed = bool(keys and all(checks.get(k) is True for k in keys)
                      and all(isinstance(evidence.get(k), str)
                              and evidence[k].strip()
                              and not evidence[k].startswith(("INPUT / REVIEW REQUIRED:", "AVAILABLE FOR REVIEW:"))
                              for k in keys))
        state = ("REVIEWED_SIGNOFF_CLAIM" if signed else
                 "EVIDENCE_FOUND_REVIEW_REQUIRED" if found else "MISSING_EVIDENCE")
        report["groups"].append({
            "id": key, "title": label, "description": description,
            "status": state, "evidence": found,
            "required_review_keys": list(keys),
            "review_claim_present": signed,
            "next_action": ("Review and record independent test/source evidence in the model-bound form"
                            if found else "Generate and inspect source/model-specific evidence")
        })
    report["counts"] = {state: sum(g["status"] == state for g in report["groups"])
                        for state in ("REVIEWED_SIGNOFF_CLAIM", "EVIDENCE_FOUND_REVIEW_REQUIRED", "MISSING_EVIDENCE")}
    return report


def export_report(report, output_folder):
    """Write audit only to requested project output folder. Never edit the draft."""
    destination = Path(output_folder).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / "Nonlinear_Readiness_Audit.json"
    md_path = destination / "Nonlinear_Readiness_Audit.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    lines = [
        "# Nonlinear analysis readiness — evidence review",
        "",
        "Model: `" + str(report["model_script"] or "NOT SELECTED") + "`",
        "",
        "Model SHA256: `" + str(report["model_sha256"] or "NOT AVAILABLE") + "`",
        "",
        "**Status:** " + report["readiness_level"],
        "",
        "Draft state: " + report["draft_state"],
        "",
        "| Workstream | Evidence status | Evidence files |",
        "|---|---|---:|",
    ]
    for group in report["groups"]:
        lines.append("| " + group["title"] + " | " + group["status"] +
                     " | " + str(len(group["evidence"])) + " |")
    lines += ["", "## Evidence detail", ""]
    for group in report["groups"]:
        lines += ["### " + group["title"], "",
                  group["description"], "",
                  "Status: **" + group["status"] + "**", ""]
        lines += ["- `" + e["path"] + "` (SHA256 `" + e["sha256"] + "`)"
                  for e in group["evidence"]]
        if not group["evidence"]:
            lines.append("- No matching source evidence found")
        lines.append("")
    lines += ["## Important limitations", ""]
    lines += ["- " + item for item in report["limitations"]]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path
