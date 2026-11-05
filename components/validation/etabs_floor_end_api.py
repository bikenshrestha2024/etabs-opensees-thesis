"""Read-only signed ETABS floor-node displacement extraction for NBC §5.4.2.

Requires the SAME already-open EDB, known ETABS point object names, explicit
centered-CM STATIC case and one user-reviewed StepType/StepNum. No CQC
envelopes are accepted. This is a source connector, not proof of correct
CM loading or plan perimeter selection.

ETABS v23 native integration has NOT been executed in GitHub Linux CI.
"""
from __future__ import annotations
import math
from pathlib import Path

from components.validation.etabs_direct_api import (
    UNITS_KN_M_C,_arrays,_ok,_select,_snapshot_setup,_restore_setup,
)
from components.validation.floor_end_extraction import _bool,_finite


def extract_centered_from_sap(sap,geometry,*,source_edb,limit_state,case,
                              axis,step_type,step_number,reviewed_centered_cm):
    """Return normalized signed Ux/Uy [m] rows for matching physical end nodes.

    Input geometry rows include node_id, storey and is_perimeter; this
    function intentionally reads only the already-reviewed perimeter nodes.
    CSI JointDispl signature: n,Obj,Elm,LoadCase,StepType,StepNum,
    U1,U2,U3,R1,R2,R3,ret. Open-model selection/units are always restored.
    """
    if reviewed_centered_cm is not True:
        raise ValueError("Explicit independent centered-CM loading review required")
    state=str(limit_state).upper();axis=str(axis).upper()
    if state not in ("ULS","SLS") or axis not in ("X","Y"):
        raise ValueError("Single ULS/SLS and X/Y required")
    case=str(case).strip()
    step_type=str(step_type).strip()
    step_number=_finite(step_number,"ETABS selected StepNum")
    if not case or not step_type or step_type.lower() in ("max","min","envelope","mode"):
        raise ValueError("Select a single centered static case/step, not a CQC/max envelope")
    model=Path(source_edb).resolve()
    from components.inputs.project_workbooks import _portable_source_stem
    import re
    source_name=_portable_source_stem(model).casefold()
    if re.search(r'(?<![a-z])(ultimate|uls)(?![a-z])',source_name) and state!='ULS':
        raise ValueError('Cross-state source: Ultimate EDB cannot be extracted as SLS')
    if re.search(r'(?<![a-z])(service|sls)(?![a-z])',source_name) and state!='SLS':
        raise ValueError('Cross-state source: Service EDB cannot be extracted as ULS')
    if not model.is_file() or model.suffix.lower()!=".edb":
        raise FileNotFoundError("The original .EDB must exist locally")
    active=Path(str(sap.GetModelFilename())).resolve()
    if active!=model:
        raise ValueError("Active ETABS EDB differs from the selected source file")
    original_units=sap.GetPresentUnits()
    snapshot=_snapshot_setup(sap)
    output=[]
    seen=set()
    try:
        _ok(sap.SetPresentUnits(UNITS_KN_M_C),"set kN-m-C units")
        _select(sap,case)
        for row in geometry:
            node=str(row["node_id"]).strip()
            story=str(row["storey"]).strip()
            if not _bool(row["is_perimeter"],"is_perimeter"):
                continue
            if not node or not story:
                raise ValueError("Missing reviewed ETABS point and story name")
            if (story,node) in seen:
                raise ValueError("Duplicate ETABS point/story input")
            seen.add((story,node))
            r=_arrays(sap.Results.JointDispl(node,0),12,"JointDispl")
            matching=[]
            for i in range(r[0]):
                if str(r[3][i])!=case:continue
                if str(r[4][i])!=step_type:continue
                if not math.isclose(_finite(r[5][i],"StepNum"),step_number,rel_tol=0,abs_tol=1e-8):
                    continue
                matching.append((r[6][i],r[7][i]))
            if len(matching)!=1:
                raise RuntimeError(f"Expected exactly one signed ETABS displacement "
                                   f"for {node} at {case}/{step_type}/{step_number}; found {len(matching)}")
            ux,uy=matching[0]
            output.append(dict(node_id=node,storey=story,limit_state=state,
                case=case,axis=axis,step=str(step_number),ux_m=_finite(ux,"U1"),
                uy_m=_finite(uy,"U2"),centered_cm_load="true",
                response_basis="signed_centered_linear_increment"))
    finally:
        try:_restore_setup(sap,snapshot)
        finally:_ok(sap.SetPresentUnits(original_units),"restore display units")
    if not output:
        raise ValueError("No reviewed ETABS perimeter nodes found")
    return output


def connect_and_extract(geometry,*,source_edb,limit_state,case,axis,
                        step_type,step_number,reviewed_centered_cm):
    """Attach to an existing ETABS instance; source .EDB stays read-only."""
    from OpenSees_Project_Inputs_V123 import connect_etabs
    app=connect_etabs()
    return extract_centered_from_sap(app.SapModel,geometry,source_edb=source_edb,
        limit_state=limit_state,case=case,axis=axis,step_type=step_type,
        step_number=step_number,reviewed_centered_cm=reviewed_centered_cm)
