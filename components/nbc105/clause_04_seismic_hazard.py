"""NBC 105:2025 clause 4 seismic hazard helpers (pure Python).

[REF NBC105-2025 §4, printed pp. 21-27] Elastic site spectrum C(T) = Ch(T) Z I
(Eq. 4.1(1)), spectral shape factor Ch(T) (Eq. 4.1(2) and Table 4-1), site
subsoil classification (Table 4-2, Vs,30 formula), the Kathmandu Valley
default Soil Type D table (Table 4-3), importance factor (Table 4-4),
serviceability spectrum (Eq. 4.2(1)) and vertical spectrum coefficient
(Eq. 4.3(1)). The functions are design-input calculations, never engineering
acceptance of a building or site.

Transcribed from the user-supplied printed pages (PDF pages 42-50) by viewing
the page images. Printed page numbers in the source PDF: Table 4-3 and
Table 4-4 are both on a page numbered 26; the Figure 4-3 page is numbered 25.
The Z value is NOT tabulated here: Table C-1 of Annex C (listed
municipalities) and Figure 4-3 interpolation are not transcribed, so
``validate_zoning_factor`` only range-checks a caller-supplied Z.
"""
from __future__ import annotations

import math
from typing import Sequence

__all__ = [
    "TABLE_4_1", "T_MAX_S", "VERTICAL_LOADING_CASES",
    "KATHMANDU_VALLEY_SOIL_D_SITES", "spectral_shape_factor",
    "importance_factor", "elastic_site_spectrum", "serviceability_spectrum",
    "vertical_spectrum_coefficient", "vs30_from_layers",
    "soil_type_from_vs30", "soil_type_from_n_spt", "soil_type_from_cu",
    "select_soil_type", "VS30_REQUIRED_ISSUE_CODE", "VS30_REQUIRED_ISSUE",
    "default_soil_type_d", "validate_zoning_factor",
]

# [REF NBC105-2025 §4.1.2, printed p. 24] Table 4-1.
TABLE_4_1 = {
    "A": {"Ta": 0.1, "Tc": 0.5, "Td": 4.0, "alpha": 2.5},
    "B": {"Ta": 0.1, "Tc": 0.7, "Td": 4.0, "alpha": 2.5},
    "C": {"Ta": 0.1, "Tc": 1.0, "Td": 4.0, "alpha": 2.5},
    "D": {"Ta": 0.5, "Tc": 2.0, "Td": 5.0, "alpha": 2.25},
}
# [REF NBC105-2025 §4.1.2, printed p. 23] Eq. 4.1(2) is defined for T <= 6 s.
T_MAX_S = 6.0
ZONING_FACTOR_MAX = 0.4
MANDATORY_VS30_HEIGHT_M = 40.0
_METHODS = ("equivalent_static", "dynamic")

# [REF NBC105-2025 §4.3, printed p. 27] Conditions a) to e).
VERTICAL_LOADING_CASES = (
    "a) horizontal or nearly horizontal structural members spanning 20 m or more",
    "b) horizontal or nearly horizontal cantilever components longer than 5 m",
    "c) horizontal or nearly horizontal pre-stressed components",
    "d) beams supporting columns",
    "e) base-isolated structures",
)

_ALL = "ALL"
_NIL = frozenset()


def _wards(*parts):
    out = set()
    for part in parts:
        out.update(range(part[0], part[1] + 1) if isinstance(part, tuple)
                   else (part,))
    return frozenset(out)


