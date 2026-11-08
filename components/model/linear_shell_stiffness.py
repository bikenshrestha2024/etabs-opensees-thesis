"""Audited linear ShellMITC4 / ElasticMembranePlateSection stiffness proxy.

For ETABS uniform in-plane f and uniform plate bending m, the OpenSees
ElasticMembranePlateSection supports E_mem=f*E, E_plate=m*E and physical
thickness h. OpenSees C++ ALSO makes transverse shear proportional to
E_plate, so ETABS v13=v23=1 cannot be exactly reproduced if m != 1.

This adapter is intentionally a documented THIN-SHELL APPROXIMATION,
not an exact stiffness equivalence or calibrated structural model.

[REF docs/source/components/model/linear_shell_stiffness.py.md]
"""
from __future__ import annotations
import math

FIELDS=("f11","f22","f12","m11","m22","m12","v13","v23","mass","weight")
TOL=1e-9


def positive(value,what):
    """Validate physical/section positive inputs.

    [REF docs/source/components/model/linear_shell_stiffness.py.md]
    """
    try:
        x=float(value)
    except (ValueError,TypeError):
        raise ValueError("Missing/non-numeric "+what) from None
    if not math.isfinite(x) or x<=0:
        raise ValueError("Nonpositive/nonfinite "+what)
    return x


def source_shell_modifiers(values, *, property_name, source_kind):
    """Require the entire effective ETABS modifier vector, not guesses.

    [REF docs/source/components/model/linear_shell_stiffness.py.md]
    """
    if not isinstance(values,dict):
        raise ValueError(property_name+": missing audited "+source_kind+" shell modifiers")
    extras=set(values)-set(FIELDS)
    missing=set(FIELDS)-set(values)
    if missing or extras:
        raise ValueError(property_name+": missing="+str(sorted(missing))+
                         " unrecognized="+str(sorted(extras)))
    return {k:positive(values[k],property_name+" "+k) for k in FIELDS}


def shell_section_parameters(E,nu,thickness,source_modifiers, *,
                             property_name,source_kind="TABULATED_BY_PROPERTY",
                             transverse_shear_policy="REJECT_DIFFERENCE",
                             density=0.):
    """Return physical-thickness shell section, or fail if not representable.

    Requirements:
      f11=f22=f12; m11=m22=m12. For anisotropic or coupled ETABS
      modifiers do NOT silently approximate with a scalar.
      v13=v23=m is what OpenSees source actually produces for this
      section (not v=1 unless m=1); any mismatch is explicitly reported.
      mass and weight are accounted independently from source load/mass
      ledgers; no disguised thickness/mass modification.

    [REF OpenSees ElasticMembranePlateSection.cpp getSectionTangent]
    """
    E=positive(E,property_name+" gross Young modulus")
    thickness=positive(thickness,property_name+" physical shell thickness")
    nu=float(nu)
    if not math.isfinite(nu) or not (-.99<nu<.49):
        raise ValueError(property_name+": invalid Poisson ratio")
    vals=source_shell_modifiers(source_modifiers,property_name=property_name,
                                source_kind=source_kind)
    for label,keys in (("membrane",("f11","f22","f12")),
                       ("bending",("m11","m22","m12"))):
        seq=[vals[k] for k in keys]
        if max(seq)-min(seq)>TOL*max(1.,max(seq)):
            raise ValueError(property_name+": nonuniform "+label+
                " modifiers need a verified anisotropic section, not isotropic shell proxy")
    if abs(vals["mass"]-1)>TOL or abs(vals["weight"]-1)>TOL:
        raise ValueError(property_name+": ETABS mass/weight modifiers !=1 must be "
                         "reconciled separately against the mass and gravity source")
    f=vals["f11"]
    m=vals["m11"]
    effective_v13=effective_v23=m
    mismatch=max(abs(vals["v13"]-effective_v13),abs(vals["v23"]-effective_v23))
    if mismatch>TOL and transverse_shear_policy!="ALLOW_REVIEWED_THIN_SHELL_APPROX":
        raise ValueError(property_name+": ShellMITC4/ElasticMembranePlateSection cannot "
              "independently reproduce transverse shear v13/v23="+
              str((vals["v13"],vals["v23"]))+
              "; it forces the plate-bending factor "+str(m)+
              ". Review and explicitly authorize a thin-shell sensitivity approximation.")
    if transverse_shear_policy not in (
        "REJECT_DIFFERENCE","ALLOW_REVIEWED_THIN_SHELL_APPROX"):
        raise ValueError("Unknown transverse shear policy "+str(transverse_shear_policy))
    mem_E=E*f
    ep_modifier=m/f
    return {
        "section_type":"ElasticMembranePlateSection",
        "element_type":"ShellMITC4",
        "E_membrane_kN_m2":mem_E,
        "ep_modifier":ep_modifier,
        "E_plate_kN_m2":E*m,
        "physical_thickness_m":thickness,
        "section_density":float(density),
        "poisson_ratio":nu,
        "actual_inplane_modifier":f,
        "actual_plate_modifier":m,
        "actual_transverse_shear_modifier":m,
        "target_transverse_shear_modifiers":[vals["v13"],vals["v23"]],
        "transverse_shear_exact":mismatch<=TOL,
        "status":("EXACT_UNIFORM_ELASTIC_SECTION" if mismatch<=TOL else
                  "EXPLICIT_THIN_SHELL_APPROX_NOT_FULL_ETABS_EQUIVALENCE"),
        "source_kind":source_kind,
        "property_name":property_name,
        "warning":("OpenSees section couples plate bending and transverse shear; "
                   "screened thin shell approximation requires numerical patch and "
                   "mesh-convergence tests. No physical thickness/mass is reduced.")
    }


def section_command(ops,tag,result):
    """Register explicitly parameterized elastic section; no hidden reductions.

    [REF docs/source/components/model/linear_shell_stiffness.py.md]
    """
    ops.section("ElasticMembranePlateSection",int(tag),
                result["E_membrane_kN_m2"],
                # E_plate is defined by the optional Ep_modifier.
                # OpenSees source: Ep = Em * Ep_modifier
                result.get("poisson_ratio",0.2),
                result["physical_thickness_m"],
                result["section_density"],
                result["ep_modifier"])
