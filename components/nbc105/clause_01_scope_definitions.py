"""NBC 105:2025 clause 1 scope, definitions and notations (pure Python).

[REF NBC105-2025 §1, printed pp. 1-9] Title (1.1), scope (1.2), definitions
(1.3), notations (1.4) and units (1.5). Only the machine-checkable parts are
coded: the scope applicability lists (materials, systems referred to
specialist literature, no height limit stated), the printed notation list as
data (symbol, meaning, unit, printed page), the g = 9.81 m/s^2 value printed on
p. 7, and the numeric thresholds that appear inside definitions (dual system
25 %, soft story 70 % / 80 %, flexible diaphragm 2 times, design basis
earthquake 2/3 of MCE, 5 % response-spectrum damping as the commonly taken
value). Prose-only definitions are recorded in
``docs/nbc105/clause_01_scope_definitions_matrix.md`` as DEFINITION_ONLY.

Transcribed from the user-supplied printed pages (PDF pages 22-30, printed
page = PDF page - 21, the foot number was checked on every page). The printed
notation list has no unit column; only g and H print a unit. Other units are
derived from clause 1.5 (SI: kg, m, s, Pa, N) and marked ``SI_DERIVED``.
Unit-test conformance only, never engineering acceptance of a building.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence

from components.nbc105.constants import PRINTED_PAGE_OFFSET

__all__ = [
    "Notation", "NOTATIONS", "notation", "notation_page_counts",
    "printed_gravity_m_s2", "pdf_page_for_printed",
    "SCOPE_MATERIALS", "SPECIALIST_LITERATURE_SYSTEMS", "SCOPE_HEIGHT_LIMIT_M",
    "EARLIER_VERSION", "scope_check",
    "DUAL_SYSTEM_MIN_FRAME_SHARE", "SOFT_STORY_ADJACENT_RATIO",
    "SOFT_STORY_THREE_ABOVE_RATIO", "FLEXIBLE_DIAPHRAGM_DEFORMATION_RATIO",
    "DESIGN_BASIS_EARTHQUAKE_MCE_FRACTION", "RESPONSE_SPECTRUM_COMMON_DAMPING_RATIO",
    "is_soft_story", "is_flexible_diaphragm", "dual_system_frame_share",
    "dual_system_frame_share_ok", "design_basis_earthquake_from_mce",
    "ductility_factor", "overstrength_factor", "eccentricity_m",
]

# [REF NBC105-2025 §1.1, printed p. 1] The code revises the earlier version.
EARLIER_VERSION = "NBC 105: 1994 Seismic Design of Buildings in Nepal"

# [REF NBC105-2025 §1.2, printed p. 1] Buildings of these materials are covered.
SCOPE_MATERIALS = ("reinforced concrete", "structural steel",
                   "steel concrete composite", "timber", "masonry")
# [REF NBC105-2025 §1.2, printed p. 1] Base-isolated buildings and buildings
# equipped and treated with structural control "can be designed in reference
# with specialist literatures".
SPECIALIST_LITERATURE_SYSTEMS = ("base-isolated", "structural control")
# [REF NBC105-2025 §1.2, printed p. 1] "applicable to all buildings, low to
# high rise": no height limit is printed.
SCOPE_HEIGHT_LIMIT_M: Optional[float] = None

# Numeric thresholds printed inside definitions (section 1.3).
# [REF NBC105-2025 §1.3 DUAL SYSTEM, printed p. 3] at least 25 % of design base shear.
DUAL_SYSTEM_MIN_FRAME_SHARE = 0.25
# [REF NBC105-2025 §1.3 SOFT STORY, printed p. 5] less than 70 per cent of the story above.
SOFT_STORY_ADJACENT_RATIO = 0.70
# [REF NBC105-2025 §1.3 SOFT STORY, printed p. 5] less than 80 per cent of the mean of the three above.
SOFT_STORY_THREE_ABOVE_RATIO = 0.80
# [REF NBC105-2025 §1.3 FLEXIBLE DIAPHRAGM, printed p. 3] more than two times the average story drift.
FLEXIBLE_DIAPHRAGM_DEFORMATION_RATIO = 2.0
# [REF NBC105-2025 §1.3 DESIGN BASIS EARTHQUAKE, printed p. 3] two-thirds of the MCE.
DESIGN_BASIS_EARTHQUAKE_MCE_FRACTION = 2.0 / 3.0
# [REF NBC105-2025 §1.3 RESPONSE SPECTRUM, printed p. 5] "commonly taken as 5% of critical".
RESPONSE_SPECTRUM_COMMON_DAMPING_RATIO = 0.05

_UNIT_BASES = ("PRINTED", "SI_DERIVED", "DIMENSIONLESS", "NOT_STATED", "NOT_APPLICABLE")


@dataclass(frozen=True)
class Notation:
    """One row of the printed notation list. [REF NBC105-2025 §1.4, printed pp. 6-9]"""
    symbol: str          # ASCII key used by this module
    printed_symbol: str  # symbol as printed (Greek letters, asterisks)
    meaning: str         # meaning text as printed
    unit: Optional[str]  # None when no unit applies or none can be derived
    unit_basis: str      # PRINTED / SI_DERIVED / DIMENSIONLESS / NOT_STATED / NOT_APPLICABLE
    page: int            # printed page
    printed_value: Optional[float] = None


def _n(page, symbol, meaning, unit, basis, printed_symbol=None, printed_value=None):
    assert basis in _UNIT_BASES
    return Notation(symbol, printed_symbol or symbol, meaning, unit, basis, page, printed_value)


_D = "DIMENSIONLESS"
_S = "SI_DERIVED"
_X = "NOT_STATED"
_A = "NOT_APPLICABLE"

# Printed pp. 6-9, in printed order (19 + 22 + 21 + 6 = 68 rows).
NOTATIONS = (
    # p. 6
    _n(6, "ap", "Component Amplification Factor", None, _D, "aₚ"),
    _n(6, "Aw", "Area of Web", "m^2", _S, "Aᵥ"),
    _n(6, "b", "Maximum horizontal dimension of the building at the particular level "
       "measured perpendicular to the direction of loading", "m", _S),
    _n(6, "CQC", "Complete Quadratic Combination", None, _A),
    _n(6, "C(T)", "Elastic Site Spectra for horizontal loading", None, _D),
    _n(6, "Cd(T)", "Horizontal Design Spectrum", None, _D),
    _n(6, "Cd(T1)", "Horizontal Base Shear Coefficient", None, _D),
    _n(6, "Ch(T)", "Spectral Shape Factor", None, _D),
    _n(6, "Cs(T)", "Elastic Site Spectra for Serviceability Limit State", None, _D),
    _n(6, "Cv(T)", "Elastic Site Spectra for Vertical Loading", None, _D),
    _n(6, "Cd(Ti)", "Ordinate of the design spectrum for translational period Ti", None, _D),
    _n(6, "DL", "Design dead load", None, _X),
    _n(6, "d*", "Displacement of equivalent SDOF system", "m", _S),
    _n(6, "det*", "Target displacement of a structure with period T*", "m", _S),
    _n(6, "di", "Horizontal displacement of the center of mass at level i, ignoring "
       "the effect of Torsion", "m", _S),
    _n(6, "dy*", "Displacement at yield of idealized SDOF system", "m", _S),
    _n(6, "E", "Design earthquake load", None, _X),
    _n(6, "ESM", "Equivalent Static Method", None, _A),
    _n(6, "ec", "Computed distance between the center of mass and the center of rigidity", "m", _S),
    # p. 7
    _n(7, "ed", "Design eccentricity of the seismic force at a particular level", "m", _S),
    _n(7, "Ec", "Modulus of Elasticity of Concrete", "Pa", _S),
    _n(7, "Ex", "Design earthquake load in Principal direction X", None, _X),
    _n(7, "Ey", "Design earthquake load in Principal direction Y", None, _X),
    _n(7, "F*", "Force of equivalent SDOF system", "N", _S),
    _n(7, "Fi", "Lateral force acting at level i", "N", _S),
    _n(7, "Fp", "Design seismic force for parts and components", "N", _S),
    _n(7, "Fy*", "Yield force of idealized SDOF system", "N", _S),
    Notation("g", "g", "Acceleration due to gravity.  To be taken as 9.81 m/s2",
             "m/s^2", "PRINTED", 7, 9.81),  # literal as printed; parity with constants is tested
    _n(7, "H", "Height from the base to the top of the main portion of the building or "
       "the eaves of the building (m)", "m", "PRINTED"),
    _n(7, "hi", "Height of the level i from the base considered", "m", _S),
    _n(7, "hp", "Height of the component", "m", _S),
    _n(7, "i", "level under consideration of the structure", None, _D),
    _n(7, "I", "Importance factor for the building", None, _D),
    _n(7, "Ip", "Component Importance Factor", None, _D, "Iₚ"),
    _n(7, "Ig", "Section moment of inertia calculated using the gross cross sectional "
       "area of concrete", "m^4", _S, "Iᵍ"),
    _n(7, "LL", "Design live load", None, _X),
    _n(7, "m*", "Mass of equivalent SDOF system", "kg", _S),
    _n(7, "MRSM", "Modal Response Spectrum Method", None, _A),
    _n(7, "n", "Number of levels in a structure", None, _D),
    _n(7, "PGA", "Peak Ground Acceleration", None, _X),
    _n(7, "RC", "Reinforced Concrete", None, _A),
    # p. 8
    _n(8, "Rs", "Ductility Factor for Serviceability Limit State", None, _D, "Rₛ"),
    _n(8, "Rmu", "Ductility Factor for Ultimate Limit State", None, _D, "Rμ"),
    _n(8, "Sep", "Earth pressure", None, _X),
    _n(8, "Sgw", "Ground water", None, _X),
    _n(8, "Sice", "Ice load", None, _X),
    _n(8, "Slp", "Static liquid pressure", None, _X),
    _n(8, "Spnd", "Rain water ponding", None, _X),
    _n(8, "Sso", "Snow load", None, _X),
    _n(8, "SDOF", "Single degree of freedom", None, _A),
    _n(8, "SRSS", "Square root of sum of squares", None, _A),
    _n(8, "T*", "Time period of idealized equivalent SDOF system", "s", _S),
    _n(8, "T1", "Approximate Fundamental Period of Vibration", "s", _S, "T₁"),
    _n(8, "Tc", "Corner period corresponding to the end of constant spectral "
       "acceleration range", "s", _S),
    _n(8, "Ti", "Fundamental Translation Period of ith mode of vibration", "s", _S),
    _n(8, "T", "Period of vibration of a linear single degree of freedom system", "s", _S),
    _n(8, "V", "Horizontal seismic base shear obtained from equivalent static method", "N", _S),
    _n(8, "VR", "Combined base shear obtained from modal response spectrum method", "N", _S),
    _n(8, "W", "Seismic weight of the structure", "N", _S),
    _n(8, "Wi", "Seismic weight at level I;", "N", _S),
    _n(8, "Wp", "Component weight", "N", _S),
    _n(8, "wj", "portion of gravity load at story level j", None, _X),
    # p. 9
    _n(9, "Z", "Seismic zoning factor", None, _D),
    _n(9, "Omega_s", "Overstrength factor for serviceability limit state", None, _D, "Ωs"),
    _n(9, "Omega_u", "Overstrength factor for ultimate limit state", None, _D, "Ωu"),
    _n(9, "alpha", "Peak spectral acceleration normalized by PGA", None, _D, "α"),
    _n(9, "mu_p", "Component ductility factor", None, _D, "μp"),
    _n(9, "phi_ji", "mode shape coefficient at floor j in mode i", None, _D, "ϕji"),
)

_BY_SYMBOL = {n.symbol: n for n in NOTATIONS}


def notation(symbol):
    """Return the printed notation row for ``symbol``; KeyError if not printed.

    [REF NBC105-2025 §1.4, printed pp. 6-9]
    """
    try:
        return _BY_SYMBOL[symbol]
    except (KeyError, TypeError):
        raise KeyError("symbol %r is not in the NBC 105:2025 notation list (printed pp. 6-9)" % (symbol,))


def notation_page_counts():
    """Return {printed page: number of notation rows}. [REF NBC105-2025 §1.4, printed pp. 6-9]"""
    counts = {}
    for n in NOTATIONS:
        counts[n.page] = counts.get(n.page, 0) + 1
    return counts


def printed_gravity_m_s2():
    """Return g as printed in the notation list (9.81). [REF NBC105-2025 §1.4, printed p. 7]"""
    return _BY_SYMBOL["g"].printed_value


def pdf_page_for_printed(page):
    """Return the PDF page of clause 1 printed page 1..9 (offset 21).

    [REF NBC105-2025 §1, printed pp. 1-9; docs/nbc105/README.md page-offset method]
    """
    if isinstance(page, bool) or not isinstance(page, int) or not 1 <= page <= 9:
        raise ValueError("clause 1 printed page must be an integer 1..9, got %r" % (page,))
    return page + PRINTED_PAGE_OFFSET


# ---------------------------------------------------------------- validators
def _pos(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s must be a real number, got %r" % (name, value))
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError("%s must be finite and > 0, got %r" % (name, value))
    return value


def _nonneg(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s must be a real number, got %r" % (name, value))
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError("%s must be finite and >= 0, got %r" % (name, value))
    return value


def _flag(value, name):
    if not isinstance(value, bool):
        raise ValueError("%s must be a bool, got %r" % (name, value))
    return value


# --------------------------------------------------------------------- scope
_MATERIAL_ALIASES = {
    "reinforced concrete": "reinforced concrete", "rc": "reinforced concrete",
    "structural steel": "structural steel", "steel": "structural steel",
    "steel concrete composite": "steel concrete composite",
    "composite": "steel concrete composite",
    "timber": "timber", "masonry": "masonry",
}


def scope_check(material, *, base_isolated=False, structural_control=False, height_m=None):
    """Classify a building against the printed scope (clause 1.2).

    [REF NBC105-2025 §1.2, printed p. 1] Returns ``{"status", "material",
    "height_limit_m", "basis"}``. Status ``IN_SCOPE`` for a listed material;
    ``SPECIALIST_LITERATURE`` when base isolation or structural control is
    used (the code says these "can be designed in reference with specialist
    literatures"); ``MATERIAL_NOT_LISTED`` otherwise (not an exclusion
    statement, the clause only lists the covered materials). No height limit is
    printed, so ``height_m`` is only validated. Not design acceptance.
    """
    if not isinstance(material, str) or not material.strip():
        raise ValueError("material must be a non-empty string")
    _flag(base_isolated, "base_isolated")
    _flag(structural_control, "structural_control")
    if height_m is not None:
        _pos(height_m, "height_m")
    key = " ".join(material.casefold().replace("-", " ").replace("_", " ").split())
    canonical = _MATERIAL_ALIASES.get(key)
    if base_isolated or structural_control:
        status, basis = ("SPECIALIST_LITERATURE",
                         "p. 1: base-isolated / structural-control buildings are designed in reference with specialist literatures")
    elif canonical is None:
        status, basis = ("MATERIAL_NOT_LISTED",
                         "p. 1 lists reinforced concrete, structural steel, steel concrete composite, timber and masonry")
    else:
        status, basis = "IN_SCOPE", "p. 1: all buildings, low to high rise; listed material"
    return {"status": status, "material": canonical or key,
            "height_limit_m": SCOPE_HEIGHT_LIMIT_M, "basis": basis}


# --------------------------------------------------- definition thresholds
def is_soft_story(stiffness, stiffness_above, three_above: Optional[Sequence[float]] = None):
    """True if a story is soft per the printed definition.

    [REF NBC105-2025 §1.3 SOFT STORY, printed p. 5] Lateral stiffness less than
    70 per cent of the story above, or (when the three stories above are
    given) less than 80 per cent of their average. Both tests are strict.
    """
    k = _pos(stiffness, "stiffness")
    ku = _pos(stiffness_above, "stiffness_above")
    if k < SOFT_STORY_ADJACENT_RATIO * ku:
        soft = True
    else:
        soft = False
    if three_above is not None:
        try:
            vals = list(three_above)
        except TypeError:
            raise ValueError("three_above must be a sequence of three stiffnesses")
        if len(vals) != 3:
            raise ValueError("three_above must hold exactly three stiffnesses")
        vals = [_pos(v, "three_above") for v in vals]
        if k < SOFT_STORY_THREE_ABOVE_RATIO * (sum(vals) / 3):
            soft = True
    return soft


def is_flexible_diaphragm(max_diaphragm_deformation, average_story_drift):
    """True if the diaphragm deformation exceeds twice the average story drift.

    [REF NBC105-2025 §1.3 FLEXIBLE DIAPHRAGM, printed p. 3] "more than two times".
    """
    d = _pos(max_diaphragm_deformation, "max_diaphragm_deformation")
    s = _pos(average_story_drift, "average_story_drift")
    return d > FLEXIBLE_DIAPHRAGM_DEFORMATION_RATIO * s


def dual_system_frame_share(frame_base_shear, design_base_shear):
    """Return frame base shear / design base shear.

    [REF NBC105-2025 §1.3 DUAL SYSTEM, printed p. 3]
    """
    f = _nonneg(frame_base_shear, "frame_base_shear")
    v = _pos(design_base_shear, "design_base_shear")
    return f / v


def dual_system_frame_share_ok(frame_base_shear, design_base_shear):
    """True if the moment frames resist at least 25 % of the design base shear.

    [REF NBC105-2025 §1.3 DUAL SYSTEM, printed p. 3] "at least 25%".
    """
    return dual_system_frame_share(frame_base_shear, design_base_shear) >= DUAL_SYSTEM_MIN_FRAME_SHARE


def design_basis_earthquake_from_mce(mce):
    """Return two-thirds of the Maximum Considered Earthquake quantity.

    [REF NBC105-2025 §1.3 DESIGN BASIS EARTHQUAKE, printed p. 3]
    """
    return DESIGN_BASIS_EARTHQUAKE_MCE_FRACTION * _pos(mce, "mce")


def ductility_factor(ultimate_displacement_demand, yield_displacement_demand):
    """Ratio of ultimate to yield displacement demand.

    [REF NBC105-2025 §1.3 DUCTILITY FACTOR, printed p. 3]
    """
    return _pos(ultimate_displacement_demand, "ultimate_displacement_demand") / \
        _pos(yield_displacement_demand, "yield_displacement_demand")


def overstrength_factor(first_significant_yield_strength, design_base_shear):
    """Ratio of the first significant yield strength to the design base shear.

    [REF NBC105-2025 §1.3 OVERSTRENGTH FACTOR, printed p. 5]
    """
    return _pos(first_significant_yield_strength, "first_significant_yield_strength") / \
        _pos(design_base_shear, "design_base_shear")


def eccentricity_m(center_of_mass_xy, center_of_stiffness_xy):
    """Distance between the center of mass and the center of stiffness (m).

    [REF NBC105-2025 §1.3 ECCENTRICITY, printed p. 3]
    """
    pts = []
    for name, p in (("center_of_mass_xy", center_of_mass_xy),
                    ("center_of_stiffness_xy", center_of_stiffness_xy)):
        try:
            x, y = p
        except (TypeError, ValueError):
            raise ValueError("%s must be an (x, y) pair" % name)
        for v in (x, y):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError("%s must hold finite numbers" % name)
        pts.append((float(x), float(y)))
    return math.hypot(pts[0][0] - pts[1][0], pts[0][1] - pts[1][1])