# [REF NBC105-2025 §4.1.3.3, printed p. 26] Table 4-3, 21 rows, transcribed
# from the page image. The Kathmandu Metropolitan City row prints the ward
# list ending "...,30,32,32"; the duplicate 32 is kept once as ward 32 and may
# be a misprint (for example for 31 or 33); confirm with the Department.
KATHMANDU_VALLEY_SOIL_D_SITES = {
    ("Kathmandu", "Budhanilkantha Municipality"): _NIL,
    ("Kathmandu", "Chandragiri Municipality"): _NIL,
    ("Kathmandu", "Gokarneswor Municipality"): _NIL,
    ("Kathmandu", "Kageswori Manahara Municipality"): _wards(8, 9),
    ("Kathmandu", "Kathmandu Metropolitan City"): _wards(1, 2, 5, (9, 30), 32),
    ("Kathmandu", "Kirtipur Municipality"): _wards(10),
    ("Kathmandu", "Nagarjun Municipality"): _wards(2, 4, 9),
    ("Kathmandu", "Sankharapur Municipality"): _NIL,
    ("Kathmandu", "Tarakeswor Municipality"): _wards(4, 8, 9, 10, 11),
    ("Kathmandu", "Tokha Municipality"): _wards((4, 11)),
    ("Lalitpur", "Bagmati Rural Municipality"): _NIL,
    ("Lalitpur", "Dakshinkali Municipality"): _NIL,
    ("Lalitpur", "Godawari Municipality"): _NIL,
    ("Lalitpur", "Konjyosom Rural Municipality"): _NIL,
    ("Lalitpur", "Lalitpur Metropolitan City"): _wards(
        (1, 4), (6, 13), 16, 17, 19, 20),
    ("Lalitpur", "Mahalaxmi Municipality"): _wards((1, 5), 7),
    ("Lalitpur", "Mahankal Rural Municipality"): _NIL,
    ("Bhaktapur", "Bhaktapur Municipality"): _ALL,
    ("Bhaktapur", "Changunarayan Municipality"): _wards(2),
    ("Bhaktapur", "Madhyapur Thimi Municipality"): _ALL,
    ("Bhaktapur", "Suryabinayak Municipality"): _wards(2, 3, 5, 6),
}


def _finite(value, name):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def spectral_shape_factor(period_s, soil, *, method):
    """Return Ch(T) of Eq. 4.1(2) with the Table 4-1 parameters.

    [REF NBC105-2025 §4.1.2, printed pp. 22-24]
    ``method="equivalent_static"`` uses Ta = 0 (Table 4-1 footnote, Figure
    4-1), so Ch = alpha for 0 <= T < Tc. ``method="dynamic"`` (modal response
    spectrum, nonlinear time history, vertical loading, parts and
    components; Figure 4-2) uses the full equation with Ta from Table 4-1.
    Rejects T < 0, NaN, T > 6 s, unknown soil or method; never extrapolates.
    """
    if method not in _METHODS:
        raise ValueError(f"method must be one of {_METHODS}")
    if soil not in TABLE_4_1:
        raise ValueError("soil must be one of A, B, C, D")
    t = float(period_s)
    if math.isnan(t) or t < 0.0:
        raise ValueError("period_s must be a number >= 0")
    if t > T_MAX_S:
        raise ValueError("period_s above 6 s is outside Eq. 4.1(2)")
    p = TABLE_4_1[soil]
    alpha, tc, td = p["alpha"], p["Tc"], p["Td"]
    ta = 0.0 if method == "equivalent_static" else p["Ta"]
    if t < ta:
        return 1.0 + (alpha - 1.0) * t / ta
    if t < tc:
        return alpha
    if t < td:
        return alpha * tc / t
    return alpha * tc * td / (t * t)


def importance_factor(importance_class, *, disaster_shelter=False):
    """Return I of Table 4-4: class 1 -> 1.0, 2 -> 1.25, 3 -> 1.5.

    [REF NBC105-2025 §4.1.5, printed p. 26]
    Footnote 2: 1.5 applies to class II facilities used as a disaster
    shelter. ``disaster_shelter=True`` for class 1 is rejected because the
    footnote concerns class II only.
    """
    if isinstance(importance_class, bool) or importance_class not in (1, 2, 3):
        raise ValueError("importance_class must be 1, 2 or 3")
    if disaster_shelter and importance_class == 1:
        raise ValueError("disaster_shelter footnote applies to class II facilities")
    if importance_class == 1:
        return 1.0
    if importance_class == 2:
        return 1.5 if disaster_shelter else 1.25
    return 1.5


def validate_zoning_factor(z):
    """Return Z after a range check only (finite, 0 < Z <= 0.4).

    [REF NBC105-2025 §4.1.4, printed p. 26]
    Figure 4-3 contours span 0.25 to 0.40. For cities/municipalities listed
    in Table C-1 of Annex C the table value governs over Figure 4-3
    interpolation; Annex C is not transcribed here, so the caller supplies Z.
    """
    value = _finite(z, "z")
    if not 0.0 < value <= ZONING_FACTOR_MAX:
        raise ValueError("z must satisfy 0 < Z <= 0.4")
    return value


