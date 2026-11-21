"""NBC 105:2025 clause 4 seismic hazard helpers (pure Python).

[REF NBC105-2025 §4, printed pp. 21-27] Elastic site spectrum C(T) = Ch(T) Z I
(Eq. 4.1(1)), spectral shape factor Ch(T) (Eq. 4.1(2) and Table 4-1), site
subsoil classification (Table 4-2, Vs,30 formula), the Kathmandu Valley
default Soil Type D table (Table 4-3), importance factor (Table 4-4),
serviceability spectrum (Eq. 4.2(1)) and vertical spectrum coefficient
(Eq. 4.3(1)). The functions are design-input calculations, never engineering
acceptance of a building or site.

Transcribed from the user-supplied printed pages (PDF pages 43-50) by viewing
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
    "select_soil_type", "default_soil_type_d", "validate_zoning_factor",
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


def select_soil_type(*, height_m, vs30=None, n_spt=None):
    """Return ``{soil, basis, issues}`` for the Table 4-2 classification.

    [REF NBC105-2025 §4.1.3.1, printed p. 24]
    Vs,30 is preferred; N_SPT is used only when Vs,30 is absent. For
    ``height_m > 40`` Vs,30 is mandatory: without it ``soil`` is None and an
    issue is reported. Does not apply the Kathmandu Valley default of
    §4.1.3.3; see ``default_soil_type_d``.
    """
    h = _finite(height_m, "height_m")
    issues = []
    if vs30 is not None:
        soil = soil_type_from_vs30(vs30)
        if n_spt is not None and soil_type_from_n_spt(n_spt) != soil:
            issues.append("N_SPT class differs from the Vs,30 class; Vs,30 governs")
        return {"soil": soil, "basis": "Vs30", "issues": issues}
    if h > MANDATORY_VS30_HEIGHT_M:
        issues.append(
            "Vs,30 is mandatory for buildings taller than 40 m (clause 4.1.3.1)")
        return {"soil": None, "basis": None, "issues": issues}
    if n_spt is not None:
        return {"soil": soil_type_from_n_spt(n_spt), "basis": "N_SPT",
                "issues": issues}
    issues.append("neither Vs,30 nor N_SPT was provided")
    return {"soil": None, "basis": None, "issues": issues}


def default_soil_type_d(district, municipality, ward=None):
    """Return True if Table 4-3 assigns Soil Type D by default to the site.

    [REF NBC105-2025 §4.1.3.3, printed p. 26]
    The default holds unless tests to 30 m demonstrate another class. A
    municipality or ward not in the table returns False (not listed, which
    is not a finding of any soil type). A partially listed municipality needs
    ``ward``; omitting it raises ValueError.
    """
    key = (str(district).strip().title(), str(municipality).strip().lower())
    entry = None
    for (d, m), wards in KATHMANDU_VALLEY_SOIL_D_SITES.items():
        if (d, m.lower()) == key:
            entry = wards
            break
    if entry is None:
        return False
    if entry == _ALL:
        return True
    if not entry:
        return False
    if ward is None:
        raise ValueError("ward is required for a partially listed municipality")
    return int(ward) in entry
