"""Soil C primary eight-pair, already-matched NLTHA motion preflight.

Actual input provenance: docs/ground_motions/seismomatch_20261104/
NBC 105:2025 §§4.1.1-4.1.2, 9.3.1-9.3.3.
DO NOT infer that spectral-error statistics alone approve source selection,
original SeismoMatch factor range, simultaneous pairing, or the building model.

This pure-stdlib module never edits, trims, interpolates, pads or re-scales
record samples. Matched accelerations are in g; OpenSees additional spectrum
scale = 1, unit-conversion factor = 9.80665 for the kN-m-s model.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

from components.nonlinear_time_history.nbc105_2025_audit import (
    nbc105_time_step_limit, response_aggregation_rule, scaling_period_range,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs/ground_motions/seismomatch_20261104/matched_component_register.csv"
SYSTEM = "RC_DUAL_RC_SHEAR_WALL"
SOIL = "C"
Z = .35
I = 1.0
R_MU = 3.5
OMEGA_U = 1.4
MATCHED_INTERVAL_S = (.05, 6.0)
UNIT_FACTOR_M_S2 = 9.80665
FIELD_TYPE = {
    "Gorkha": "Near-field", "Landers": "Near-field",
    "Northridge": "Near-field", "Kobe": "Near-field",
    "Kocaeli": "Near-field", "Chi-Chi": "Near-field",
    "Hector Mine": "Far-field", "Loma Prieta": "Far-field",
}
# The near/far designation follows the study's grouping; earthquake source
# distance, rupture directivity and pulse classification are NOT verified
# by file names and require record selection metadata for each station.
EVENT_ORDER = tuple(FIELD_TYPE)
EXPLICIT_REVIEW = {
    "Gorkha": "Matched exports span 322.94 s; original files span 120 s. Verify full processing/export history.",
    "Loma Prieta": "Component A ends 39.975 s, B ends 39.980 s; confirm an explicit end-time policy.",
}


def register_rows(register=REGISTER):
    """Read a strictly paired A/B manifest; source paths may not escape a directory."""
    with Path(register).open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 16:
        raise ValueError("Soil C source register must contain exactly 16 components")
    found = {}
    for row in rows:
        key = (row["event"], row["component"])
        name = row["source_filename"]
        if (key in found or key[0] not in FIELD_TYPE or key[1] not in ("A", "B")
                or not name or Path(name).name != name or "/" in name or "\\" in name):
            raise ValueError("Invalid duplicate, event/component or unsafe matched source path")
        digest = row["matched_sha256"].lower()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Invalid source SHA256")
        found[key] = row
    if set(found) != {(name, comp) for name in EVENT_ORDER for comp in ("A", "B")}:
        raise ValueError("The manifest does not contain the expected eight complete pairs")
    return found


def _metadata(row):
    return {
        "source_filename": row["source_filename"],
        "sha256": row["matched_sha256"],
        "dt_s": float(row["matched_dt_s"]),
        "end_s": float(row["matched_end_time_s"]),
        "pga_g": float(row["matched_pga_g"]),
        "previous_conditional_mean_PSA_error_percent":
            float(row["mean_abs_conditional_psa_error_percent"]),
    }


def audit_suite(matched_root, *, t1_x_s=None, t1_y_s=None, tn90_x_s=None,
                tn90_y_s=None, analysis_dt_s=None, register=REGISTER,
                verify_waveforms=True):
    """Audit exact input bytes, pair synchronization and optional NBC time bound.

    No period is filled in from an unrelated ETABS trial or the workbook's
    illustrative period. No new FVD, BRB or RC material values are inferred.
    """
    source = Path(matched_root).expanduser().resolve()
    entries = register_rows(register)
    if not source.is_dir():
        raise NotADirectoryError(str(source))
    from tools.verify_matched_waveforms import check_source
    pairs = []
    source_failures = []
    timing_review = []
    for event in EVENT_ORDER:
        comps = []
        for label in ("A", "B"):
            row = entries[event, label]
            path = source / row["source_filename"]
            if not path.is_file():
                source_failures.append({"event":event, "component":label,
                                        "reason":"SOURCE_FILE_MISSING"})
                comps.append({"component":label, "status":"MISSING",
                              **_metadata(row)})
                continue
            if verify_waveforms:
                try:
                    inspected = check_source(path, row)
                    if inspected["status"] != "SOURCE_REGISTER_MATCH":
                        source_failures.append({"event":event, "component":label,
                                                "reason":inspected["errors"]})
                except (OSError, ValueError) as exc:
                    inspected = {"status":"SOURCE_PARSE_FAILED","errors":[str(exc)]}
                    source_failures.append({"event":event, "component":label,
                                            "reason":[str(exc)]})
            else:
                inspected = {"status":"NOT_CHECKED"}
            comps.append({"component":label, **_metadata(row),
                          "status":inspected["status"]})
        a, b = (entries[event, x] for x in ("A", "B"))
        dt_a, dt_b = float(a["matched_dt_s"]), float(b["matched_dt_s"])
        end_a, end_b = float(a["matched_end_time_s"]), float(b["matched_end_time_s"])
        if abs(dt_a-dt_b)>1e-10 or abs(end_a-end_b)>1e-10:
            timing_review.append(event)
        pairs.append({
            "pair_id":event.replace(" ","_"),
            "earthquake":event,
            "study_field_type":FIELD_TYPE[event],
            "seismological_distance_class_independently_verified":False,
            "target_soil":"C", "original_records_are_already_matched":True,
            "common_additional_spectrum_scale":1.0,
            "path_factor_if_units_g_m_s2":UNIT_FACTOR_M_S2,
            "simultaneous_orientations":["XY","YX"],
            "dt_s":dt_a,"duration_a_s":end_a,"duration_b_s":end_b,
            "components":comps,
            "timing_policy_required":event in timing_review,
            "processing_history_required":event=="Gorkha",
        })
    optional = [t1_x_s,t1_y_s,tn90_x_s,tn90_y_s,analysis_dt_s]
    has_modal = all(v is not None for v in optional)
    if any(v is not None for v in optional) and not has_modal:
        raise ValueError("Supply ALL of T1_X, T1_Y, Tn90_X, Tn90_Y, dt, or NONE")
    period = {"status":"UNKNOWN_NO_VERIFIED_CURRENT_MODAL_INPUTS"}
    if has_modal:
        windows = {axis:scaling_period_range(tn,t1,R_MU) for axis, tn,t1 in (
            ("X",tn90_x_s,t1_x_s),("Y",tn90_y_s,t1_y_s))}
        ranges_covered = all(MATCHED_INTERVAL_S[0] <= a and
                             b <= MATCHED_INTERVAL_S[1] for a,b in windows.values())
        dt_bound = {pair["earthquake"]:nbc105_time_step_limit(
            record_dt_s=pair["dt_s"],
            t1_x_s=t1_x_s,t1_y_s=t1_y_s,
            tn90_x_s=tn90_x_s,tn90_y_s=tn90_y_s) for pair in pairs}
        chosen_dt=float(analysis_dt_s)
        if not math.isfinite(chosen_dt) or chosen_dt <= 0:
            raise ValueError("analysis_dt_s must be finite and positive")
        period = {
            "status":"INPUT_PERIOD_SCREEN_ONLY",
            "fit_window_X_s":windows["X"],"fit_window_Y_s":windows["Y"],
            "record_fit_range_covered":ranges_covered,
            "analysis_dt_by_event_limit_s":dt_bound,
            "proposed_analysis_dt_s":chosen_dt,
            "time_step_screen_pass":all(chosen_dt <= v+1e-12
                                        for v in dt_bound.values()),
            "current_modal_source_verified_by_this_program":False,
        }
    checks_pass = bool(verify_waveforms and not source_failures and not timing_review)
    return {
        "status":("SOURCE_WAVEFORMS_NOT_READ" if not verify_waveforms else
                  "SOURCE_FILES_NOT_VERIFIED" if source_failures else
                  "SOURCE_INTEGRITY_REVIEW_REQUIRED" if timing_review else
                  "SOURCE_REGISTER_MATCH_NOT_NBC_APPROVAL"),
        "target":dict(soil=SOIL,system=SYSTEM,Z=Z,I=I,R_mu=R_MU,
                      omega_u=OMEGA_U,period_min_s=.05,period_max_s=6.),
        "records":pairs,
        "pair_count":len(pairs), "component_count":16,
        "orientations_per_pair":["XY","YX"],
        "expected_horizontal_cases_per_model_state":16,
        "study_field_type_counts":{"Near-field":6,"Far-field":2},
        "study_field_type_is_user_supplied_not_independently_checked":True,
        "component_source_failures":source_failures,
        "timing_policy_review_required":timing_review,
        "source_and_pair_synchronization_pass":checks_pass,
        "current_modal_period_screen":period,
        "nbc_105_9_3_3_response_rule_for_eight_pairs":
            response_aggregation_rule(8),
        "gorkha_export_provenance_reviewed":False,
        "loma_prieta_end_time_policy_approved":False,
        "original_SeismoMatch_0_33_to_3_scale_logs_verified":False,
        "original_SeismoMatch_lower_of_pair_factor_verified":False,
        "site_Vs30_and_record_magnitude_distance_metadata_verified":False,
        "site_and_earthquake_input_design_approval":False,
        "solver_and_nonlin_material_model_approved":False,
        "important":("The eight waveform pairs are already matched to Soil C. "
                     "Never apply a second spectral factor in OpenSees. "
                     "Retain the two orthogonal components in XY and YX, and "
                     "review the Gorkha and Loma Prieta provenance issues."),
    }


def write_suite_report(destination, matched_root, **kwargs):
    data=audit_suite(matched_root,**kwargs)
    p=Path(destination)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,allow_nan=False),encoding="utf-8")
    return data


def verify_runner_pair(x_path, y_path, *, registered_event=None,
                       gorkha_processing_approved=False, reviewer=None,
                       loma_end_policy="reject"):
    """Bind a REAL run to exactly one registered A/B pair by SHA256.

    Filenames may have a browser's '(1)' suffix; hashes are canonical.
    This check NEVER regards record source as proof of SeismoMatch source
    scale logs or the approved target, merely the waveforms being used.
    """
    files = [Path(x_path).resolve(), Path(y_path).resolve()]
    if not all(p.is_file() for p in files):
        raise FileNotFoundError("Both registered Soil C matched components required")
    sha = [hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
    entries = register_rows()
    event = None
    for name in EVENT_ORDER:
        if (sha[0] == entries[name, "A"]["matched_sha256"] and
                sha[1] == entries[name, "B"]["matched_sha256"]):
            event = name
            break
    if event is None:
        raise ValueError("Matched waveforms do not correspond to one approved-register A/B pair in their A/B order")
    if registered_event is not None and registered_event != event:
        raise ValueError("Selected event does not match source waveform SHA256")
    if event == "Gorkha" and not gorkha_processing_approved:
        raise ValueError("Gorkha source expands 120s to 322.94s; explicit project-source review required")
    if event == "Loma Prieta" and loma_end_policy != "append_zero_reviewed":
        raise ValueError("Loma Prieta original matched A/B differ by 0.005s; explicitly review zero-extension or revise source")
    if event == "Loma Prieta" and not reviewer:
        raise ValueError("A named engineering reviewer is required for the Loma Prieta 0.005s reconciliation")
    if event == "Gorkha" and not reviewer:
        raise ValueError("A named engineering reviewer is required for Gorkha provenance approval")
    return {
        "event":event, "target_soil":"C", "source_sha256_A":sha[0],
        "source_sha256_B":sha[1], "additional_spectral_scale":1.,
        "acceleration_source_units":"g", "opensees_path_unit_factor":9.80665,
        "orientations_required":["XY","YX"],
        "gorkha_provenance_reviewed":event=="Gorkha" and bool(gorkha_processing_approved),
        "loma_end_policy":loma_end_policy if event=="Loma Prieta" else "as_recorded",
        "reviewer":reviewer,
        "seismomatch_source_scaling_logs_verified":False,
    }


def reconcile_loma_runtime_pair(records, *, policy="reject", reviewer=None):
    """Opt-in one-sample numerical extension for Loma Prieta, never edit files.

    Only accept exactly one timestep duration difference, identical dt and
    a named reviewer. No scaling, interpolation or truncation is performed.
    """
    if len(records)!=2:
        raise ValueError("Exactly two source component arrays required")
    arrays=[(list(values),float(dt),unit) for values,dt,unit in records]
    a,b=arrays
    if a[1]!=b[1] or a[2]!=b[2]:
        raise ValueError("Component sampling dt and units must match")
    difference=abs(len(a[0])-len(b[0]))
    if difference==0:
        return records,dict(status="NO_EXTENSION_NEEDED",added_samples=0)
    if difference!=1 or policy!="append_zero_reviewed" or not reviewer:
        raise ValueError("Loma Prieta may be extended by exactly ONE zero sample only after explicit review")
    shorter=0 if len(a[0])<len(b[0]) else 1
    arrays[shorter][0].append(0.)
    return arrays,dict(status="REVIEWED_IN_MEMORY_ZERO_END_EXTENSION",
      component_extended="A" if shorter==0 else "B",
      added_samples=1,extension_dt_s=a[1],reviewer=reviewer,
      original_source_files_changed=False,
      explicit_note="Numerical endpoint policy; not an alteration of SeismoMatch source bytes")
