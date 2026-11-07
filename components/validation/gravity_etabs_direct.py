"""Read-only ETABS gravity OAPI extraction and direct OpenSees reconciliation.

[REF components/validation/etabs_direct_api.py] Existing CSI OAPI selection/units
and read-only semantics. ETABS v23 native validation is required.
The sole comparison case is an existing LINEAR ADD Dead(1)+Live(1)
combination; neither an EDB nor a result case is created/modified.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

UNITS_KN_M_C=6
BASE_FIELDS=('LoadCase','StepType','StepNum','FX','FY','FZ','MX','MY','MZ')
JOINT_FIELDS=('Obj','Elm','LoadCase','StepType','StepNum','F1','F2','F3','M1','M2','M3')
DISP_FIELDS=('Obj','Elm','LoadCase','StepType','StepNum','U1','U2','U3','R1','R2','R3')

def _out(raw,count,label):
    if not isinstance(raw,(tuple,list)) or len(raw)!=count+1:
        raise RuntimeError(f'{label}: API contract differs from expected {count} OUT values')
    if raw[-1] not in (0,None):raise RuntimeError(f'{label}: API returned {raw[-1]}')
    return raw[:-1]

def _names(api,label):
    n,names=_out(api.GetNameList(),2,label+'.GetNameList')
    if int(n)!=len(names):raise ValueError(label+': name count mismatch')
    return [str(x) for x in names]

def _snapshot(sap):
    setup=sap.Results.Setup
    cases=_names(sap.LoadCases,'LoadCases')
    combos=_names(sap.RespCombo,'RespCombo')
    return dict(units=sap.GetPresentUnits(),
        cases=[(x,bool(_out(setup.GetCaseSelectedForOutput(x),1,x)[0])) for x in cases],
        combos=[(x,bool(_out(setup.GetComboSelectedForOutput(x),1,x)[0])) for x in combos])

def _restore(sap,state):
    setup=sap.Results.Setup
    try:
        _out((setup.DeselectAllCasesAndCombosForOutput(),),0,'restore deselection')
        for x,flag in state['cases']:
            if flag:_out((setup.SetCaseSelectedForOutput(x),),0,'restore case '+x)
        for x,flag in state['combos']:
            if flag:_out((setup.SetComboSelectedForOutput(x),),0,'restore combo '+x)
    finally:
        _out((sap.SetPresentUnits(state['units']),),0,'restore units')

def _select(sap,case,combo=False):
    setup=sap.Results.Setup
    _out((setup.DeselectAllCasesAndCombosForOutput(),),0,'deselect all')
    if combo:
        _out((setup.SetComboSelectedForOutput(case),),0,'select combo '+case)
    else:
        _out((setup.SetCaseSelectedForOutput(case),),0,'select case '+case)

def _finite(x,label):
    value=float(x)
    if not math.isfinite(value):raise ValueError('Nonfinite '+label)
    return value

def _rows(raw,fields,label):
    result=_out(raw,len(fields)+1,label)
    n=int(result[0])
    if n<0:raise ValueError(label+': negative row count')
    for values in result[1:]:
        if len(values)<n:raise ValueError(label+': truncated array')
    return [dict(zip(fields,[arr[i] for arr in result[1:]])) for i in range(n)]

def _base(sap,case):
    raw=_out(sap.Results.BaseReact(),13,'Results.BaseReact')
    n=int(raw[0])
    if n<0 or any(len(a)<n for a in raw[1:10]):
        raise ValueError('BaseReact response array length mismatch')
    origin=dict(zip(('GX','GY','GZ'),[float(x) for x in raw[10:13]]))
    return [{**dict(zip(BASE_FIELDS,[a[i] for a in raw[1:10]])),**origin}
            for i in range(n) if str(raw[1][i])==case]

def _exact_one(rows,case,step=None,label='results'):
    candidates=[r for r in rows if str(r.get('LoadCase'))==case]
    if step is not None:
        candidates=[r for r in candidates if
                    str(r.get('StepType'))==str(step[0]) and
                    float(r.get('StepNum'))==float(step[1])]
    if len(candidates)!=1:
        raise ValueError(f'{label}: expected exactly one matching static {case} result, received {len(candidates)}')
    return candidates[0]

def _combo(sap,case):
    (kind,)=_out(sap.RespCombo.GetTypeCombo(case),1,'RespCombo.GetTypeCombo')
    if int(kind)!=0:raise ValueError('Requires a LINEAR ADD combination (type 0)')
    n,types,names,factors=_out(sap.RespCombo.GetCaseList(case),4,'RespCombo.GetCaseList')
    if n!=2:raise ValueError('Select exact Dead + Live combination, not nested/envelope')
    items=[dict(name=str(names[i]),factor=_finite(factors[i],'factor'),type=int(types[i])) for i in range(n)]
    if any(v['type']!=0 or abs(v['factor']-1)>1e-9 for v in items):
        raise ValueError('Both components must be load cases with factor 1.0')
    if {v['name'].strip().lower() for v in items}!={'dead','live'}:
        raise ValueError('Combination must refer to exact Dead and Live cases. Manually audit any alternative case composition.')
    return items

def _get_case_status(sap):
    raw=sap.Analyze.GetCaseStatus()
    n,names,states=_out(raw,3,'Analyze.GetCaseStatus')
    if int(n)!=len(names) or int(n)!=len(states):raise ValueError('Analysis status lengths differ')
    return {str(name):int(state) for name,state in zip(names,states)}

def _point_rows(sap,method,point,fields):
    return _rows(getattr(sap.Results,method)(point,0),fields,method+' '+point)

def _point_position(sap,point):
    x,y,z=_out(sap.PointObj.GetCoordCartesian(point),3,'GetCoordCartesian '+point)
    (restraint,)=_out(sap.PointObj.GetRestraint(point),1,'GetRestraint '+point)
    if len(restraint)!=6:raise ValueError('Incomplete restraint for '+point)
    return [float(x),float(y),float(z)],[bool(x) for x in restraint]

def extract_from_sap(sap,case='1. DL + LL',source_edb=None,allow_alternate_edb=False):
    """Get exactly one full-gravity concurrent result, without changing ETABS model.

    [REF components/validation/etabs_direct_api.py extract_from_sap] Restores
    original display units and result-selection state on success/failure.
    [REF docs/review/GRAVITY_ETABS_COMPARISON.md] Require exact model and case.
    """
    selected=Path(str(sap.GetModelFilename())).resolve()
    source_path=Path(source_edb).resolve() if source_edb else None
    differs=bool(source_path and selected!=source_path)
    if differs and not allow_alternate_edb:
        raise ValueError(
            'Active ETABS EDB differs from OpenSees export source: '+str(selected)+
            ' | Export source: '+str(source_path)+
            '. If this is an intentional gravity-only COPY of the same model, '
            'enable diagnostic alternate-EDB mode in the GUI. The result will '
            'remain UNVERIFIED for model equivalence until source geometry '
            'and loading are independently reconciled.')
    if not selected.is_file():
        raise FileNotFoundError('Active ETABS EDB unavailable: '+str(selected))
    state=_snapshot(sap)
    if case not in [x for x,_ in state['combos']]:
        raise ValueError('Required gravity combination not found: '+str(case))
    result=None
    try:
        _out((sap.SetPresentUnits(UNITS_KN_M_C),),0,'SetPresentUnits')
        components=_combo(sap,case)
        statuses=_get_case_status(sap)
        for c in components:
            if statuses.get(c['name'])!=4:
                raise RuntimeError('Analyze Dead and Live in ETABS first: '+c['name'])
        _select(sap,case,True)
        base=_exact_one(_base(sap,case),case,label='BaseReact')
        if str(base['StepType']).casefold() in ('max','min','envelope'):
            raise ValueError('Envelope reaction is not a simultaneous gravity state')
        base_vertical=_finite(base['FZ'],'BaseReact FZ')
        step=(str(base['StepType']),float(base['StepNum']))
        component_rows=[]
        for c in components:
            _select(sap,c['name'])
            v=_exact_one(_base(sap,c['name']),c['name'],label='component BaseReact')
            component_rows.append(dict(case=c['name'],factor=c['factor'],
                                       base_FZ_kN=_finite(v['FZ'],'FZ'),
                                       weighted_FZ_kN=c['factor']*_finite(v['FZ'],'FZ')))
        _select(sap,case,True)
        points=_names(sap.PointObj,'PointObj')
        supports=[];reaction_rows=[];displacements=[];errors=[]
        for name in points:
            try:
                xyz,flags=_point_position(sap,name)
            except Exception as exc:
                errors.append(dict(stage='point_inventory',point=name,error=str(exc)))
                continue
            if not any(flags):continue
            supports.append(dict(point=name,x_m=xyz[0],y_m=xyz[1],z_m=xyz[2],
                                 restraints=flags,is_fully_fixed=all(flags)))
            try:
                raw=_point_rows(sap,'JointReact',name,JOINT_FIELDS)
                matching=[r for r in raw if str(r['LoadCase'])==case and
                          str(r['StepType'])==step[0] and float(r['StepNum'])==step[1]]
                if len(matching)!=1:
                    raise ValueError('Expected exactly one concurrent support reaction row, got '+str(len(matching)))
                r=matching[0]
                reaction_rows.append(dict(point=name,x_m=xyz[0],y_m=xyz[1],z_m=xyz[2],
                    **{key:_finite(r[key],key) for key in ('F1','F2','F3','M1','M2','M3')},
                    axes='POINT_LOCAL',element=str(r['Elm'])))
            except Exception as exc:
                errors.append(dict(stage='JointReact',point=name,error=str(exc)))
            try:
                disp=_point_rows(sap,'JointDispl',name,DISP_FIELDS)
                d=_exact_one(disp,case,step,'JointDispl')
                displacements.append(dict(point=name,x_m=xyz[0],y_m=xyz[1],z_m=xyz[2],
                    **{key:_finite(d[key],key) for key in ('U1','U2','U3','R1','R2','R3')}))
            except Exception as exc:
                errors.append(dict(stage='JointDispl',point=name,error=str(exc)))
        components_total=sum(c['weighted_FZ_kN'] for c in component_rows)
        delta=components_total-base_vertical
        return dict(schema='ETABS_GRAVITY_DIRECT_V1',source_edb=str(selected),case=case,
            source_model_edb=str(source_path) if source_path else None,
            source_model_edb_sha256=_file_hash(source_path) if source_path and source_path.is_file() else None,
            active_etabs_edb_sha256=_file_hash(selected),
            model_identity_status=('ALTERNATE_EDB_UNVERIFIED' if differs else 'SAME_EDB_PATH'),
            matched_edb_identity=not differs,
            case_definition=components,case_step=dict(type=step[0],number=step[1]),
            units=dict(force='kN',length='m',moment='kN-m'),
            base_reactions=[base],source_case_base_reactions=component_rows,
            support_inventory=supports,joint_reactions=reaction_rows,
            support_displacements=displacements,
            summary=dict(base_reaction_FZ_kN=base_vertical,
                source_case_base_FZ_sum_kN=components_total,
                source_vs_combination_delta_kN=delta,
                additive_check=abs(delta)<=max(1.0,abs(base_vertical)*0.001),
                support_count=len(supports),joint_reaction_count=len(reaction_rows),
                joint_reactions_axes='POINT_LOCAL',
                data_complete=len(reaction_rows)==len(supports) and not errors,
                physical_roof_live_assignments_verified=False),
            warnings=errors+([dict(stage='model_identity',
                note='Alternate EDB was explicitly permitted for diagnostic comparison only. '
                     'Its geometry, section properties, load assignments and supports '
                     'are not proven identical to the OpenSees source model.')] if differs else [])+[
                dict(stage='units',note='Individual JointReact values use point local axes; BaseReact FZ is global.'),
                dict(stage='load_inventory',note='Combo definition does not prove roof-live physical assignments.'),
                dict(stage='support_scope',note='Ground springs/links and internal mesh reaction nodes may need additional evidence.')])
    finally:
        _restore(sap,state)

def _file_hash(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def compare_existing(etabs,open_sees_result):
    """Compare actual ETABS base FZ to matching completed OpenSees full gravity.

    [REF docs/review/GRAVITY_ETABS_COMPARISON.md] Reject nonmatching profiles.
    """
    if not open_sees_result.get('ok') or open_sees_result.get('gravity_profile')!='GRAVITY_1.0D_1.0L':
        raise ValueError('OpenSees result must be a completed full 1.0D+1.0L gravity run')
    r=open_sees_result['report']
    # Different legacy report key aliases are accepted only if actually recorded.
    def get(keys):
        for key in keys:
            if key in r:return _finite(r[key],key)
        raise ValueError('OpenSees report missing '+str(keys))
    applied=get(('applied_vertical_load_kN','total_downward_load_kN'))
    reaction=get(('support_vertical_reaction_kN','total_vertical_reaction_kN'))
    etabs_fz=_finite(etabs['summary']['base_reaction_FZ_kN'],'ETABS FZ')
    delta=etabs_fz-reaction
    percent=abs(delta)/abs(reaction)*100 if reaction else None
    return dict(status='COMPARISON_NOT_ENGINEERING_ACCEPTANCE',case=etabs['case'],
        etabs_base_FZ_kN=etabs_fz,opensees_support_FZ_kN=reaction,
        opensees_applied_kN=applied,difference_kN=delta,
        percent_difference=percent,
        matched_edb_identity=etabs.get('matched_edb_identity',False),
        model_identity_status=etabs.get('model_identity_status','UNVERIFIED'),
        limitations=['Only global reaction totals compared; self-weight, slab forces and displacement equivalence remain to be checked.'])

def export_direct(folder,etabs,comp):
    """Export audit JSON, CSV and Excel into existing gravity output folder.

    [REF components/gravity/comparison_bundle.py export_bundle] Uses matching
    source naming for the already integrated gravity evidence ZIP workflow.
    """
    out=Path(folder);out.mkdir(parents=True,exist_ok=True)
    (out/'etabs_gravity.json').write_text(json.dumps(etabs,indent=2),encoding='utf8')
    (out/'Direct_Gravity_Comparison.json').write_text(json.dumps(comp,indent=2),encoding='utf8')
    for name,rows in (('ETABS_Fixed_Support_Reactions.csv',etabs['joint_reactions']),
                      ('ETABS_Base_Reactions.csv',etabs['base_reactions']),
                      ('ETABS_Support_Displacements.csv',etabs['support_displacements'])):
        if rows:
            cols=list(dict.fromkeys(k for row in rows for k in row.keys()))
            with (out/name).open('w',encoding='utf-8-sig',newline='') as h:
                w=csv.DictWriter(h,fieldnames=cols,extrasaction='ignore')
                w.writeheader();w.writerows(rows)
    try:
        from openpyxl import Workbook
        from openpyxl.styles import PatternFill,Font
        wb=Workbook();ws=wb.active;ws.title='Comparison'
        for key,value in comp.items():
            if not isinstance(value,(list,dict)):ws.append([key,value])
        for title,rows in [('ETABS supports',etabs['joint_reactions']),
                           ('ETABS base',etabs['base_reactions']),
                           ('ETABS displacements',etabs['support_displacements']),
                           ('Source cases',etabs['source_case_base_reactions'])]:
            sheet=wb.create_sheet(title)
            if rows:
                columns=list(dict.fromkeys(k for row in rows for k in row))
                sheet.append(columns)
                for row in rows:sheet.append([row.get(c) for c in columns])
                sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
                for c in sheet[1]:
                    c.font=Font(bold=True,color='FFFFFF')
                    c.fill=PatternFill('solid',fgColor='1E3A5F')
        wb.save(out/'ETABS_OpenSees_Direct_Gravity_Comparison.xlsx')
    except ImportError:
        pass
    return out

def connect_and_compare(export_dir,gravity_result_path,case='1. DL + LL',output_dir=None,allow_alternate_edb=False):
    """Read attached ETABS EDB and compare with existing gravity JSON.

    [REF components/validation/etabs_direct_api.py connect_and_extract] Existing
    read-only ETABS connector; no model opening, saving or analysis.
    """
    from OpenSees_Project_Inputs_V123 import connect_etabs
    import json
    folder=Path(export_dir)
    from components.inputs.project_workbooks import _source_edb_path
    source=_source_edb_path(folder)
    if not source:raise ValueError('Export lacks source EDB identity; re-export rather than guessing')
    if not Path(source).is_file():raise FileNotFoundError('ETABS source EDB path is inaccessible: '+source)
    gravity=Path(gravity_result_path)
    if not gravity.is_file():raise FileNotFoundError('OpenSees gravity JSON missing: '+str(gravity))
    app=connect_etabs()
    data=extract_from_sap(app.SapModel,case,source_edb=source,
                          allow_alternate_edb=allow_alternate_edb)
    result=json.loads(gravity.read_text(encoding='utf-8-sig'))
    comp=compare_existing(data,result)
    out=export_direct(output_dir or gravity.parent/'Gravity_ETABS_OpenSees_Direct',data,comp)
    return comp,out
