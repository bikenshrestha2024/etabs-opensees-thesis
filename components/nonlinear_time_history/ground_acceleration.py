"""OpenSees UniformExcitation support-acceleration reconstruction.

OpenSees documentation:
https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html

For a uniform-support acceleration, nodeDisp/nodeVel/nodeAccel responses
are RELATIVE to supports. Absolute translational floor acceleration in the
input horizontal DOFs equals recorded relative floor acceleration PLUS
the corresponding applied support acceleration, in compatible units.

The Path series uses linear interpolation between uniformly sampled values.
This helper matches the source Path series default (zero outside record),
including additional spectral factor =1 for already matched sources.
Nonuniform/multi-support excitation needs a DIFFERENT algorithm.
"""
from __future__ import annotations
import math

CONVERSION={"g":9.80665,"m/s2":1.0}

def _sample_path(values,dt,time_s):
    """Uniformly sampled Path at analysis time, zero outside record duration."""
    n=len(values)
    d=float(dt)
    t=float(time_s)
    if n<2 or not math.isfinite(d) or d<=0 or not math.isfinite(t):
        raise ValueError("Invalid Path history, dt, or analysis time")
    if t<0 or t>(n-1)*d+1e-10:
        return 0.
    sample=min(max(t/d,0.),float(n-1))
    i=int(math.floor(sample))
    # Check only sampled ordinates (O(1) per integration step), so a
    # malformed accelerogram cannot silently introduce NaN/Inf support motion.
    left = float(values[i])
    if not math.isfinite(left):
        raise ValueError("Nonfinite ground-motion Path ordinate")
    if i>=n-1:
        return left
    right = float(values[i+1])
    if not math.isfinite(right):
        raise ValueError("Nonfinite ground-motion Path ordinate")
    frac=sample-i
    return left*(1.-frac)+right*frac


def applied_ground_acceleration(records, *, time_s, orientation, excitation="XY",
                                additional_spectral_scale=1.0):
    """Return (agX,agY) m/s² for EXACT configured XY/YX and X/Y/ZERO probe."""
    if orientation not in ("XY","YX"):
        raise ValueError("Orientation must be XY or YX")
    if excitation not in ("XY","X","Y","ZERO"):
        raise ValueError("diagnostic_excitation must be XY, X, Y or ZERO")
    if len(records)!=2:
        raise ValueError("Exactly two orthogonal records required")
    scale=float(additional_spectral_scale)
    if not math.isfinite(scale) or scale<=0:
        raise ValueError("Additional scale must be positive finite")
    ordered=records if orientation=="XY" else records[::-1]
    result=[]
    for direction,(values,dt,unit) in enumerate(ordered):
        if unit not in CONVERSION:
            raise ValueError("Unsupported acceleration unit: "+str(unit))
        enabled=excitation=="XY" or excitation=="X" and direction==0 or excitation=="Y" and direction==1
        result.append(_sample_path(values,dt,time_s)*CONVERSION[unit]*scale if enabled else 0.)
    return tuple(result)


def relative_to_absolute_floor_acceleration(node_relative_xyz,ground_xy):
    """Only horizontal absolute translation; vertical remains unchanged/unsupported."""
    if len(node_relative_xyz)<2 or len(ground_xy)!=2:
        raise ValueError("Expected at least 2 nodal accelerations and 2 support accelerations")
    values = (float(node_relative_xyz[0]), float(node_relative_xyz[1]),
              float(ground_xy[0]), float(ground_xy[1]))
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Nonfinite relative or support acceleration")
    return (values[0]+values[2], values[1]+values[3])
