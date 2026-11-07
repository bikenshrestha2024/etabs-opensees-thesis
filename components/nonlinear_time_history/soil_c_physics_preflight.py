"""Soil C thesis NLTHA input evidence gate (not a substitute for an engineer).

Actual user-supplied basis:
  - Target workbook SHA256 fe513b2d...9c63a8 (Soil C, ULS C(T)/1.4)
  - Z=0.35; I=1; RC dual-wall R_mu=3.5; Omega_u=1.4.
  - Eight SeismoMatch matched A/B pairs in Acc(g); extra spectrum scale 1.
References: NBC 105:2025 §§4.1.1–4.1.3, 5.3, 9.3.1–9.3.3,
OpenSees Path / UniformExcitation official manuals.
This pure Python module does not solve or approve any structural model.
"""
from __future__ import annotations

import math

from components.nonlinear_time_history.nbc105_2025_audit import (
    nbc105_time_step_limit, scaling_period_range,
)

SOIL_C_INPUT_BASIS = {
    "soil": "C",
    "system": "RC_DUAL_RC_SHEAR_WALL",
    "Z": 0.35,
    "I": 1.0,
    "R_mu": 3.5,
    "omega_u": 1.4,
    "omega_s": 1.2,
    "target_plateau_g": 0.625,
    "matched_min_period_s": 0.05,
    "matched_max_period_s": 6.0,
    "target_workbook_sha256":
        "fe513b2dc8ad33dda870a2eeefba07f3c6ae8dc8ff92f332b20a323a9d9c63a8",
    "source_units": "g",
    "extra_spectral_multiplier": 1.0,
    "path_factor_m_s2_per_g": 9.80665,
}

def _positive(raw, name):
    try:
        value = float(raw)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Missing or invalid " + name) from exc
    if not math.isfinite(value) or value <= 0:
        raise ValueError(name + " must be positive and finite")
    return value