def elastic_site_spectrum(period_s, soil, z, importance_factor_i, *, method):
    """Return C(T) = Ch(T) Z I.

    [REF NBC105-2025 §4.1.1, printed p. 22]
    Eq. 4.1(1).
    """
    zone = validate_zoning_factor(z)
    i_factor = _finite(importance_factor_i, "importance_factor_i")
    if i_factor <= 0.0:
        raise ValueError("importance_factor_i must be positive")
    return spectral_shape_factor(period_s, soil, method=method) * zone * i_factor


def serviceability_spectrum(period_s, soil, z, importance_factor_i, *, method):
    """Return Cs(T) = 0.20 C(T).

    [REF NBC105-2025 §4.2, printed p. 27]
    Eq. 4.2(1).
    """
    return 0.20 * elastic_site_spectrum(
        period_s, soil, z, importance_factor_i, method=method)


def vertical_spectrum_coefficient(z):
    """Return Cv(Tv) = 2/3 Z.

    [REF NBC105-2025 §4.3, printed p. 27]
    Eq. 4.3(1). Applies to the cases in ``VERTICAL_LOADING_CASES``.
    """
    return 2.0 / 3.0 * validate_zoning_factor(z)


def vs30_from_layers(layers: Sequence[tuple[float, float]]):
    """Return Vs,30 = 30 / sum(hi/Vi) for (thickness m, Vs m/s) layers.

    [REF NBC105-2025 §4.1.3.2, printed p. 24]
    Thicknesses must sum to 30 m (within 1e-6), the top 30 m.
    """
    if not layers:
        raise ValueError("layers must not be empty")
    total_h = 0.0
    travel = 0.0
    for thickness, velocity in layers:
        h = _finite(thickness, "thickness")
        v = _finite(velocity, "velocity")
        if h <= 0.0 or v <= 0.0:
            raise ValueError("layer thickness and velocity must be positive")
        total_h += h
        travel += h / v
    if abs(total_h - 30.0) > 1e-6:
        raise ValueError("layer thicknesses must sum to 30 m")
    return 30.0 / travel


def soil_type_from_vs30(vs30):
    """Return soil type from Table 4-2: >800 A, >350 B, >150 C, else D.

    [REF NBC105-2025 §4.1.3.1, printed p. 25]
    Upper limits are inclusive (350 < Vs,30 <= 800 is B; Vs,30 <= 150 is D).
    """
    v = _finite(vs30, "vs30")
    if v <= 0.0:
        raise ValueError("vs30 must be positive")
    if v > 800.0:
        return "A"
    if v > 350.0:
        return "B"
    if v > 150.0:
        return "C"
    return "D"


def soil_type_from_n_spt(n):
    """Return soil type from N_SPT: >50 B, 10 to 50 C, <10 D.

    [REF NBC105-2025 §4.1.3.1, printed p. 25]
    Table 4-2 gives no N_SPT value for Soil Type A ("-"), so A is never
    returned from N_SPT.
    """
    value = _finite(n, "n")
    if value < 0.0:
        raise ValueError("n must be >= 0")
    if value > 50.0:
        return "B"
    if value >= 10.0:
        return "C"
    return "D"


def soil_type_from_cu(cu_kpa):
    """Return soil type from Cu (kPa): >250 B, 25 to 250 C, <25 D.

    [REF NBC105-2025 §4.1.3.1, printed p. 25]
    Table 4-2 gives no Cu value for Soil Type A ("-"), so A is never
    returned from Cu.
    """
    value = _finite(cu_kpa, "cu_kpa")
    if value < 0.0:
        raise ValueError("cu_kpa must be >= 0")
    if value > 250.0:
        return "B"
    if value >= 25.0:
        return "C"
    return "D"


VS30_REQUIRED_ISSUE_CODE = "VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED"
VS30_REQUIRED_ISSUE = (
    VS30_REQUIRED_ISSUE_CODE + ": clause 4.1.3.1 (printed p. 24) requires Vs,30 for "
    "buildings higher than 40 m; Vs,30 is optional for this thesis, "
    "USER_DECLARED 2026-11-21")


