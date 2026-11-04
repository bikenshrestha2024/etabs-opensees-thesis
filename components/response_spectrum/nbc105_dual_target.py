"""NBC 105:2025 Eq. 4.1(2) target builder, RC shear-wall dual system.

The code uses the official MODAL/NLTHA spectral shape, not the ESM shape.
Source (GoN DUDBC), pp. 22–24 Table 4-1 and 2025 Table 5-2:
https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf

Each soil C/D case is a DIFFERENT target. The nominal source-matching
scaling factor is already embedded in the SeismoMatch matched waveform:
never multiply it a second time in the OpenSees Path timeSeries.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

SOURCE = "https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf"
SOIL = {
    "C": dict(Ta=0.1, Tc=1.0, Td=4.0, alpha=2.5),
    "D": dict(Ta=0.5, Tc=2.0, Td=5.0, alpha=2.25),
}
RC_DUAL_SHEAR_WALL = {
    "system": "RC_DUAL_RC_SHEAR_WALL",
    "R_mu_ULS": 3.5,
    "omega_u_ULS": 1.4,
    "omega_s_SLS": 1.2,
    "basis": "NBC 105:2025 Table 5-2, Dual Systems, RC shear wall (row 19)",
}


def _positive(value, name):
    try: result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name + " must be numeric") from exc
    if not math.isfinite(result) or result <= 0:
        raise ValueError(name + " must be positive and finite")
    return result


def ch_modal_nltha(T_s, soil):
    """Exact published Figure 4-2 / Eq 4.1(2), strictly 0 <= T <= 6 s."""
    if soil not in SOIL:
        raise ValueError("Select soil C or D explicitly")
    T = float(T_s)
    if not math.isfinite(T) or T < 0 or T > 6.:
        raise ValueError("NBC Fig 4-2 is specified only for 0..6 s; no silent extrapolation")
    p = SOIL[soil]
    ta, tc, td, alpha = (p[k] for k in ("Ta", "Tc", "Td", "alpha"))
    if T < ta:
        return 1. + (alpha - 1.) * T / ta
    if T < tc:
        return alpha
    if T < td:
        return alpha * tc / T
    return alpha * tc * td / (T*T)


def target_nltha_g(T_s, soil, *, zoning_Z, importance_I,
                   omega_u=RC_DUAL_SHEAR_WALL["omega_u_ULS"]):
    """Dimensionless C(T)/Omega_u in gravitational-acceleration units g.

    Do not apply this formula to SLS without a separate reviewed SLS target.
    """
    Z = _positive(zoning_Z, "zoning_Z")
    I = _positive(importance_I, "importance_I")
    omega = _positive(omega_u, "omega_u")
    if not math.isclose(omega, 1.4, abs_tol=1e-10):
        raise ValueError("RC dual wall system uses omega_u=1.4 in NBC Table 5-2")
    return ch_modal_nltha(T_s, soil) * Z * I / omega


def load_target_csv(path, *, expected_soil, expected_units="g"):
    """Explicit CSV input schema: T_s,Sa_g; reject hidden soil/unit changes.

    CSV itself is only a target data carrier. The caller must separately
    establish its originating Z, I, Omega, code edition and source SHA.
    """
    if expected_soil not in SOIL:
        raise ValueError("Expected soil label C or D")
    if expected_units != "g":
        raise ValueError("Expected spectrum ordinates in g")
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or not {"T_s", "Sa_g"}.issubset(reader.fieldnames):
            raise ValueError("Target CSV columns must be T_s,Sa_g")
        data = [(float(r["T_s"]), float(r["Sa_g"])) for r in reader]
    if len(data) < 3:
        raise ValueError("Target spectrum has fewer than three ordinates")
    previous = -1.
    for t,sa in data:
        if not (math.isfinite(t) and math.isfinite(sa) and 0 <= t <= 6
                and sa >= 0 and t > previous):
            raise ValueError("Target periods or acceleration invalid")
        previous = t
    return data


def verify_target_csv(path, soil, *, zoning_Z, importance_I,
                      abs_tolerance_g=1e-4):
    observed = load_target_csv(path, expected_soil=soil)
    tolerance = _positive(abs_tolerance_g, "abs_tolerance_g")
    mismatches = []
    for T, actual in observed:
        expected = target_nltha_g(T, soil, zoning_Z=zoning_Z, importance_I=importance_I)
        if abs(expected-actual) > tolerance:
            mismatches.append(dict(period_s=T, expected_g=expected,
                                   file_g=actual, diff_g=actual-expected))
    return dict(soil=soil, system=RC_DUAL_SHEAR_WALL["system"],
                target_source=SOURCE, source_rows=len(observed),
                status="TARGET_ORDINATES_MATCH_REVIEWED_PARAMETERS" if not mismatches
                else "TARGET_ORDINATES_DIFFER_FROM_NBC_FORMULA",
                mismatch_count=len(mismatches),
                first_mismatches=mismatches[:20],
                other_soil_target_verified=False,
                matched_accelerogram_spectra_verified=False,
                seismomatch_scaling_session_verified=False)


def write_target_spectra(folder, *, zoning_Z, importance_I,
                         start_s=0., end_s=6., step_s=.005):
    """Build distinct Soil C/D reference data; no event is assumed to match both."""
    start = float(start_s)
    end = float(end_s)
    step = _positive(step_s, "step_s")
    if not 0 <= start < end <= 6:
        raise ValueError("NBC Fig 4-2 target domain must be within 0..6 s")
    count = int(round((end-start)/step))
    if count < 2 or not math.isclose(start+count*step,end,abs_tol=1e-9):
        raise ValueError("Select a step that evenly divides the period range")
    root = Path(folder)
    root.mkdir(parents=True, exist_ok=True)
    files = {}
    for soil in ("C","D"):
        target = root / ("NBC105_2025_RC_DUAL_Soil_" + soil + "_ULS_Target_g.csv")
        with target.open("w",newline="",encoding="utf-8") as fh:
            writer=csv.writer(fh)
            writer.writerow(["T_s","Sa_g"])
            for i in range(count+1):
                T = start + step*i
                writer.writerow([f"{T:.9f}",f"{target_nltha_g(T,soil,zoning_Z=zoning_Z,importance_I=importance_I):.12g}"])
        files[soil] = str(target)
    metadata = dict(schema="NBC105_2025_RC_DUAL_C_D_TARGETS_V1",
        code_source=SOURCE, system=RC_DUAL_SHEAR_WALL,
        Z=float(zoning_Z), I=float(importance_I),
        target_kind="C_h(T) * Z * I / Omega_u_ULS",
        soil=SOIL,period_min_s=start,period_max_s=end,period_step_s=step,
        target_files=files,
        soil_type_selected_for_each_record=False,
        record_to_soil_mapping_provided=False,
        spectrum_match_approved=False,
        source_notes=[
          "Code Eq 4.1(2) is for modal/NLTHA spectrum, not equivalent static spectrum.",
          "Do not mix Soil C and D targets or assume both match the same record.",
          "Soil category requires Vs30/geotechnical justification for >40m buildings.",
          "No unreviewed extrapolation beyond 6 seconds.",
          "Already matched Acc(g) source Path factor remains 9.80665 for kN-m-s."
        ])
    filename=root/"NBC105_2025_RC_DUAL_C_D_Target_Metadata.json"
    filename.write_text(json.dumps(metadata,indent=2,allow_nan=False),encoding="utf-8")
    return metadata
