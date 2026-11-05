"""NBC 105:2025 §§5.4.2.1–5.4.2.2 centered-load floor-end torsion.

This module evaluates *paired, opposite physical ends of the same floor* in
the horizontal earthquake direction for a load applied through the floor
center of mass. It does not infer torsion from roof-only or diaphragm-master
translations, or from incompatible CQC envelope rows.

Per the official 2025 code, torsion irregularity is max/min > 1.5;
extreme torsional irregularity is max/min > 2.5, and is prohibited.
The ordinary 1.5 threshold is NOT max divided by average displacement.
All displacements must have matching units and result basis.
No solver model or load patterns are mutated.
"""
from __future__ import annotations
import math

SOURCE = ("https://giwmscdnone.gov.np/media/files/"
          "NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf")
TORSION_LIMIT=1.5
EXTREME_LIMIT=2.5


def check_floor_end_torsion(end_a_m, end_b_m, *, same_floor=True,
                            centered_cm_load=True, same_direction=True,
                            same_case=True, same_basis=True, zero_tolerance_m=1e-12):
    """Evaluate code ratio for *two reviewed opposite-end displacement values*.

    Input: end_a_m, end_b_m are SIGNED horizontal displacement increments in
    metres (not inter-storey drift). All evidence flags must describe the
    actual same floor/axis/force-pattern/result basis. No accidental eccentricity
    is used in the §5.4.2 reference case. Output has ratio, evidence status and
    'design_acceptance_blocked'. The function does not halt diagnostic analyses.
    """
    if not all((same_floor,centered_cm_load,same_direction,same_case,same_basis)):
        return dict(ratio=None,status="NOT EVALUATED",torsion=False,extreme=False,
                    design_acceptance_blocked=True,
                    reason="Opposite-end, same-floor, same-axis, centered-CM case/basis evidence is missing.")
    a=float(end_a_m);b=float(end_b_m);tol=float(zero_tolerance_m)
    if not all(math.isfinite(x) for x in (a,b,tol)) or tol<0:
        raise ValueError("Displacements and zero tolerance must be finite; tolerance cannot be negative.")
    high=max(abs(a),abs(b));low=min(abs(a),abs(b))
    if high<=tol:
        return dict(ratio=None,status="NOT EVALUATED",torsion=False,extreme=False,
                    design_acceptance_blocked=True,
                    reason="Both end displacements are zero/near zero: torsion ratio undefined.")
    if low<=tol:
        return dict(ratio=None,status="UNBOUNDED",torsion=True,extreme=True,
                    design_acceptance_blocked=True,
                    reason="Minimum end displacement is zero/near zero; ratio is unbounded. Inspect model and load case.")
    ratio=high/low
    extreme=ratio>EXTREME_LIMIT
    torsion=ratio>TORSION_LIMIT
    return dict(ratio=ratio,status="EXTREME TORSION" if extreme else
                "TORSIONAL IRREGULARITY" if torsion else "NO TORSION TRIGGER",
                torsion=torsion,extreme=extreme,
                design_acceptance_blocked=extreme,
                reason=("NBC 105:2025 §5.4.2.2 prohibits extreme torsional irregularity; revise configuration."
                        if extreme else "Computed for centered center-of-mass lateral loading; check input evidence."))


def check_torsional_irregularity(rows):
    """Check explicit same-case floor-end records without silently joining rows.

    Each row: limit_state, case, axis, storey, end_a_m, end_b_m,
    centered_cm_load (boolean), same_end_basis (boolean).
    Missing/contradictory source evidence reports NOT EVALUATED.
    Duplicate case-state-axis-storey records are rejected. A ULS result
    cannot be silently relabelled SLS and vice versa.
    """
    results=[];seen=set()
    for row in rows:
        state=str(row.get("limit_state","")).upper()
        axis=str(row.get("axis","")).upper()
        if state not in ("ULS","SLS") or axis not in ("X","Y"):
            raise ValueError("Each torsion row requires explicit ULS/SLS and X/Y.")
        key=(state,str(row.get("case","")),axis,str(row.get("storey","")))
        if not key[1] or not key[3]:
            raise ValueError("Each row requires an explicit case and storey.")
        if key in seen:raise ValueError("Duplicate floor/case torsion record: "+repr(key))
        seen.add(key)
        verified=row.get("centered_cm_load") is True and row.get("same_end_basis") is True
        if row.get("end_a_m") is None or row.get("end_b_m") is None:
            result=dict(ratio=None,status="NOT EVALUATED",torsion=False,extreme=False,
                        design_acceptance_blocked=True,reason="One or both physical end responses missing.")
        else:
            result=check_floor_end_torsion(
                row["end_a_m"],row["end_b_m"],centered_cm_load=verified)
        results.append({**row,**result, "clause":"NBC 105:2025 §§5.4.2.1–5.4.2.2",
                        "ratio_basis":"max(abs(U_end_A),abs(U_end_B))/min(abs(U_end_A),abs(U_end_B))",
                        "source":SOURCE})
    return results
