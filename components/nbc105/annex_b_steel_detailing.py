"""NBC 105:2025 Annex B — seismic-link rotation only for qualified EBF I-links.

[REF NBC105-2025 Annex B §§7.1.1–7.1.4 printed pp.95–97]
Do not apply these capacities to SHS outriggers, BRB, FVD, generic link
objects, RC coupling beams or unverified non-seismic steel connections.
Link classification and I-section qualification require source model checks.
"""
from __future__ import annotations
import math

__all__=["seismic_link_rotation_limit_rad"]

def _positive(v,name):
    if isinstance(v,bool):raise ValueError(f"{name} must be positive finite")
    try:x=float(v)
    except (ValueError,TypeError,OverflowError) as exc:
        raise ValueError(f"{name} must be positive finite") from exc
    if not math.isfinite(x) or x<=0:raise ValueError(f"{name} must be positive finite")
    return x

def seismic_link_rotation_limit_rad(*,link_length_m,mp_kNm,vp_kN,
                                    orientation,section_type,alpha=None):
    """Annex B §7.1.2–7.1.4 pp.96–97: link rotation limit by classification.

    [REF NBC105-2025 Annex B §§7.1.2–7.1.4, printed pp.96–97]
    Horizontal: short e <=1.6Mp/Vp, long e>=3Mp/Vp.
    Vertical: short e<=0.8(1+alpha)Mp/Vp, long e>=1.5(1+alpha)Mp/Vp.
    Short theta<=0.08 rad, long theta<=0.02 rad; intermediate interpolated.
    alpha (small/large end moment ratio) is needed for vertical links.
    section_type must explicitly certify that a real I-section seismic link
    is being evaluated; no SHS/FVD/BRB default is allowed. This is an
    acceptance limit ONLY, not a design/check of actual rotation.
    """
    # Annex B §7.1.1 explicitly limits seismic links to I sections.
    # A square hollow section outrigger or FVD must never be passed off as one.
    if str(section_type).strip().upper() not in ("I","I-SECTION"):
        raise ValueError("Annex B §7.1.1 permits seismic links of I section only")
    length=_positive(link_length_m,"link_length_m")
    m=_positive(mp_kNm,"mp_kNm")
    v=_positive(vp_kN,"vp_kN")
    orient=str(orientation).strip().lower()
    if orient=="horizontal":
        low=1.6*m/v;high=3.0*m/v
    elif orient=="vertical":
        if alpha is None:raise ValueError("alpha required for vertical link")
        a=float(alpha)
        if not math.isfinite(a) or not 0<=a<=1:
            raise ValueError("alpha must be a finite ratio between 0 and 1")
        low=.8*(1+a)*m/v;high=1.5*(1+a)*m/v
    else:
        raise ValueError("NBC Annex B seismic link must be horizontal/vertical EBF I-link, not a damper")
    if length<=low:return .08
    if length>=high:return .02
    return .08-(length-low)/(high-low)*(.08-.02)
