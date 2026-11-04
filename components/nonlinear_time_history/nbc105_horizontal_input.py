"""NBC105:2025 horizontal XY/YX and vertical-action applicability audit.

Official NBC 105:2025 clauses 4.3, 9.3.1.1, 9.3.2.2–9.3.2.4.
https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
OpenSees UniformExcitation: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html

The absence of cantilever projection ALONE does not waive NBC §4.3:
20m spans, prestressed horizontal components, transfer beams supporting
columns and base isolation must be independently checked.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

HORIZONTAL_AXES={"X":1,"Y":2}
UNITS_TO_M_S2={"g":9.80665,"m/s2":1.0}
TRIGGERS=(
    ("unsupported_horizontal_span_ge_20m","Horizontal or nearly horizontal structural member spans >=20 m"),
    ("horizontal_cantilever_gt_5m","Horizontal cantilever longer than 5 m"),
    ("prestressed_horizontal_component","Prestressed horizontal member"),
    ("beam_supporting_column","Beam supporting a column"),
    ("base_isolation","Base-isolated structural system"),
)

def vertical_acceleration_review(features):
    """Only confidently verified *negative* answers can exclude §4.3 triggers."""
    if not isinstance(features,dict):
        raise ValueError("NBC 4.3 structural features must be an object")
    found=[];unknown=[]
    for key,note in TRIGGERS:
        value=features.get(key)
        if value is True:found.append({"key":key,"condition":note})
        elif value is not False:unknown.append({"key":key,"condition":note})
    if found:status="VERTICAL_ACTION_CONSIDERATION_TRIGGERED"
    elif unknown:status="INCOMPLETE_REVIEW_NO_VERTICAL_EXCLUSION"
    else:status="NO_CLAUSE_4_3_TRIGGER_DECLARED_REVIEW_REQUIRED"
    return dict(status=status,clause="NBC 105:2025 §4.3",
                triggers=found,unknown=unknown,
                horizontal_nltha_xy_yx_allowed=True,
                vertical_record_automatically_required=False,
                engineering_scope="Vertical design action applicability; not proof a Z record is necessary or unnecessary",
                source="Official NBC 105:2025 page 27")

def component_direction_mapping(orientation):
    """Both accelerograms act simultaneously; no Z input in XY/YX."""
    if orientation=="XY":return (("A",1),("B",2))
    if orientation=="YX":return (("B",1),("A",2))
    raise ValueError("Only horizontal simultaneous XY and YX are supported")

def unit_and_scale(source_units,pair_scale,*,already_scaled=False):
    """OpenSees Path '-factor' for kN-m-s model, once and once only.

    Pair scale is dimensionless; g conversion is m/s² per 1 g.
    Reject records previously spectrum-scaled to avoid double multiplication.
    """
    units=str(source_units).strip()
    if units not in UNITS_TO_M_S2:
        raise ValueError("Use source acceleration units g or m/s2")
    try:scale=float(pair_scale)
    except (ValueError,TypeError,OverflowError) as exc:
        raise ValueError("Invalid pair scale") from exc
    if not math.isfinite(scale) or scale<=0:
        raise ValueError("Pair scale must be finite positive")
    if already_scaled:
        raise ValueError("Already scaled input: cannot apply pair scale a second time")
    return UNITS_TO_M_S2[units]*scale

def applied_motion_manifest(*,orientation,record_a,record_b,dt_s,units_a,
                            units_b,pair_scale,already_scaled=False):
    """Create auditable exact OpenSees uniform-support command arguments.

    In a 3D -ndm 3 model, dof 1=X, dof 2=Y, dof 3=Z (unused).
    Input records ordered by original A/B, never by swapped global axis.
    """
    if not math.isfinite(float(dt_s)) or float(dt_s)<=0:
        raise ValueError("Record dt must be positive")
    profiles={
       "A":{"source_path":str(record_a),"source_units":units_a},
       "B":{"source_path":str(record_b),"source_units":units_b}}
    commands=[]
    for axis,(component,dof) in zip(("X","Y"),component_direction_mapping(orientation)):
        profile=profiles[component]
        commands.append(dict(global_axis=axis,dof=dof,source_component=component,
           source_path=profile["source_path"],source_units=profile["source_units"],
           path_factor_m_s2=unit_and_scale(profile["source_units"],pair_scale,
                                          already_scaled=already_scaled),
           path_series_tag=900000+dof,uniform_excitation_pattern_tag=900000+dof,
           path_dt_s=float(dt_s),
           opensees_time_series_command="ops.timeSeries('Path', tsTag, '-dt', dt, '-values', *values, '-factor', unit_factor * pair_scale)",
           opensees_pattern_command="ops.pattern('UniformExcitation', patternTag, dof, '-accel', tsTag)"))
    return dict(status="COMMAND_MAPPING_ONLY_NOT_NBC_DESIGN_APPROVAL",
       clause="NBC105:2025 §§9.3.2.2(d),9.3.2.3(a–c)",
       model_ndm=3,directions=[1,2],vertical_dof_3_used=False,
       simultaneous_two_horizontal_inputs=True,orientation=orientation,
       common_pair_scale_dimensionless=float(pair_scale),commands=commands,
       response_reference="OpenSees UniformExcitation nodal displacement is relative to support",
       caveat="Inspect original record unit provenance and source hashes; do not apply pattern -fact additionally.")

def write_manifest(destination,**kwargs):
    result=applied_motion_manifest(**kwargs)
    path=Path(destination);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    return result
