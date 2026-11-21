"""NBC 105:2025 §10, printed pp.49–52, Tables 10-1, 10-2, 10-3.

Assumes the source's component design force equation 10.3(1):
Fp = Z(1+hp/H)(ap/mu_p)Ip*Wp. This is a reference implementation;
detailing, connection capacity and source acceleration checks are external.
"""
from __future__ import annotations
import math
__all__=["component_amplification_factor","component_design_force",
         "component_ductility_factor","component_importance_factor",
         "component_scope","friction_design_resistance",
         "shutdown_threshold_g"]
_TABLE_DUCTILITY={"low":1.5,"moderate":2.5}
_TABLE_IMPORTANCE={"hazardous":1.5,"life safety":1.5,
  "public storage":1.5,"emergency":1.5,"other":1.0}

def _nonnegative(v,name):
    if isinstance(v,bool):raise ValueError(name+" invalid")
    try:x=float(v)
    except (ValueError,TypeError) as exc:raise ValueError(name+" invalid") from exc
    if not math.isfinite(x) or x<0:raise ValueError(name+" must be nonnegative finite")
    return x

def _positive(v,name):
    x=_nonnegative(v,name)
    if x<=0:raise ValueError(name+" must be positive")
    return x

def component_amplification_factor(building_period_s,component_period_s):
    """§10.3.1 Table 10-1 p.50: 2.5 at ΔT=0; 1 at ΔT>=0.5s."""
    t1=_positive(building_period_s,"T1")
    tp=_positive(component_period_s,"Tp")
    delta=abs(t1-tp)
    return 1.0 if delta>=.5 else 2.5-3.0*delta

def component_ductility_factor(deformability):
    """§10.3.2 Table 10-2 p.50; research-supported higher <=3.5 is not auto-approved."""
    k=str(deformability).strip().lower()
    if k not in _TABLE_DUCTILITY:raise ValueError("unknown Table 10-2 category")
    return _TABLE_DUCTILITY[k]

def component_importance_factor(component_class):
    """§10.3.3 Table 10-3 p.51."""
    k=str(component_class).strip().lower().replace("_"," ")
    if k not in _TABLE_IMPORTANCE:raise ValueError("unknown Table 10-3 category")
    return _TABLE_IMPORTANCE[k]

def component_scope(building_seismic_weight,component_weight):
    """§10.1 p.49: §10 inapplicable if component weight MORE THAN 25% of building.
    Equality is allowed by the literal text, though independent structural
    modelling of a massive component remains necessary.
    """
    w=_positive(building_seismic_weight,"building weight")
    p=_nonnegative(component_weight,"component weight")
    return {"allowed":p<=.25*w,"component_to_building_ratio":p/w,
            "basis":"SECTION_10_SCOPE_NOT_CONNECTION_DESIGN"}

def component_design_force(*,z,hp,H,ap,mu_p,Ip,Wp):
    """§10.3 Eq.10.3(1) p.49: Z (1+hp/H) (ap/mu_p) Ip Wp."""
    h=_positive(H,"H"); attach=_nonnegative(hp,"hp")
    if attach>h:raise ValueError("component attachment above top of building")
    return (_positive(z,"Z")*(1.+attach/h)*_positive(ap,"ap")/
      _positive(mu_p,"mu_p")*_positive(Ip,"Ip")*_positive(Wp,"Wp"))

def friction_design_resistance(vertical_normal_force,coefficient_of_friction):
    """§10.1 p.49: half of gravity-friction resistance for seismic design."""
    return .5*_nonnegative(vertical_normal_force,"N")*_nonnegative(coefficient_of_friction,"mu")

def shutdown_threshold_g(value):
    """§10.2 p.49: automatic service shut-off trigger cannot exceed 0.2g."""
    a=_nonnegative(value,"shutoff trigger")
    if a>.2:raise ValueError("automatic shut-off must trigger at no more than 0.2g")
    return a
