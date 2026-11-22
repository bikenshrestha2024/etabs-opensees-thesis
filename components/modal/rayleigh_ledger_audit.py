"""Pure validation helpers for NBC 105:2025 Rayleigh storey audits.

No ETABS/OpenSees solver imports. Inputs are already-exported model/ledger
records; geometry and weights must come from the matching source model.
"""
from __future__ import annotations
import math
from components.nbc105.constants import GRAVITY_M_S2
from components.nbc105.clause_05_dynamic_characteristics import rayleigh_period_s


def verify_storey_coverage(model_diaphragms, ledger_rows):
    """[REF docs/source/components/modal/rayleigh_ledger_audit.py.md]

    Reject stale, incomplete, duplicated or mismapped Rayleigh ledgers."""
    expected = [(int(d["storey_number"]), int(d["master_tag"])) for d in model_diaphragms]
    actual = [(int(r["story_number"]), int(r["master_node_tag"])) for r in ledger_rows]
    if not expected:
        raise ValueError("Model has no diaphragm inventory")
    if len(set(expected)) != len(expected) or len(set(actual)) != len(actual):
        raise ValueError("Repeated storey/master pair in model or ledger")
    if len({tag for _, tag in expected}) != len(expected):
        raise ValueError("Model diaphragm master tags are not unique")
    if len({tag for _, tag in actual}) != len(actual):
        raise ValueError("Rayleigh master tags are not unique")
    if set(expected) != set(actual):
        raise ValueError("Incomplete Rayleigh ledger: missing=%s; extra=%s" %
                         (sorted(set(expected) - set(actual)), sorted(set(actual) - set(expected))))
    return len(actual)


def verify_rayleigh_sum(rows, *, g=GRAVITY_M_S2):
    """[REF docs/source/components/modal/rayleigh_ledger_audit.py.md]

    Recalculate Rayleigh T from all participating storeys in SI units.

    Each row has weight_kN, force_kN and incremental displacement_m.
    Results must not be labelled NBC accepted without source/mass/stiffness review.
    """
    g = float(g)
    if not math.isfinite(g) or g <= 0 or not rows:
        raise ValueError("Positive gravity acceleration and at least one storey required")
    terms = []
    for i, row in enumerate(rows, 1):
        w, f, d = (float(row[key]) for key in
                   ("weight_kN", "force_kN", "displacement_m"))
        if not all(math.isfinite(v) for v in (w, f, d)) or w <= 0 or f <= 0:
            raise ValueError("Nonfinite or nonpositive Rayleigh weights/forces at row %s" % i)
        terms.append((w * d * d, f * d))
    numerator = math.fsum(t[0] for t in terms)
    sum_fidi = math.fsum(t[1] for t in terms)
    denominator = g * sum_fidi
    if numerator <= 0 or denominator <= 0:
        raise ValueError("Nonpositive Rayleigh quotient: check displacement sign and boundary conditions")
    period = rayleigh_period_s([float(r['weight_kN']) for r in rows],
                               [float(r['displacement_m']) for r in rows],
                               [float(r['force_kN']) for r in rows],g=g)
    return {"storey_count": len(rows), "numerator_kN_m2": numerator,
            "sum_Fi_di_kN_m": sum_fidi, "denominator_kN_m2_s2": denominator,
            "period_s": period, "gravity_m_s2": g,
            "status": "NUMERICAL_RECONSTRUCTION_ONLY"}


