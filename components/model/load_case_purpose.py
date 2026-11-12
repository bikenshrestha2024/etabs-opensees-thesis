"""Separate gravity-only load cases from NBC 105:2025 seismic weight.

[REF KNOWLEDGE_BASE/04_ENGINEERING_GATES/README.md;
     REVIEW_MAIN/01_GRAVITY/REVIEW.md]
This pure, read-only audit makes no structural modifications. It reports
what purpose a profile serves and which source patterns need human review.
Actual profile application is still performed in model/assembly.py.
"""
from __future__ import annotations

import math
import re

NBC105_2025_SOURCE = (
    "https://giwmscdnone.gov.np/media/files/"
    "NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf"
)
NBC105_2025_CLAUSE = "5.2 / Table 5-1, printed p. 30"
SEISMIC_FACTORS = {
    "DEAD": 1.0,
    "STORAGE_LIVE": 0.6,
    "OTHER_LIVE": 0.3,
    "ROOF_LIVE": 0.0,
}
GRAVITY_ONLY_FACTORS = {
    "DEAD": 1.0,
    "STORAGE_LIVE": 1.0,
    "OTHER_LIVE": 1.0,
    "ROOF_LIVE": 1.0,
}


def classify_load_pattern(pattern, *, explicit_category=None):
    """Classify a source pattern, with explicit independent categories.

    [REF NBC 105:2025 5.2 Table 5-1;
         KNOWLEDGE_BASE/04_ENGINEERING_GATES/README.md]
    Never treat unknown names as dead load or ordinary live load.
    ETABS load pattern type alone cannot prove storage occupancy.
    """
    if explicit_category is not None:
        category = str(explicit_category).strip().upper().replace("-", "_").replace(" ", "_")
        if category not in SEISMIC_FACTORS:
            raise ValueError(f"Invalid declared load category {explicit_category!r}")
        return category
    name = re.sub(r"[_\-]+", " ", str(pattern)).strip().casefold()
    if re.search(r"\broof\b", name) and re.search(r"\b(live|ll|imposed)\b", name):
        return "ROOF_LIVE"
    if re.search(r"\b(storage|warehouse|stock)\b", name) and re.search(
        r"\b(live|ll|storage|warehouse|stock)\b", name
    ):
        return "STORAGE_LIVE"
    if name in {"self weight", "dead", "dl", "sdead", "super dead", "superdead",
                "floor finish", "floor finishes", "wall", "partition", "partitions",
                "sdl", "permanent"}:
        return "DEAD"
    if name in {"live", "ll", "other live", "other ll", "imposed", "live load"}:
        return "OTHER_LIVE"
    return "UNCLASSIFIED"


def audit_load_case_purpose(profile, gravity_factors, mass_factors,
                            *, category_overrides=None, present_patterns=None,
                            tolerance=1e-9):
    """Audit case-purpose compatibility without changing factors or mass.

    [REF NBC 105:2025 5.2 Table 5-1;
         REVIEW_MAIN/01_GRAVITY/REVIEW.md]
    Unknown and mismatched factors are flagged, not overwritten.
    Distinguishes gravity-only comparisons from seismic mass and preload.
    """
    if not isinstance(gravity_factors, dict) or not isinstance(mass_factors, dict):
        raise TypeError("Explicit gravity_factors and mass_factors dicts are required")
    profile = str(profile)
    if profile == "GRAVITY_1.0D_1.0L":
        purpose = "FULL_GRAVITY_COMPARISON"
        expected_gravity = GRAVITY_ONLY_FACTORS
    elif profile in {"AS_CONFIGURED", "SEISMIC_SOURCE"}:
        purpose = "SEISMIC_PRELOAD_CONFIGURED_REVIEW_REQUIRED"
        expected_gravity = SEISMIC_FACTORS
    else:
        purpose = "OTHER_GRAVITY_COMBINATION_NOT_SEISMIC_WEIGHT"
        expected_gravity = None

    overrides = category_overrides or {}
    patterns = sorted(set(present_patterns) if present_patterns is not None
                      else (set(gravity_factors) | set(mass_factors)))
    rows, errors = [], []
    for pattern in patterns:
        category = classify_load_pattern(
            pattern, explicit_category=overrides.get(pattern))
        actual_gravity = gravity_factors.get(pattern)
        actual_mass = mass_factors.get(pattern)
        expected_g = (expected_gravity or {}).get(category)
        expected_m = SEISMIC_FACTORS.get(category)
        violations = []
        for label, value, expected in (
            ("gravity", actual_gravity, expected_g),
            ("seismic_mass", actual_mass, expected_m),
        ):
            if value is None:
                violations.append(f"MISSING_{label.upper()}_FACTOR")
            elif not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                violations.append(f"INVALID_{label.upper()}_FACTOR")
            elif expected is not None and not math.isclose(
                float(value), expected, abs_tol=tolerance, rel_tol=0.0
            ):
                violations.append(f"{label.upper()}_FACTOR_MISMATCH")
        if category == "UNCLASSIFIED":
            violations.append("LOAD_CATEGORY_REQUIRES_REVIEW")
        if violations:
            errors.append({"pattern": pattern, "issues": violations})
        rows.append({
            "pattern": pattern, "category": category,
            "gravity_factor": actual_gravity, "seismic_mass_factor": actual_mass,
            "expected_gravity_factor": expected_g,
            "expected_seismic_mass_factor": expected_m,
            "issues": violations,
        })
    status = "MATCHES_DECLARED_PURPOSE_FOR_CLASSIFIED_PATTERNS" if not errors else "REVIEW_REQUIRED"
    return {
        "profile": profile, "purpose": purpose, "status": status,
        "citation": NBC105_2025_CLAUSE, "source_url": NBC105_2025_SOURCE,
        "rows": rows, "issues": errors,
        "scope": (
            "Comparison of factors and load-pattern labels, not numerical load equivalence. "
            "Actual load contributions, mass assignment, P-Delta combinations, "
            "ETABS identity and occupancy categories require independent verification."
        ),
        "comparison_policy": (
            "GRAVITY_1.0D_1.0L and seismic-preload total reactions must not "
            "be compared as identical load states. Compare case-to-case only "
            "with identical source patterns and coefficients."
        ),
    }