def _close(value, expected, name):
    if not math.isclose(_positive(value, name), expected, rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError(name + " conflicts with verified Soil C user target workbook")
    
def audit_soil_c_analysis_config(config):
    """Check immutable analysis-input values without inferring code approval.

    Applied extra factor of 1 means samples have ALREADY been matched, not
    that the original SeismoMatch scaling factors were all 1.
    """
    if not isinstance(config, dict):
        raise TypeError("run configuration must be a JSON object")
    # RTFC audit 2026-11: a misspelled intent must not bypass thesis-only
    # guards for the actual 25-storey nonlinear building.
    intent = config.get("analysis_intent")
    if intent not in ("RESEARCH_DIAGNOSTIC", "THESIS_NLTHA"):
        raise ValueError("analysis_intent must be RESEARCH_DIAGNOSTIC or THESIS_NLTHA")
    expected_hash = SOIL_C_INPUT_BASIS["target_workbook_sha256"]
    declared_hash = config.get("target_workbook_sha256")
    if declared_hash is not None and declared_hash.lower() != expected_hash:
        raise ValueError("Target workbook SHA256 differs from verified Soil C source")
    declared_target = config.get("target_spectrum_kind")
    if declared_target is not None and declared_target != "SOIL_C_ULS_C_OVER_OMEGA_U":
        raise ValueError("Soil C target must be the declared ULS C(T)/Omega_u curve")
    if config.get("input_record_class") not in (
        None, "MATCHED_SEISMOMATCH_SOIL_C"):
        raise ValueError("Soil C input record class must not be relabeled")
    if str(config.get("soil_type", "")).upper() != "C":
        raise ValueError("Primary research run requires Soil C, not relabeled D")
    if config.get("soil_c_primary_nltha") is not True:
        raise ValueError("Explicit Soil C primary mode is required")
    if config.get("source_records_already_scaled") is not True:
        raise ValueError("Matched Acc(g) records must declare preprocessing")
    _close(config.get("scale"), 1., "extra spectral scale")
    if config.get("diagnostic_excitation") != "XY":
        raise ValueError("Production input requires BOTH simultaneous XY components")
    if config.get("orientations") != ["XY", "YX"]:
        raise ValueError("Separate XY and YX orientations required, in this exact order")
    state = config.get("limit_state")
    if state not in ("ULS", "SLS"):
        raise ValueError("Limit state must be ULS or SLS")
    # ULS matched inputs should not be silently promoted into a separate
    # code-certified SLS matching exercise. Retain research comparisons.
    if state == "SLS" and config.get("analysis_intent") == "THESIS_NLTHA":
        if config.get("sls_seismic_input_basis_reviewed") is not True:
            raise ValueError("SLS matched-input/design-basis review required separately")
    if config.get("duration_s") is not None and config.get("analysis_intent") == "THESIS_NLTHA":
        raise ValueError("Thesis response must use entire record duration")
    if config.get("diagnostic_zero_damping") or config.get("diagnostic_mass_damping"):
        if config.get("analysis_intent") == "THESIS_NLTHA":
            raise ValueError("Thesis runs may not use diagnostic damping overrides")
    return dict(
        status="SOIL_C_CONFIG_NUMERICS_CONSISTENT_NOT_DESIGN_APPROVAL",
        soil_target=SOIL_C_INPUT_BASIS,
        limit_state=state,
        target_is_uls_spectrum=True,
        sls_source_application_review_required=(state=="SLS"),
        applied_path_acceleration_factor=9.80665,
        seismomatch_independent_scale_factors_verified=False,
        current_modal_periods_verified=False,
        material_and_wall_model_approved=False,
    )

def assess_modal_damping_and_time_step(config, eigenperiods_s, record_dt_s):
    """Explicit mode IDs and period-based dt screen; no fake Tn90 inference.

    [REF R10 NBC105-2025 §9.3.2.4 (dt bound)] [REF PEER TBI 2017; LATBSDC 2020 (inherent damping ratio)]

    Selection is from natural modes of a preloaded full 3D model.
    Uses 1-based modal indices as defined by the actual OpenSees eigen solve;
    does not claim a mode has 90% cumulative mass participation.
    """
    from components.nonlinear_time_history.damping_regions import (
        resolve_inherent_damping_ratio)
    periods = [_positive(p, "eigenperiod") for p in eigenperiods_s]
    selected = config.get("damping_reference_modes")
    if not (isinstance(selected, list) and len(selected)==2
            and all(type(x) is int for x in selected)
            and 1 <= selected[0] <= len(periods)
            and 1 <= selected[1] <= len(periods)
            and selected[0] != selected[1]):
        raise ValueError("Provide two distinct 1-based damping_reference_modes within calculated modes")
    a,b=selected
    modal = config.get("nbc105_2025_design_evidence")
    report=dict(
        damping_reference_modes_1_based=selected,
        damping_reference_periods_s=[periods[a-1],periods[b-1]],
        # [REF PEER TBI 2017; LATBSDC 2020; NBC105-2025 §8.1.1 (repo citation)]
        # Report the ratio actually configured (default 0.025; 0.05 only via
        # inherent_damping_five_percent). Previously a fixed 0.05 was written.
        damping_zeta_assumed=resolve_inherent_damping_ratio(config),
        modal_participation_90_percent_independently_verified=False,
        status="REVIEW_MODE_PARTICIPATION_AND_DAMPING_FORMULATION",
    )
    if modal is not None:
        for k in ("t1_x_s","t1_y_s","tn90_x_s","tn90_y_s"):
            _positive(modal.get(k),k)
        dt_limit=nbc105_time_step_limit(
            record_dt_s=record_dt_s,
            t1_x_s=modal["t1_x_s"], t1_y_s=modal["t1_y_s"],
            tn90_x_s=modal["tn90_x_s"], tn90_y_s=modal["tn90_y_s"])
        user_dt=_positive(config.get("dt_s"),"dt_s")
        windows={axis:scaling_period_range(
            modal["tn90_"+axis+"_s"],modal["t1_"+axis+"_s"],3.5)
            for axis in ("x","y")}
        report["nbc_limit_dt_s"]=dt_limit
        report["dt_within_code_bound"]=user_dt <= dt_limit+1e-12
        report["fit_windows_s"]=windows
        report["previous_005_to_6_window_covers_both_axes"]=all(
            low>=.05-1e-12 and high<=6+1e-12
            for low,high in windows.values())
        if config.get("analysis_intent")=="THESIS_NLTHA":
            if not report["dt_within_code_bound"]:
                raise ValueError("NBC 105 §9.3.2.4: chosen dt exceeds modal bound")
            if not report["previous_005_to_6_window_covers_both_axes"]:
                raise ValueError("NBC 105 §9.3.2.2: selected record fitting interval incomplete")
    elif config.get("analysis_intent")=="THESIS_NLTHA":
        raise ValueError("Thesis NLTHA must supply actual reviewed T1 and Tn90")
    return report

def evaluate_original_seismomatch_logs(evidence):
    """A metadata consistency gate; not an independent spectral matching test.

    An explicit named-reviewer claim and documentary log hash are needed.
    Never infer original factors from matched PGA/original PGA.
    """
    if not isinstance(evidence,dict):
        raise ValueError("SeismoMatch approval metadata is required")
    sha=evidence.get("scale_log_sha256")
    if not isinstance(sha,str) or len(sha)!=64 or any(c not in "0123456789abcdefABCDEF" for c in sha):
        raise ValueError("Original SeismoMatch scale log SHA256 required")
    if not evidence.get("engineering_reviewer"):
        raise ValueError("Named source reviewer required")
    a=_positive(evidence.get("factor_A"),"original factor_A")
    b=_positive(evidence.get("factor_B"),"original factor_B")
    adopted=_positive(evidence.get("adopted_common_pair_factor"),"adopted common pair factor")
    if not (.33<=a<=3 and .33<=b<=3):
        raise ValueError("NBC 105 9.3.2.2(c): independent factors must each lie in 0.33..3")
    if not math.isclose(adopted,min(a,b),rel_tol=1e-9):
        raise ValueError("NBC 105 9.3.2.2(d): adopted common factor must be min(A,B)")
    if evidence.get("matching_log_reviewed") is not True:
        raise ValueError("Original SeismoMatch matching session not reviewed")
    return dict(status="REVIEWED_METADATA_CONSISTENT_NOT_SPECTRAL_RECALCULATION",
                log_sha256=sha, factor_A=a,factor_B=b,
                adopted_common_pair_factor=adopted,
                applied_extra_opensees_spectral_scale=1.0,
                independent_spectral_match_recomputed=False)
