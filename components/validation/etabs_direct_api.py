"""Read-only, explicit-case ETABS API results for model-equivalence comparison.

SI outputs: periods [s], base reactions [kN], point displacements [m],
story drift ratios [-]. This uses the attached ETABS session and never
runs/saves/unlocks its EDB. Calling Result.Setup/SetPresentUnits temporarily
changes session settings; both are snapshotted and restored in finally.

References: CSI ETABS API Results.ModalPeriod, ModalParticipatingMassRatios,
BaseReact, StoryDrifts, JointDispl; Results.Setup and SapModel.SetPresentUnits.
The 2016 API signatures are a documented baseline; verify ETABS v23 COM
binding with the supplied mocked contract and native Windows integration.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

UNITS_KN_M_C = 6  # ETABS eUnits.kN_m_C; verify active ETABS API enumeration.
FIELD_NAMES = ("method","limit_state","case","axis","location","metric","unit","basis")


def _ok(result, label):
    if result not in (0, None):
        raise RuntimeError(f"ETABS {label} returned {result!r}")


def _arrays(raw, expected, label):
    """COM out tuples end with the ETABS return code; no silent field shift."""
    if not isinstance(raw, (tuple,list)) or len(raw)!=expected+1:
        raise RuntimeError(f"ETABS {label}: expected {expected} returned arguments and code, got {type(raw).__name__} with {len(raw) if isinstance(raw,(tuple,list)) else 'unknown'} values; check ETABS v23 API.")
    _ok(raw[-1], label)
    count=raw[0]
    if not isinstance(count,int) or count<0:
        raise RuntimeError(f"ETABS {label}: invalid result count {count!r}")
    for a in raw[1:]:
        if hasattr(a,"__len__") and len(a)<count:
            raise RuntimeError(f"ETABS {label}: returned array shorter than NumberResults.")
    return raw[:-1]


def _names(api, label):
    raw=api.GetNameList()
    if not isinstance(raw,(tuple,list)) or len(raw)<3:
        raise RuntimeError(f"ETABS {label}.GetNameList signature unexpected.")
    _ok(raw[-1], label+".GetNameList")
    names=list(raw[1])
    if len(names)!=int(raw[0]):
        raise RuntimeError(f"ETABS {label} name count mismatch.")
    return names


def _selection_flag(value, label):
    # comtypes GetCaseSelectedForOutput normally returns (bool, returncode).
    if not isinstance(value,(tuple,list)) or len(value)!=2:
        raise RuntimeError(f"ETABS {label} selection status signature unknown.")
    _ok(value[-1], label)
    return bool(value[0])


def _snapshot_setup(sap):
    # The entire selection state, not only cases used by this extractor.
    cases=_names(sap.LoadCases,"LoadCases")
    combos=_names(sap.RespCombo,"RespCombo")
    setup=sap.Results.Setup
    return ([(c,_selection_flag(setup.GetCaseSelectedForOutput(c),c)) for c in cases],
            [(c,_selection_flag(setup.GetComboSelectedForOutput(c),c)) for c in combos])


def _restore_setup(sap, snapshot):
    cases,combos=snapshot
    setup=sap.Results.Setup
    _ok(setup.DeselectAllCasesAndCombosForOutput(),"clear result selection on restore")
    for name,selected in cases:
        if selected:_ok(setup.SetCaseSelectedForOutput(name),"restore case "+name)
    for name,selected in combos:
        if selected:_ok(setup.SetComboSelectedForOutput(name),"restore combo "+name)


def _select(sap,case):
    setup=sap.Results.Setup
    _ok(setup.DeselectAllCasesAndCombosForOutput(),"clear output selection")
    _ok(setup.SetCaseSelectedForOutput(str(case)),"select "+str(case))


def _finite(value,label):
    v=float(value)
    if not math.isfinite(v):
        raise ValueError(label+" is nonfinite")
    return v


def validate_mapping(mapping):
    """Explicit ETABS→OpenSees case/point identities, no fuzzy case guessing."""
    cases=mapping.get("cases")
    if not isinstance(cases,list) or not cases:
        raise ValueError("Provide at least one explicit ETABS case mapping.")
    seen=set()
    for m in cases:
        for key in ("etabs_case","method","limit_state","case","axis"):
            if not str(m.get(key,"")).strip():
                raise ValueError("Mapping case missing "+key)
        if m["method"] not in ("MRSM","MODAL"):
            raise ValueError("Direct API supports MRSM or MODAL only; no ESM case inference.")
        if m["limit_state"] not in ("ULS","SLS"):
            raise ValueError("State must be ULS or SLS.")
        if m["method"]=="MRSM" and m["axis"] not in ("X","Y"):
            raise ValueError("MRSM axis must be X or Y.")
        if m["method"]=="MRSM" and not m["case"].startswith(m["axis"]+"_E"):
            raise ValueError("MRSM OpenSees case must specify axis and E0/Eplus/Eminus.")
        ident=(m["method"],m["limit_state"],m["case"],m["axis"])
        if ident in seen:raise ValueError("Duplicated OpenSees case mapping "+str(ident))
        seen.add(ident)
        if m["method"]=="MRSM" and not m.get("story_map"):
            raise ValueError("MRSM mapping requires exact ETABS story-name to OpenSees storey-number mapping.")
        if m.get("force_basis_verified") and not m.get("force_scale_note"):
            raise ValueError("Force-basis verification needs a force_scale_note explaining CQC and NBC §7.5 handling.")
        if m.get("displacement_basis_verified") and not m.get("displacement_scale_note"):
            raise ValueError("Displacement/drift-basis verification needs a displacement_scale_note.")
        names=list(m.get("story_map",{}).values())
        if len(names)!=len(set(map(str,names))):
            raise ValueError("Multiple ETABS stories map to the same OpenSees storey.")
        for point in m.get("points",[]):
            if not point.get("etabs_point") or not str(point.get("story_number","")).strip():
                raise ValueError("Point map requires ETABS point object and OpenSees story_number.")
    return cases


def extract_from_sap(sap, mapping):
    """Read results directly from an already analysed ETABS model object.

    Physical comparability is NOT inferred from same-looking case names.
    Without explicit verification flags results carry incompatible basis
    markers, blocking misleading equality. No COM call is made in tests.
    """
    cases=validate_mapping(mapping)
    from components.inputs.project_workbooks import source_limit_state
    # The ETABS EDB selected here must correspond to the actual OpenSees
    # export. A source-labelled Ultimate model must not be compared with
    # Service responses (or vice versa), even when numeric units and case
    # names happen to match.
    model_state,_=source_limit_state(mapping.get("export_dir",""))
    if not model_state:
        name=Path(str(mapping.get("source_edb",""))).stem.casefold()
        import re
        ultimate=bool(re.search(r'(?<![a-z])(ultimate|uls)(?![a-z])',name))
        service=bool(re.search(r'(?<![a-z])(service|sls)(?![a-z])',name))
        if ultimate != service:model_state='ULS' if ultimate else 'SLS'
    if model_state:
        for case in cases:
            if case["limit_state"]!=model_state:
                raise ValueError("Cross-limit-state comparison blocked: source EDB is "+
                                 model_state+" but case is "+case["limit_state"])
    selected=Path(str(mapping.get("source_edb",""))).expanduser()
    actual=Path(str(sap.GetModelFilename())).resolve()
    if not selected.is_file():
        raise FileNotFoundError("Select an existing original .EDB file on this Windows PC.")
    if selected.resolve()!=actual:
        raise ValueError("Active ETABS model is NOT selected source EDB. Open the correct file in ETABS first; no automatic model switching.")
    original_units=sap.GetPresentUnits()
    snapshot=_snapshot_setup(sap)
    rows=[]
    def add(m,location,metric,unit,basis,value,source_case,extra=None,axis_override=None):
        if value is None:return
        rows.append({**{k:str(m.get(k,"")) for k in ("method","limit_state","case","axis")},
            "location":str(location),"metric":metric,"unit":unit,"basis":basis,
            "value":_finite(value,metric),"source_file":str(actual),
            "etabs_source_case":str(source_case),"etabs_step_type":str((extra or {}).get("step_type","")),
            "etabs_step_number":(extra or {}).get("step_number",""),
            **({"axis":axis_override} if axis_override is not None else {})})
    try:
        _ok(sap.SetPresentUnits(UNITS_KN_M_C),"SetPresentUnits(kN-m-C)")
        for m in cases:
            source=m["etabs_case"]
            _select(sap,source)
            if m["method"]=="MODAL":
                r=_arrays(sap.Results.ModalPeriod(),8,"ModalPeriod")
                # NumberResults, LoadCase, StepType, StepNum, Period,
                # Frequency, CircFreq, EigenValue (CSI official signature).
                for i in range(r[0]):
                    if str(r[1][i])!=source:continue
                    mode=int(r[3][i])
                    add(m,mode,"period","s","eigen" if m.get("modal_mode_pairing_verified") else "ETABS_mode_unpaired",
                        r[4][i],source,{"step_type":r[2][i],"step_number":r[3][i]},axis_override="")
                # Modal mass is recorded for audit only; aggregate is not an
                # equivalent shape pairing or matching OpenSees mass model.
                mm=_arrays(sap.Results.ModalParticipatingMassRatios(),17,"ModalParticipatingMassRatios")
                matched=[]
                for i in range(mm[0]):
                    if str(mm[1][i])!=source:continue
                    matched.append(i)
                    # Individual effective modal mass ratio; use the same
                    # mode/axis/basis as the OpenSees modal collector.
                    add(m,int(mm[3][i]),"individual_mass","percent","modal_mass",
                        _finite(mm[5][i],"UX")*100,source,axis_override="X")
                    add(m,int(mm[3][i]),"individual_mass","percent","modal_mass",
                        _finite(mm[6][i],"UY")*100,source,axis_override="Y")
                if matched:
                    last=max(matched,key=lambda i:float(mm[3][i]))
                    # CSI SumUX / SumUY fields are 8 and 9. The OpenSees
                    # modal audit reports cumulative mass in percent at ALL.
                    add(m,"ALL","cumulative_mass","percent","modal_mass",
                        _finite(mm[8][last],"SumUX")*100,source,axis_override="X")
                    add(m,"ALL","cumulative_mass","percent","modal_mass",
                        _finite(mm[9][last],"SumUY")*100,source,axis_override="Y")
                continue
            force_basis=("CQC_force_scaled" if m.get("force_basis_verified") else "ETABS_force_unverified")
            disp_basis=("CQC_design_unscaled_by_7_5" if m.get("displacement_basis_verified") and m.get("drift_location_verified") else "ETABS_displacement_unverified")
            r=_arrays(sap.Results.BaseReact(),13,"BaseReact")
            if not r[0]:raise RuntimeError("ETABS returned no BaseReact rows for "+source)
            for i in range(r[0]):
                if str(r[1][i])!=source:continue
                axis_index=4 if m["axis"]=="X" else 5
                # CQC envelopes require magnitudes; do not sum signed
                # modal results or interpret this as a transient base force.
                add(m,"BASE","base_shear","kN",force_basis,abs(_finite(r[axis_index][i],"base reaction")),source,
                    {"step_type":r[2][i],"step_number":r[3][i]})
            dr=_arrays(sap.Results.StoryDrifts(),11,"StoryDrifts")
            # CSI v18+ StoryDrifts.Drift is a dimensionless drift ratio.
            # The StoryDrifts API reports envelope at its critical plan
            # point; this is comparable only to matching OpenSees edge drift.
            grouped={}
            for i in range(dr[0]):
                if str(dr[2][i])!=source or str(dr[5][i]).strip().upper()!=m["axis"]:continue
                story=m["story_map"].get(str(dr[1][i]))
                if story is None:continue
                value=abs(_finite(dr[6][i],"drift"))
                grouped[str(story)]=max(grouped.get(str(story),0.),value)
            for story,v in grouped.items():
                add(m,story,"drift_ratio","ratio",disp_basis,v,source)
            for point in m.get("points",[]):
                p=str(point["etabs_point"])
                dis=_arrays(sap.Results.JointDispl(p,0),12,"JointDispl")
                vals=[abs(_finite(dis[6 if m["axis"]=="X" else 7][i],"U")) for i in range(dis[0]) if str(dis[3][i])==source]
                if not vals:
                    raise RuntimeError("No JointDispl output for "+source+" / ETABS object "+p)
                point_basis=("CQC_design_unscaled_by_7_5"
                             if m.get("displacement_basis_verified") and
                                point.get("same_location_verified") is True and
                                m.get("point_response_basis_verified") is True
                             else "ETABS_point_location_unverified")
                add(m,str(point["story_number"]),"displacement","m",point_basis,max(vals),source,
                    {"point_object":p})
    finally:
        # Restore original case/combo selections and display units even on errors.
        try:_restore_setup(sap,snapshot)
        finally:_ok(sap.SetPresentUnits(original_units),"restore ETABS present units")
    if not rows:
        raise RuntimeError("No ETABS API result rows for configured case mapping.")
    return rows


def connect_and_extract(folder, mapping):
    """Attach to ETABS (Windows only); refuse wrong loaded source model.

    No File.OpenFile/RunAnalysis/Save/unlock, and no upload of source EDB.
    The existing project connector attaches to the active ETABS session.
    """
    from OpenSees_Project_Inputs_V123 import connect_etabs
    from components.inputs.project_workbooks import source_limit_state
    current,reason=source_limit_state(folder)
    if current:
        for item in validate_mapping(mapping):
            if item['limit_state']!=current:
                raise ValueError('Selected export is '+current+
                                 ' but ETABS comparison requests '+item['limit_state']+
                                 '. '+reason)
    app=connect_etabs()
    return extract_from_sap(app.SapModel,{**mapping,'export_dir':str(folder)})


def fingerprint(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):digest.update(block)
    return digest.hexdigest()


def mapping_template(source_edb):
    """Produce a safe incomplete example; users must name real ETABS cases."""
    return {"source_edb":str(source_edb),"assumptions_verified":False,
        "notes":"Verify spectrum, mass, stiffness, CQC, NBC force scale and eccentricity before assigning PASS.",
        "cases":[
            {"etabs_case":"REPLACE_WITH_ACTUAL_ETABS_MODAL_CASE","method":"MODAL",
             "limit_state":"ULS","case":"MODAL","axis":"X","modal_mode_pairing_verified":False},
            {"etabs_case":"REPLACE_WITH_ACTUAL_ETABS_RSX_CASE","method":"MRSM",
             "limit_state":"ULS","case":"X_E0","axis":"X",
             "story_map":{},"points":[],"force_basis_verified":False,
             "displacement_basis_verified":False}]} 
