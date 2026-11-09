"""Physical self-weight single-count audit, independent of support topology.

Native ETABS self-weight multipliers specify load-pattern allocation of
gamma*volume. OpenSees has no implicit self-weight for these elements:
assembled explicit nodal loads are the only gravity weight source.

[REF docs/source/components/model/single_count_self_weight.py.md]
"""
from __future__ import annotations
import math


def audit_self_weight_patterns(records, gravity_factors, mass_factors, *,
                               beam_weight_policy, joint_volume_policy):
    """Reject accidental double inclusion of the same geometric self-weight.

    One physical member's full weight can be allocated to multiple patterns
    only if their combined factors for the analysed profile do not exceed 1.
    For the production configured gravity profile, we check its actual
    source pattern multipliers. The full 1D+1L runtime profile is checked
    independently using a physical sum of ETABS multipliers.
    """
    if not isinstance(records,list) or not records:
        raise ValueError("No native ETABS self-weight load-pattern multipliers")
    if not isinstance(gravity_factors,dict) or not isinstance(mass_factors,dict):
        raise ValueError("Missing gravity/mass pattern factors")
    seen=set();rows=[];physical=0.;configured=0.;mass=0.
    for i,rec in enumerate(records,1):
        pattern=str(rec.get("pattern","")).strip()
        if not pattern or pattern in seen:
            raise ValueError("Duplicate or empty ETABS self-weight pattern "+pattern)
        seen.add(pattern)
        if pattern not in gravity_factors or pattern not in mass_factors:
            raise ValueError("Missing pattern factors for self-weight "+pattern)
        try:
            m=float(rec["multiplier"])
            gf=float(gravity_factors[pattern])
            mf=float(mass_factors[pattern])
        except (TypeError,ValueError,KeyError) as exc:
            raise ValueError("Invalid ETABS self-weight pattern record "+pattern) from exc
        if not all(math.isfinite(x) for x in (m,gf,mf)):
            raise ValueError("Nonfinite self-weight allocation in "+pattern)
        if m<0 or gf<0 or mf<0:
            raise ValueError("Negative self-weight or pattern factor requires separate reviewed treatment: "+pattern)
        physical+=m
        configured+=m*gf
        mass+=m*mf
        rows.append(dict(pattern=pattern,etabs_self_weight_multiplier=m,
                         configured_gravity_factor=gf,seismic_mass_factor=mf,
                         configured_weight_coefficient=m*gf,
                         mass_weight_coefficient=m*mf))
    eps=1e-8
    if physical>1+eps:
        raise ValueError(
            "DOUBLE COUNT RISK: ETABS source self-weight multipliers sum to "
            f"{physical:.8f} (>1), so the same model geometry is counted "
            "more than once in full 1D+1L. Correct original ETABS load patterns "
            "and re-export; never subtract support reactions to conceal it.")
    if configured>1+eps:
        raise ValueError("DOUBLE COUNT RISK: configured self-weight coefficient "
                         f"{configured:.8f} (>1) for the same physical geometry.")
    if mass>1+eps:
        raise ValueError("DOUBLE COUNT RISK: mass from self-weight coefficient "
                         f"{mass:.8f} (>1) for the same physical geometry.")
    if (beam_weight_policy=="ETABS_BEAM_CLEAR_LENGTH"
            and joint_volume_policy=="VERIFIED_SINGLE_OWNER"):
        raise ValueError("DOUBLE SUBTRACTION: beam clear length plus joint volume")
    return dict(schema="gravity-single-count-v1",
                status="SELF_WEIGHT_PATTERN_ACCOUNTING_PASS_NOT_JOINT_SOLID_VALIDATED",
                etabs_pattern_rows=rows,
                full_DL_LL_physical_self_weight_coefficient=physical,
                configured_gravity_self_weight_coefficient=configured,
                seismic_mass_self_weight_coefficient=mass,
                physical_weight_rule="gamma_kN_m3 * physical_member_volume_m3; load pattern multiplier allocates this single weight, not a second weight",
                beam_weight_policy=beam_weight_policy,
                joint_volume_policy=joint_volume_policy,
                geometric_joint_solid_ownership="NOT_ESTABLISHED_BY_THIS_AUDIT",
                independent_etabs_material_list="REQUIRED_FOR_FULL_WEIGHT_VALIDATION",
                warning=("Pattern allocation tests prevent adding the same full "
                         "member weight in two load patterns. They do not by "
                         "themselves detect intersections of beam, column, "
                         "slab and wall solids. Rigid offsets are stiffness "
                         "kinematics, not proof of a geometric mass deduction."))
