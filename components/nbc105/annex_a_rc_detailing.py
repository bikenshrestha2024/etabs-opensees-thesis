"""NBC 105:2025 Annex A — strictly scoped RC shear-wall detailing helpers.

[REF NBC105-2025 Annex A §§5.1,5.3,5.5, printed pp.76–79]
These calculate only explicit, independently checkable geometric and material
minima for the user's wall interpretation. They do not design the full wall,
boundary zone, coupling beam, opening reinforcement, or verify demand/capacity.
"""
from __future__ import annotations
import math

__all__=[
    "rc_wall_detailing_minima","rc_wall_boundary_element_requirement",
    "coupling_beam_diagonal_required",
]

def _positive(value,name):
    if isinstance(value,bool):
        raise ValueError(f"{name} must be finite positive")
    try: f=float(value)
    except (ValueError,TypeError,OverflowError) as exc:
        raise ValueError(f"{name} must be finite positive") from exc
    if not math.isfinite(f) or f<=0:
        raise ValueError(f"{name} must be finite positive")
    return f

def _nonnegative(value,name):
    if isinstance(value,bool):
        raise ValueError(f"{name} must be finite nonnegative")
    try: f=float(value)
    except (ValueError,TypeError,OverflowError) as exc:
        raise ValueError(f"{name} must be finite nonnegative") from exc
    if not math.isfinite(f) or f<0:
        raise ValueError(f"{name} must be finite nonnegative")
    return f

def rc_wall_detailing_minima(*,thickness_mm,wall_length_mm,coupled,
                             fck_mpa,shear_stress_mpa,horizontal_ratio,
                             vertical_ratio,bar_diameter_mm,bar_spacing_mm,
                             reinforcement_curtains):
    """Annex A §5.1 pp.76–77: minimum special RC shear wall checks.

    [REF NBC105-2025 Annex A §5.1, printed p.76]
    A fully coupled wall needs >=300 mm; otherwise special wall >=150 mm.
    l_w/t_w>=4; reinforcement ratio >=0.0025 each direction.
    Two curtains if t>=200 mm or tau_v>0.25sqrt(fck).
    Longitudinal bar diameter <=t/10; maximum spacing
    min(l_w/5,3t_w,450 mm).
    """
    t=_positive(thickness_mm,"thickness_mm")
    length=_positive(wall_length_mm,"wall_length_mm")
    if type(coupled) is not bool:raise ValueError("coupled must be bool")
    strength=_positive(fck_mpa,"fck_mpa")
    tau=_nonnegative(shear_stress_mpa,"shear_stress_mpa")
    rh=_nonnegative(horizontal_ratio,"horizontal_ratio")
    rv=_nonnegative(vertical_ratio,"vertical_ratio")
    db=_positive(bar_diameter_mm,"bar_diameter_mm")
    spacing=_positive(bar_spacing_mm,"bar_spacing_mm")
    if (isinstance(reinforcement_curtains,bool)
        or not isinstance(reinforcement_curtains,int)
        or reinforcement_curtains<1):
        raise ValueError("reinforcement_curtains must be a positive integer")
    minimum=300 if coupled else 150
    max_dia=t/10.
    max_spacing=min(length/5.,3.*t,450.)
    curtains_required=t>=200. or tau>0.25*math.sqrt(strength)
    violations=[]
    if t<minimum:violations.append("THICKNESS_LT_COUPLED_MINIMUM" if coupled
                                  else "THICKNESS_LT_SPECIAL_MINIMUM")
    if length/t<4.:violations.append("WALL_LENGTH_TO_THICKNESS_LT_4")
    if rh<.0025:violations.append("HORIZONTAL_REBAR_RATIO_LT_0_0025")
    if rv<.0025:violations.append("VERTICAL_REBAR_RATIO_LT_0_0025")
    if db>max_dia:violations.append("LONGITUDINAL_BAR_DIAMETER_TOO_LARGE")
    if spacing>max_spacing:violations.append("BAR_SPACING_TOO_LARGE")
    if curtains_required and reinforcement_curtains<2:
        violations.append("TWO_REINFORCEMENT_CURTAINS_REQUIRED")
    return {
        "geometry_and_rebar_minima_pass":not violations,
        "violations":violations,
        "min_thickness_mm":minimum,
        "min_wall_length_over_thickness":4.,
        "min_horizontal_ratio":.0025,
        "min_vertical_ratio":.0025,
        "max_bar_diameter_mm":max_dia,
        "max_bar_spacing_mm":max_spacing,
        "two_curtains_required":curtains_required,
        "scope":"ONLY_ANNEX_A_5_1_MINIMA_NOT_SHEAR_FLEXURE_OR_COUPLING_APPROVAL",
    }

def rc_wall_boundary_element_requirement(*,fck_mpa,extreme_compression_mpa,
                                          wall_length_mm,longitudinal_ratio):
    """Annex A §5.3 p.78: >0.2fck triggers boundaries, length 0.2lw each end.

    [REF NBC105-2025 Annex A §5.3, printed p.78]
    Boundary reinforcement range 0.8% to 6% (practical upper 4% noted).
    Design stress MUST be from a gross-section linear elastic calculation.
    """
    fck=_positive(fck_mpa,"fck_mpa")
    stress=_nonnegative(extreme_compression_mpa,"extreme_compression_mpa")
    length=_positive(wall_length_mm,"wall_length_mm")
    ratio=_nonnegative(longitudinal_ratio,"longitudinal_ratio")
    required=stress>.2*fck
    return {
        "boundary_required":required,
        "boundary_length_each_end_mm":.2*length,
        "ratio_pass":.008<=ratio<=.06,
        "practical_ratio_upper":.04,
        "stress_trigger_mpa":.2*fck,
        "discontinuation_stress_below_mpa":.15*fck,
        "scope":"GROSS_SECTION_LINEAR_COMPRESSION_REQUIRED_NOT_FULL_BOUNDARY_CAPACITY",
    }

def coupling_beam_diagonal_required(*,shear_stress_mpa,fck_mpa,
                                    clear_span_mm,depth_mm):
    """Annex A §5.5.2(a) p.78: tau_ve >0.1 sqrt(fck)*Ls/D.

    [REF NBC105-2025 Annex A §5.5.2(a), printed p.78]
    If true, diagonal reinforcement alone must resist induced actions;
    this function makes no claim of reinforcement or anchorage sufficiency.
    """
    stress=_nonnegative(shear_stress_mpa,"shear_stress_mpa")
    strength=_positive(fck_mpa,"fck_mpa")
    span=_positive(clear_span_mm,"clear_span_mm")
    depth=_positive(depth_mm,"depth_mm")
    return stress>.1*math.sqrt(strength)*span/depth