def select_soil_type(*, height_m, vs30=None, n_spt=None):
    """Return ``{soil, basis, issues}`` for the Table 4-2 classification.

    [REF NBC105-2025 §4.1.3.1, printed p. 24]
    Vs,30 is preferred; N_SPT is used only when Vs,30 is absent. For
    ``height_m > 40`` clause 4.1.3.1 requires Vs,30. That requirement is
    optional for this thesis (USER_DECLARED 2026-11-21) but stays documented:
    without Vs,30 the result carries the issue ``VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED``
    (``VS30_REQUIRED_ISSUE``) and nothing is raised. ``soil`` is then taken from
    N_SPT when it is given and is None otherwise. Does not apply the Kathmandu
    Valley default of §4.1.3.3; see ``default_soil_type_d``.
    """
    h = _finite(height_m, "height_m")
    if h <= 0:
        raise ValueError("height_m must be positive")
    issues = []
    if vs30 is not None:
        soil = soil_type_from_vs30(vs30)
        if n_spt is not None and soil_type_from_n_spt(n_spt) != soil:
            issues.append("N_SPT class differs from the Vs,30 class; Vs,30 governs")
        return {"soil": soil, "basis": "Vs30", "issues": issues}
    if h > MANDATORY_VS30_HEIGHT_M:
        issues.append(VS30_REQUIRED_ISSUE)
    if n_spt is not None:
        return {"soil": soil_type_from_n_spt(n_spt), "basis": "N_SPT",
                "issues": issues}
    issues.append("neither Vs,30 nor N_SPT was provided")
    return {"soil": None, "basis": None, "issues": issues}


_NAME_SUFFIXES = (" rural municipality", " metropolitan city", " municipality")


def _norm_name(text):
    return " ".join(str(text).split()).lower()


def _name_stem(norm):
    for suffix in _NAME_SUFFIXES:
        if norm.endswith(suffix):
            return norm[: -len(suffix)]
    return norm


def _find_table_4_3_entry(district, municipality):
    """Look up a Table 4-3 row, ignoring case and extra whitespace.

    A name matches if it equals the printed name (for example "Kirtipur
    Municipality") or the printed name without its generic suffix
    ("Municipality", "Metropolitan City", "Rural Municipality"; for example
    "Kirtipur"). A stem shared by two rows of one district would be ambiguous
    and is not matched. No other alias is used.
    """
    dist, name = _norm_name(district), _norm_name(municipality)
    rows = [(_norm_name(m), w) for (d, m), w in KATHMANDU_VALLEY_SOIL_D_SITES.items()
            if _norm_name(d) == dist]
    for full, wards in rows:
        if full == name:
            return wards
    stems = [(_name_stem(full), wards) for full, wards in rows]
    matches = [wards for stem, wards in stems if stem == name]
    if len(matches) == 1 and sum(1 for stem, _ in stems if stem == name) == 1:
        return matches[0]
    return None


def default_soil_type_d(district, municipality, ward=None):
    """Return True if Table 4-3 assigns Soil Type D by default to the site.

    [REF NBC105-2025 §4.1.3.3, printed p. 26]
    The default holds unless tests to 30 m demonstrate another class. Names
    are matched ignoring case and surrounding whitespace, and the generic
    suffix of the printed municipality name may be omitted ("Kirtipur" for
    "Kirtipur Municipality"). A municipality or ward not in the table
    returns False (not listed, which is not a finding of any soil type). A
    partially listed municipality needs ``ward``; omitting it raises
    ValueError.
    """
    entry = _find_table_4_3_entry(district, municipality)
    if entry is None:
        return False
    if entry == _ALL:
        return True
    if not entry:
        return False
    if ward is None:
        raise ValueError("ward is required for a partially listed municipality")
    return int(ward) in entry


# --- Table 4-4 occupancy classification (owner ruling 9d) ---
OCCUPANT_LIMIT_PERSONS = 500

