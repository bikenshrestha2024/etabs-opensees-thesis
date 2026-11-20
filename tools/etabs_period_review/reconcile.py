"""Reconcile this thesis model's centered ETABS exports with NBC 105:2025."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

G = 9.80665
HEIGHT_M = 95.0
Z, IMPORTANCE, R_MU, OMEGA_U, OMEGA_S = 0.35, 1.0, 3.5, 1.4, 1.2
WALL_GROUPS = {
    "X": [(12.0, 0.6, 2, 2.0)] * 2,
    "Y": [(6.0, 0.6, 0, 0.0)] * 3,
}
# Recorded pre/post normalization from rows 8–9 of SCALING SUMMARY.
ARCHIVE = {
    "X": (275628.4068, 24842.19148714326, 25054.08657091004,
          0.8258723701035505, 0.8188875497011598, 1.763, 0.222),
    "Y": (275628.4068, 25608.6765781037, 26280.29509549768,
          1.115854001239674, 1.087337266278462, 2.427, 0.176),
}


def rayleigh(rows, *, torsion_tolerance_kNm=0.002):
    if not rows or len({row["story"] for row in rows}) != len(rows):
        raise ValueError("Rayleigh requires one row per storey.")
    for row in rows:
        values = [row[key] for key in (
            "weight_kN", "force_kN", "displacement_m", "rotation_rad", "torsion_kNm"
        )]
        if not all(math.isfinite(value) for value in values) or row["weight_kN"] <= 0:
            raise ValueError("Rayleigh inputs must be finite, with positive weights.")
        if abs(row["rotation_rad"]) > 1e-7 or abs(row["torsion_kNm"]) > torsion_tolerance_kNm:
            raise ValueError(f"{row['story']} fails the centered-case check.")
    inertia = math.fsum(row["weight_kN"] / G * row["displacement_m"] ** 2 for row in rows)
    work = math.fsum(row["force_kN"] * row["displacement_m"] for row in rows)
    if inertia <= 0 or work <= 0:
        raise ValueError("Rayleigh inertia and signed lateral work must be positive.")
    return {"period_s": 2 * math.pi * math.sqrt(inertia / work),
            "inertia_kN_m_s2": inertia, "work_kNm": work}


def force_scale(spectrum_shear, static_minimum):
    if not all(math.isfinite(value) and value > 0
               for value in (spectrum_shear, static_minimum)):
        raise ValueError("Base shears must be positive and finite.")
    return {"force": max(1.0, static_minimum / spectrum_shear), "displacement": 1.0}


def soil_c_modal_ch(period):
    if not 0 <= period <= 6:
        raise ValueError("The published modal spectrum is defined from 0 to 6 s.")
    if period < 0.1:
        return 1 + 15 * period
    if period <= 1:
        return 2.5
    if period <= 4:
        return 2.5 / period
    return 10 / period ** 2


def audit_native_spectrum(path):
    data = path.read_bytes()
    native_text = data.decode("latin-1")
    points = [
        (float(t), float(ch))
        for row in re.findall(r'FUNCTION "NBC Soil Type C" +TIMEVAL "([^"]+)"', native_text)
        for t, ch in zip(row.split()[::2], row.split()[1::2], strict=True)
    ]
    in_range = [(t, ch) for t, ch in points if 0 <= t <= 6]
    if (not in_range or in_range[0][0] != 0 or in_range[-1][0] != 6
            or any(right[0] <= left[0] for left, right in zip(points, points[1:]))):
        raise ValueError("Expected a strictly increasing native Soil C spectrum spanning 0 to 6 s.")
    error = max(abs(ch - soil_c_modal_ch(t)) for t, ch in in_range)
    if error > 0.000051:
        raise ValueError(f"Native Soil C ordinates differ from NBC Ch by up to {error:.7g}.")
    for axis, dof in (("X", 1), ("Y", 2)):
        scales = re.findall(
            rf'LOADCASE "RS{axis} P Delta" +ACCEL +"U{dof}" +FUNC +"NBC Soil Type C" +SF +([\d.]+)',
            native_text,
        )
        if len(scales) != 1 or abs(float(scales[0]) / 1000 - ARCHIVE[axis][4]) > 1e-7:
            raise ValueError(f"Archived {axis} acceleration scale does not match this E2K in mm/s².")
    return {"file": path.name, "sha256": hashlib.sha256(data).hexdigest(),
            "audited_ordinates_0_to_6_s": len(in_range), "max_absolute_ch_error": error,
            "ordinates_beyond_code_range": len(points) - len(in_range),
            "nbc_uls_excitation_m_per_s2": G * Z * IMPORTANCE / (R_MU * OMEGA_U)}


def stage_e2k(source, destination, result, *, empirical_only=False):
    """Prepare a separate ETABS analysis input with the verified Soil C baseline."""
    if destination.suffix.lower() != ".e2k":
        raise ValueError("The staged output must use an .e2k extension.")
    raw = source.read_bytes()
    audit = result["native_spectrum_audit"]
    if hashlib.sha256(raw).hexdigest() != audit["sha256"]:
        raise ValueError("E2K changed after spectrum verification.")
    native_text = raw.decode("latin-1")
    for axis, dof in (("X", 1), ("Y", 2)):
        direction = result["directions"][axis]
        if empirical_only:
            direction = direction["empirical_reference"]
        if direction["cd_uls"] is None:
            raise ValueError(f"{axis}: final ETABS input requires an active period.")
        static = rf'(SEISMIC "EQ{axis}"[^\r\n]+SHEARCOEFF )\d+(?:\.\d+)?( +HEIGHTEXPONENT )\d+(?:\.\d+)?'
        native_text, static_count = re.subn(
            static,
            lambda m: f"{m[1]}{direction['cd_uls']:.10f}{m[2]}{direction['k']:.9f}",
            native_text,
        )
        if static_count != 1:
            raise ValueError(f"Expected one ESM edit for axis {axis}.")
        if empirical_only:
            continue
        dynamic = rf'(LOADCASE "RS{axis} P Delta" +ACCEL +"U{dof}" +FUNC +"NBC Soil Type C" +SF +)[\d.]+'
        native_text, dynamic_count = re.subn(
            dynamic, lambda m: f"{m[1]}{audit['nbc_uls_excitation_m_per_s2'] * 1000:.6f}",
            native_text,
        )
        if dynamic_count != 1:
            raise ValueError(f"Expected one RS edit for axis {axis}.")
    with destination.open("xb") as stream:
        stream.write(native_text.encode("latin-1"))


def select_period(cap, automatic, manual_rayleigh=None, direct=None, *, allow_pending=False):
    for value in (cap, automatic, manual_rayleigh, direct):
        if value is not None and (not math.isfinite(value) or value <= 0):
            raise ValueError("Periods must be positive and finite.")
    if manual_rayleigh is not None and direct is not None:
        raise ValueError("Enter only one manual period per direction.")
    analytical = manual_rayleigh if manual_rayleigh is not None else automatic
    minimum = min(cap, analytical) if analytical is not None else None
    if direct is None and minimum is None:
        if allow_pending:
            return {"adopted_s": None, "nbc_minimum_s": None, "source": "EMPIRICAL_PDELTA_PENDING"}
        raise ValueError("A verified P-Delta period or manual period is required.")
    return {"adopted_s": direct if direct is not None else minimum, "nbc_minimum_s": minimum,
            "source": ("DIRECT_OVERRIDE" if direct is not None else
                       "MANUAL_ANALYTICAL_CAPPED" if manual_rayleigh is not None else
                       "AUTOMATIC_CAPPED")}


def soil_c_static_ch(period):
    if not 0 < period <= 6:
        raise ValueError("The model's published Soil C spectrum covers 0 < T ≤ 6 s.")
    return 2.5 if period <= 1 else soil_c_modal_ch(period)


def wall_geometry(axis):
    walls = []
    for length, thickness, openings, width in WALL_GROUPS[axis]:
        net_area = thickness * (length - openings * width)
        walls.append({"length_m": length, "thickness_m": thickness, "opening_count": openings,
                      "opening_width_m": width, "net_area_m2": net_area,
                      "aw_m2": net_area * (0.2 + min(length / HEIGHT_M, 0.9) ** 2)})
    aw = math.fsum(wall["aw_m2"] for wall in walls)
    return walls, aw, 0.075 / math.sqrt(aw) * HEIGHT_M ** 0.75


def static_parameters(period, total_weight):
    if period is None:
        return dict.fromkeys(("ch", "cd_uls", "cd_sls", "k", "updated_esm_minimum_kN"))
    ch = soil_c_static_ch(period)
    cd = ch * Z * IMPORTANCE / (R_MU * OMEGA_U)
    return {"ch": ch, "cd_uls": cd, "cd_sls": 0.2 * ch * Z * IMPORTANCE / OMEGA_S,
            "k": min(2, max(1, 1 + (period - 0.5) / 2)),
            "updated_esm_minimum_kN": cd * total_weight}


def empirical_reference(axis):
    _, _, empirical = wall_geometry(axis)
    return {"period_s": empirical, **static_parameters(empirical, ARCHIVE[axis][0])}


def matches_empirical_reference(axis, cd, exponent, base_shear):
    ref = empirical_reference(axis)
    return (abs(cd - ref["cd_uls"]) < 5.1e-7
            and abs(exponent - ref["k"]) < 5.1e-7
            and abs(base_shear - ref["updated_esm_minimum_kN"]) < 0.01)


def reconcile(spectrum=None, *, period_inputs):
    directions = {}
    for axis in WALL_GROUPS:
        total_weight, saved_shear, pre_normalization_shear, old_sf, saved_sf, ritz, tn = ARCHIVE[axis]
        walls, aw, empirical = wall_geometry(axis)
        cap = 1.25 * empirical
        selection = select_period(cap, **period_inputs[axis], allow_pending=True)
        adopted = selection["adopted_s"]
        static = static_parameters(adopted, total_weight)
        minimum = static["updated_esm_minimum_kN"]
        directions[axis] = {
            "walls": walls, "aw_m2": aw, "empirical_s": empirical, "empirical_cap_s": cap,
            "adopted_s": adopted, "ritz_s": ritz, "tn90_s": tn,
            "period_selection": selection,
            **static, "empirical_reference": empirical_reference(axis),
            "native_weight_kN": total_weight,
            "saved_esm_and_rs_kN": saved_shear,
            "archived_pre_normalization_rs_kN": pre_normalization_shear,
            "archived_pre_normalization_sf_m_per_s2": old_sf,
            "saved_normalized_sf_m_per_s2": saved_sf,
        }
        if spectrum:
            baseline = saved_shear * spectrum["nbc_uls_excitation_m_per_s2"] / saved_sf
            directions[axis]["projected_code_baseline_kN"] = baseline
            if minimum is not None:
                directions[axis]["projected_code_force_scaling"] = force_scale(baseline, minimum)
    return {"status": "RECONCILED_CALCULATION_NATIVE_REANALYSIS_PENDING",
            "height_m": HEIGHT_M, "gravity_m_per_s2": G,
            "directions": directions, "native_spectrum_audit": spectrum}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    directory = Path(__file__).resolve().parent
    parser.add_argument("--output", type=Path, default=directory / "Reconciliation.json")
    parser.add_argument("--e2k", type=Path, help="Audit the saved ETABS Soil C spectrum and excitation.")
    stage = parser.add_mutually_exclusive_group()
    stage.add_argument("--stage-e2k", type=Path, help="Write a final ETABS analysis input.")
    stage.add_argument("--stage-empirical", type=Path, help="Write a preliminary empirical-period ETABS input.")
    parser.add_argument("--pdelta-readback", type=Path, help="Verified P-Delta floor output JSON.")
    for axis in ("x", "y"):
        parser.add_argument(f"--manual-rayleigh-{axis}", type=float)
        parser.add_argument(f"--direct-t1-{axis}", type=float)
    arguments = parser.parse_args()
    if (arguments.stage_e2k or arguments.stage_empirical) and not arguments.e2k:
        parser.error("Staging requires --e2k.")
    spectrum = audit_native_spectrum(arguments.e2k) if arguments.e2k else None
    verified = {}
    if arguments.pdelta_readback:
        verified = json.loads(arguments.pdelta_readback.read_text(encoding="utf-8"))["directions"]
    inputs = {}
    for axis in ("x", "y"):
        label = axis.upper()
        readback = verified.get(label, {})
        automatic = None
        if (readback.get("empirical_reference_verified") is True
                and readback.get("pdelta_rayleigh_verified") is True
                and matches_empirical_reference(label, readback["native_cd"], readback["native_k"],
                                                readback["base_shear_kN"])):
            automatic = readback["period_s"]
        inputs[label] = {"automatic": automatic,
                         "manual_rayleigh": getattr(arguments, f"manual_rayleigh_{axis}"),
                         "direct": getattr(arguments, f"direct_t1_{axis}")}
    result = reconcile(spectrum, period_inputs=inputs)
    for axis, direction in result["directions"].items():
        if inputs[axis]["automatic"] is not None:
            record = verified[axis]
            direction["pdelta_rayleigh"] = {key: record[key] for key in (
                "case", "period_s", "max_cut_equivalent_eccentricity_m", "max_floor_rotation_rad"
            )}
    if arguments.stage_e2k:
        stage_e2k(arguments.e2k, arguments.stage_e2k, result)
    if arguments.stage_empirical:
        stage_e2k(arguments.e2k, arguments.stage_empirical, result, empirical_only=True)
    arguments.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(arguments.output)


if __name__ == "__main__":
    main()