def verify_saved_rayleigh_axis(axis, *, expected_storeys=None):
    """Fail closed on saved NBC 105 Rayleigh period and kinematic evidence.

    [REF docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md]
    [REF components/inputs/project_workbooks.py import_project_inputs]

    This reconstructs numerical evidence only; it cannot certify ETABS
    stiffness, seismic mass, P-Delta, diaphragm constraints or real solver runs.
    """
    if not isinstance(axis, dict) or not isinstance(axis.get("rows"), list):
        raise ValueError("Rayleigh saved axis requires all recorded storey rows")
    rows = axis["rows"]
    if not rows:
        raise ValueError("Rayleigh saved axis has no storeys")
    if expected_storeys is not None and len(rows) != expected_storeys:
        raise ValueError("Rayleigh saved axis storey coverage differs from source")
    tags = [r.get("master_node") for r in rows if isinstance(r, dict)]
    if (len(tags) != len(rows) or any(isinstance(t, bool) or not isinstance(t, int) for t in tags)
            or len(set(tags)) != len(tags)):
        raise ValueError("Rayleigh saved axis contains invalid or repeated masters")
    if any(isinstance(r.get("constrained_floor_node_count"), bool)
           or not isinstance(r.get("constrained_floor_node_count"), int)
           or r["constrained_floor_node_count"] <= 0 for r in rows):
        raise ValueError("Rayleigh saved axis lacks physical constrained floor nodes")
    rec = verify_rayleigh_sum(rows)
    if rec["storey_count"] != len(rows):
        raise ValueError("Rayleigh saved axis reconstruction does not cover all storeys")
    for key, value in (
        ("period_s", rec["period_s"]),
        ("rayleigh_numerator_kN_m2", rec["numerator_kN_m2"]),
        ("rayleigh_denominator_gFiDi_kN_m2_s2", rec["denominator_kN_m2_s2"]),
        ("reference_force_total_kN", math.fsum(float(row["force_kN"]) for row in rows)),
    ):
        raw = axis.get(key)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError("Rayleigh saved axis missing numeric proof: " + key)
        if not math.isfinite(raw) or not math.isclose(raw, value, rel_tol=1e-8, abs_tol=1e-10):
            raise ValueError("Rayleigh saved axis reconstructed proof mismatch: " + key)
    kin = axis.get("kinematic_audit")
    if not isinstance(kin, dict) or kin.get("status") != "VERIFIED_FLOOR_TRANSLATIONS":
        raise ValueError("Rayleigh saved axis has no kinematic audit")
    if type(kin.get("steps")) is not int or kin["steps"] != 1:
        raise ValueError("Rayleigh saved axis requires the verified one-step reference solution")
    limits = {
        "pattern_factor": (1.0, 1e-10),
        "relative_reaction_error": (0.0, .001),
        "max_floor_translation_spread_m": (0.0, 1e-8),
    }
    for key, (target, limit) in limits.items():
        value = kin.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("Rayleigh saved axis missing finite kinematic evidence: " + key)
        if abs(value-target) > limit:
            raise ValueError("Rayleigh saved axis failed kinematic check: " + key)
    increment = kin.get("incremental_base_reaction_kN")
    if isinstance(increment, bool) or not isinstance(increment, (int, float)) or not math.isfinite(increment):
        raise ValueError("Rayleigh saved axis missing base reaction evidence")
    applied = math.fsum(float(row["force_kN"]) for row in rows)
    error = abs(increment + applied) / applied
    if error > .001 or not math.isclose(error, kin["relative_reaction_error"], rel_tol=1e-6, abs_tol=1e-8):
        raise ValueError("Rayleigh saved axis reaction balance contradicts stored forces")
    return rec


def verify_storey_elevations(model_diaphragms, ledger_rows, base_z_m, *,
                             tolerance_m=1e-6):
    """Require Rayleigh load heights to match assembled diaphragm elevations.

    [REF components/model/assembly.py story_ledger]
    [REF components/modal/rayleigh.py run]

    Rejects a ledger whose IDs match but elevation/height reference changed.
    """
    try:
        base = float(base_z_m)
        tol = float(tolerance_m)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Invalid Rayleigh geometric height basis") from exc
    if any(not math.isfinite(v) for v in (base, tol)) or tol < 0:
        raise ValueError("Invalid Rayleigh geometric height tolerance")
    verify_storey_coverage(model_diaphragms, ledger_rows)
    model_heights = {}
    for d in model_diaphragms:
        tag = int(d["master_tag"])
        xyz = d["master_xyz"]
        if len(xyz) != 3:
            raise ValueError("Rayleigh master coordinates must have 3 components")
        z = float(xyz[2])
        if not math.isfinite(z):
            raise ValueError("Nonfinite Rayleigh master elevation")
        model_heights[tag] = z-base
    for row in ledger_rows:
        tag = int(row["master_node_tag"])
        actual = float(row["height_m"])
        expected = model_heights[tag]
        if not math.isfinite(actual) or actual <= 0 or expected <= 0:
            raise ValueError("Invalid Rayleigh storey elevation relative to base")
        if abs(actual-expected) > tol:
            raise ValueError(
                f"Rayleigh storey {row['story_number']} ledger height {actual:g} m "
                f"differs from assembled diaphragm height {expected:g} m"
            )
    return len(ledger_rows)