# Printed Table 4-4 structure names, keyed by a stable token (printed p. 26).
OCCUPANCY_CLASS = {
    # Class I (I = 1.0): ordinary structures not falling in classes II and III
    "residence": 1, "apartments": 1, "offices": 1, "banks": 1, "financial_institutions": 1,
    "commercial_buildings": 1, "hospitality_buildings": 1, "factory_buildings": 1,
    # Class II (I = 1.25)
    "schools": 2, "colleges": 2, "cinemas": 2, "assembly_buildings": 2, "shopping_malls": 2,
    "convention_halls": 2, "temples": 2, "monumental_structures": 2, "police_stations": 2,
    "emergency_vehicle_shelters": 2, "stadiums": 2, "airport_terminals": 2,
    "food_storage_structures": 2, "emergency_relief_stores": 2, "water_works_and_towers": 2,
    "radio_television_facilities": 2, "telephone_exchanges": 2, "transmission_facilities": 2,
    "senior_rescue_relief_offices_and_quarters": 2,
    # Class III (I = 1.5)
    "hospitals": 3, "fire_stations": 3, "police_headquarters": 3, "air_traffic_control": 3,
    "power_stations": 3, "gas_petroleum_distribution": 3, "dangerous_substance_structures": 3,
}


def classify_importance(categories, *, occupant_count=None, declared_class=None,
                        disaster_shelter=False):
    """Table 4-4 importance class and factor from occupancy categories.

    [REF NBC105-2025 §4.1.5 Table 4-4, printed p. 26]
    The governing class is the highest class among the listed ``categories``
    (tokens of ``OCCUPANCY_CLASS``). Class I is limited to occupancy "less than
    500 persons" and class II includes "any other buildings designed to
    accommodate more than 500 persons": a class I category with more than 500
    occupants is class II. Exactly 500 is not printed for either class; it is
    treated as class II (conservative) and flagged. If ``occupant_count`` is
    None for a class I category the result carries
    CLASS_I_OCCUPANCY_UNVERIFIED. ``declared_class`` (the class the project
    adopted) is cross-checked: below the table is DECLARED_BELOW_TABLE_4_4,
    above it is DECLARED_ABOVE_TABLE_4_4 (allowed, more conservative).
    ``disaster_shelter`` applies footnote 2 (I = 1.5) to class II facilities.
    """
    if isinstance(categories, str) or not categories:
        raise ValueError("categories must be a non-empty list of Table 4-4 category tokens")
    unknown = [c for c in categories if c not in OCCUPANCY_CLASS]
    if unknown:
        raise ValueError("unknown Table 4-4 category: " + ", ".join(map(str, unknown)))
    flags = []
    cls = max(OCCUPANCY_CLASS[c] for c in categories)
    if occupant_count is not None:
        n = _finite(occupant_count, "occupant_count")
        if n < 0:
            raise ValueError("occupant_count must be >= 0")
        if cls == 1 and n >= OCCUPANT_LIMIT_PERSONS:
            cls = 2
            flags.append("OCCUPANCY_EXACTLY_500_NOT_PRINTED_TREATED_AS_CLASS_II" if n == OCCUPANT_LIMIT_PERSONS
                         else "OCCUPANCY_ABOVE_500_CLASS_II")
    elif cls == 1:
        flags.append("CLASS_I_OCCUPANCY_UNVERIFIED")
    shelter = bool(disaster_shelter)
    if shelter and cls == 1:
        raise ValueError("disaster_shelter footnote applies to class II facilities")
    factor = importance_factor(cls, disaster_shelter=shelter and cls == 2)
    status = "CLASSIFIED"
    if declared_class is not None:
        if isinstance(declared_class, bool) or declared_class not in (1, 2, 3):
            raise ValueError("declared_class must be 1, 2 or 3")
        if declared_class < cls:
            status = "DECLARED_BELOW_TABLE_4_4"
        elif declared_class > cls:
            status = "DECLARED_ABOVE_TABLE_4_4"
        else:
            status = "DECLARED_MATCHES_TABLE_4_4"
    if status != "DECLARED_BELOW_TABLE_4_4" and "CLASS_I_OCCUPANCY_UNVERIFIED" in flags:
        status = "CLASSIFIED_OCCUPANCY_UNVERIFIED" if declared_class is None else status
    return {"importance_class": cls, "importance_factor": factor, "declared_class": declared_class,
            "status": status, "flags": flags, "categories": list(categories),
            "occupant_count": occupant_count, "disaster_shelter": shelter and cls == 2,
            "conforming": status != "DECLARED_BELOW_TABLE_4_4"}


__all__ += ["OCCUPANT_LIMIT_PERSONS", "OCCUPANCY_CLASS", "classify_importance"]
