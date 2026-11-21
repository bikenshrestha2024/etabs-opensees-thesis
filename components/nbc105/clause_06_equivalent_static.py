"""NBC 105:2025 §6, printed pp.38–39, pure ESM rules."""
from __future__ import annotations
import math
__all__=["base_shear_coefficient","base_shear","distribution_exponent",
         "distribute_forces","esm_deflection_factor"]

def _positive(v,name):
    if isinstance(v,bool):raise ValueError(name+" must be positive")
    try:x=float(v)
    except (ValueError,TypeError) as exc:raise ValueError(name+" invalid") from exc
    if not math.isfinite(x) or x<=0:raise ValueError(name+" must be positive finite")
    return x

def base_shear_coefficient(spectrum,*,overstrength,limit_state,ductility=None):
    """§6.1 p.38: Cd,ULS=C(T1)/(Rmu*Omega_u); Cd,SLS=Cs(T1)/Omega_s."""
    c=_positive(spectrum,"elastic spectrum"); o=_positive(overstrength,"overstrength")
    state=str(limit_state).upper()
    if state=="ULS":return c/(_positive(ductility,"ductility")*o)
    if state=="SLS":
        if ductility is not None:raise ValueError("SLS does not divide by ductility")
        return c/o
    raise ValueError("limit state must be ULS/SLS")

def base_shear(coefficient,seismic_weight):
    """§6.2(1) p.38: V=Cd(T1)*W."""
    return _positive(coefficient,"coefficient")*_positive(seismic_weight,"seismic_weight")

def distribution_exponent(period_s):
    """§6.3 p.39: k=1 for T<=0.5, k=2 for T>=2.5; interpolate."""
    t=_positive(period_s,"period")
    return 1. if t<=.5 else 2. if t>=2.5 else 1.+(t-.5)/2.

def distribute_forces(shear_kN,weights_kN,heights_m,exponent):
    """§6.3(1) p.39: Fi=V Wi hi^k / sum(Wj hj^k)."""
    v=_positive(shear_kN,"base shear");k=_positive(exponent,"k")
    w=list(weights_kN);h=list(heights_m)
    if not w or len(w)!=len(h):raise ValueError("weights and heights mismatched")
    terms=[_positive(wi,"Wi")*_positive(hi,"hi")**k for wi,hi in zip(w,h)]
    denom=math.fsum(terms)
    return [v*t/denom for t in terms]

def esm_deflection_factor(storeys):
    """§6.5 Table 6-1 p.39, applies only to ESM deflections."""
    if isinstance(storeys,bool) or not isinstance(storeys,int) or storeys<1:
        raise ValueError("storeys must be a positive integer")
    return {1:1.,2:.97,3:.94,4:.91,5:.88}.get(storeys,.85)
