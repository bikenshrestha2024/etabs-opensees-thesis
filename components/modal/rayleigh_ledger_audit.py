"""Pure validation helpers for NBC 105:2025 Rayleigh storey audits.

No ETABS/OpenSees solver imports. Inputs are already-exported model/ledger
records; geometry and weights must come from the matching source model.
"""
from __future__ import annotations
import math


def verify_storey_coverage(model_diaphragms, ledger_rows):
    """Reject stale, incomplete, duplicated or mismapped Rayleigh ledgers."""
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


def verify_rayleigh_sum(rows, *, g=9.81):
    """Recalculate Rayleigh T from all participating storeys in SI units.

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
    period = 2 * math.pi * math.sqrt(numerator / denominator)
    return {"storey_count": len(rows), "numerator_kN_m2": numerator,
            "sum_Fi_di_kN_m": sum_fidi, "denominator_kN_m2_s2": denominator,
            "period_s": period, "gravity_m_s2": g,
            "status": "NUMERICAL_RECONSTRUCTION_ONLY"}
