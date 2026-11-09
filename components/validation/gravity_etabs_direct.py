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
import traceback
import shutil
import uuid
import os
import tempfile
from datetime import datetime, timezone
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

def _gravity_run_flags(sap):
    """Inspect ETABS load-case run flags without changing the source model.

    [REF CSI ETABS OAPI cAnalyze.GetRunCaseFlag] Returns enabled run flags.
    """
    n,names,flags=_out(sap.Analyze.GetRunCaseFlag(),3,'Analyze.GetRunCaseFlag')
    if int(n)!=len(names) or int(n)!=len(flags):
        raise ValueError('ETABS analysis run-flag arrays differ in length')
    return {str(name):bool(flag) for name,flag in zip(names,flags)}


def _enable_gravity_cases_on_copy(sap,log):
    """Enable only existing Dead and Live cases on the isolated working EDB.

    [REF CSI ETABS OAPI cAnalyze.SetRunCaseFlag] Mutate working copy only.
    A gravity comparison must not trigger all enabled seismic histories.
    """
    before=_gravity_run_flags(sap)
    for needed in ('Dead','Live'):
        if needed not in before:
            raise ValueError('ETABS working copy lacks required load case '+needed)
    log('ETABS_RUN_FLAGS','Read run flags on isolated EDB copy',
        enabled_count=sum(before.values()),
        dead_enabled=before['Dead'],live_enabled=before['Live'])
    _out((sap.Analyze.SetRunCaseFlag('',False,True),),0,'Disable all working-copy cases')
    for needed in ('Dead','Live'):
        _out((sap.Analyze.SetRunCaseFlag(needed,True,False),),0,
             'Enable working-copy '+needed)
    after=_gravity_run_flags(sap)
    if not after.get('Dead') or not after.get('Live'):
        raise RuntimeError('ETABS did not enable both Dead and Live for analysis')
    enabled=[k for k,v in after.items() if v]
    if set(enabled)!={'Dead','Live'}:
        raise RuntimeError('Unexpected extra enabled cases on gravity working copy: '+str(enabled))
    log('ETABS_RUN_FLAGS','Enabled only Dead and Live for gravity analysis',
        enabled=enabled,former_enabled_count=sum(before.values()))
    return before,after


def _point_rows(sap,method,point,fields):
    return _rows(getattr(sap.Results,method)(point,0),fields,method+' '+point)

def _point_position(sap,point):
    x,y,z=_out(sap.PointObj.GetCoordCartesian(point),3,'GetCoordCartesian '+point)
    (restraint,)=_out(sap.PointObj.GetRestraint(point),1,'GetRestraint '+point)
    if len(restraint)!=6:raise ValueError('Incomplete restraint for '+point)
    return [float(x),float(y),float(z)],[bool(x) for x in restraint]

def extract_from_sap(sap,case='1. DL + LL',source_edb=None,allow_alternate_edb=False,log=None):
    """Get exactly one full-gravity concurrent result, without changing ETABS model.

    [REF components/validation/etabs_direct_api.py extract_from_sap] Restores
    original display units and result-selection state on success/failure.
    [REF docs/review/GRAVITY_ETABS_COMPARISON.md] Require exact model and case.
    """
    log=log or (lambda stage,message,**kw:None)
    selected=Path(str(sap.GetModelFilename())).resolve()
    log('ETABS_MODEL','Read ETABS active model',path=str(selected))
    source_path=Path(source_edb).resolve() if source_edb else None
    path_differs=bool(source_path and selected!=source_path)
    identical_bytes=False
    if path_differs and source_path.is_file():
        identical_bytes=_file_hash(selected)==_file_hash(source_path)
    differs=path_differs and not identical_bytes
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
    log('ETABS_SELECTION','Captured display units and selected output cases',
        units=state['units'],cases_count=len(state['cases']),
        combos_count=len(state['combos']))
    if case not in [x for x,_ in state['combos']]:
        raise ValueError('Required gravity combination not found: '+str(case))
    result=None
    try:
        _out((sap.SetPresentUnits(UNITS_KN_M_C),),0,'SetPresentUnits')
        components=_combo(sap,case)
        log('ETABS_COMBO','Confirmed linear additive gravity combination',
            combo=case,components=components)
        # GetCaseStatus is advisory: ETABS can report incomplete or different
        # status codes after reopening a copy, even when valid saved result
        # arrays are available. Real BaseReact rows are the authoritative gate.
        try:
            statuses=_get_case_status(sap)
            log('ETABS_CASE_STATUS','Read analysis case status (advisory only)',
                selected_case_status={c['name']:statuses.get(c['name']) for c in components},
                status_note='Only actual finite result rows are used to establish availability')
        except Exception as exc:
            log('ETABS_CASE_STATUS_WARNING','Could not read analysis status; checking real results',error=str(exc))
            statuses={}
        _select(sap,case,True)
        log('ETABS_RESULTS','Selecting existing gravity combination output',combo=case)
        try:
            base=_exact_one(_base(sap,case),case,label='BaseReact')
        except Exception as exc:
            raise RuntimeError('ETABS gravity combination has no usable BaseReact results for '+case+
                '; verify Dead and Live have been analyzed and the combo exists. '
                'API status='+str({c['name']:statuses.get(c['name']) for c in components})+
                '; result error='+str(exc)) from exc
        log('ETABS_BASE_REACTION','Read global combination base reaction',
            FZ_kN=base.get('FZ'),step=base.get('StepType'),step_number=base.get('StepNum'))
        if str(base['StepType']).casefold() in ('max','min','envelope'):
            raise ValueError('Envelope reaction is not a simultaneous gravity state')
        base_vertical=_finite(base['FZ'],'BaseReact FZ')
        step=(str(base['StepType']),float(base['StepNum']))
        component_rows=[]
        for c in components:
            _select(sap,c['name'])
            try:
                v=_exact_one(_base(sap,c['name']),c['name'],label='component BaseReact')
            except Exception as exc:
                raise RuntimeError('Missing saved ETABS BaseReact results for case '+c['name']+
                    '; API status='+str(statuses.get(c['name']))+
                    '; actual result='+str(exc)) from exc
            log('ETABS_COMPONENT_REACTION','Read load case base reaction',
                case=c['name'],FZ_kN=v.get('FZ'),scale=c['factor'])
            component_rows.append(dict(case=c['name'],factor=c['factor'],
                                       base_FZ_kN=_finite(v['FZ'],'FZ'),
                                       weighted_FZ_kN=c['factor']*_finite(v['FZ'],'FZ')))
        _select(sap,case,True)
        points=_names(sap.PointObj,'PointObj')
        log('ETABS_POINTS','Inventory ETABS point objects',count=len(points))
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
                # JointReact is reported in point LOCAL axes. The vertical
                # global reaction equals F3 only for an unrotated point.
                # Any nonzero/advanced/unknown axes must remain unverified;
                # do not silently compare local F3 with global OpenSees RZ.
                try:
                    angles=_out(sap.PointObj.GetLocalAxes(name),4,
                                'PointObj.GetLocalAxes '+name)
                    ax=[_finite(v,'axis angle') for v in angles[:3]]
                    advanced=bool(angles[3])
                    aligned=all(abs(v)<1e-9 for v in ax) and not advanced
                    basis='GLOBAL_Z_VERIFIED_DEFAULT_AXES' if aligned else 'POINT_LOCAL_ROTATED'
                except Exception as exc:
                    aligned=False;ax=None;advanced=None
                    basis='POINT_LOCAL_AXES_UNAVAILABLE'
                    errors.append(dict(stage='point_local_axes',point=name,error=str(exc)))
                reaction_rows.append(dict(point=name,x_m=xyz[0],y_m=xyz[1],z_m=xyz[2],
                    **{key:_finite(r[key],key) for key in ('F1','F2','F3','M1','M2','M3')},
                    rz_global_kN=_finite(r['F3'],'F3') if aligned else None,
                    global_z_basis=basis,local_axis_angles_deg=ax,
                    local_axes_advanced=advanced,
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
        log('ETABS_SUPPORTS','Finished restrained point reaction/displacement extraction',
            points_scanned=len(points),restrained_points=len(supports),
            reaction_records=len(reaction_rows),displacement_records=len(displacements),
            error_count=len(errors),error_samples=errors[:6])
        components_total=sum(c['weighted_FZ_kN'] for c in component_rows)
        log('ETABS_EQUILIBRIUM','Compare Dead+Live case sums with linear combination',
            combo_FZ_kN=base_vertical,case_sum_FZ_kN=components_total,
            delta_kN=components_total-base_vertical)
        delta=components_total-base_vertical
        return dict(schema='ETABS_GRAVITY_DIRECT_V1',source_edb=str(selected),case=case,
            source_model_edb=str(source_path) if source_path else None,
            source_model_edb_sha256=_file_hash(source_path) if source_path and source_path.is_file() else None,
            active_etabs_edb_sha256=_file_hash(selected),
            model_identity_status=('ALTERNATE_EDB_UNVERIFIED' if differs else
                                   'IDENTICAL_EDB_BYTES_WORKING_COPY' if identical_bytes else
                                   'SAME_EDB_PATH'),
            is_isolated_working_copy=bool(identical_bytes),
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
                for row in rows:
                    # ETABS point local-axis metadata includes three-value lists;
                    # XLSX cells accept scalars only. Preserve structured values
                    # in machine-readable JSON and serialize for Excel display.
                    sheet.append([json.dumps(row.get(c),ensure_ascii=False)
                                  if isinstance(row.get(c),(list,dict,tuple))
                                  else row.get(c) for c in columns])
                sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
                for c in sheet[1]:
                    c.font=Font(bold=True,color='FFFFFF')
                    c.fill=PatternFill('solid',fgColor='1E3A5F')
        wb.save(out/'ETABS_OpenSees_Direct_Gravity_Comparison.xlsx')
    except ImportError:
        pass
    return out

def _new_etabs_instance(edb_path, *, exe_path=None):
    """Launch a PRIVATE ETABS COM instance and open the selected EDB.

    [REF CSI ETABS OAPI cHelper.CreateObjectProgID; cOAPI.ApplicationStart]
    [REF CSI ETABS OAPI cSapModel.File.OpenFile] No attached ETABS instance
    is taken over or closed. Caller owns and must finally close this instance.
    """
    import comtypes.client
    helper=comtypes.client.CreateObject('ETABSv1.Helper')
    try:
        from comtypes.gen import ETABSv1
        helper=helper.QueryInterface(ETABSv1.cHelper)
    except (ImportError,AttributeError):
        # The interface may be usable through late-bound COM on some machines.
        pass
    if exe_path:
        exe=Path(exe_path).expanduser().resolve()
        if not exe.is_file():raise FileNotFoundError('ETABS executable not found: '+str(exe))
        instance=helper.CreateObject(str(exe))
    else:
        instance=helper.CreateObjectProgID('CSI.ETABS.API.ETABSObject')
    try:
        result=instance.ApplicationStart()
        if result not in (0,None):
            raise RuntimeError('ETABS ApplicationStart returned '+str(result))
        opened=instance.SapModel.File.OpenFile(str(edb_path))
        if opened not in (0,None):
            raise RuntimeError('ETABS File.OpenFile returned '+str(opened)+
                               '; check EDB version, file access and license')
        actual=Path(str(instance.SapModel.GetModelFilename())).resolve()
        if actual!=Path(edb_path).resolve():
            raise RuntimeError('ETABS opened a different file: '+str(actual))
    except BaseException:
        # Instance belongs solely to this request; never touch pre-existing ETABS.
        try:instance.ApplicationExit(False)
        except Exception:pass
        raise
    return instance


def _release_owned_instance(instance):
    """Close ONLY ETABS started for the direct gravity comparison; do not save.

    [REF CSI ETABS OAPI cOAPI.ApplicationExit(False)] False = no EDB save.
    """
    if instance is not None:
        code=instance.ApplicationExit(False)
        if code not in (0,None):
            raise RuntimeError('Owned ETABS ApplicationExit(False) returned '+str(code))


def _short_etabs_working_copy(selected,expected_sha,log):
    """Use short, private, writable model path for CSI solver sidecar creation.

    [REF Microsoft Win32 MAX_PATH] CSI analysis workers may not support a
    300+ character result/model path. The original ETABS file remains read-only.
    User may override TEMP_ROOT via ETABS_GRAVITY_TEMP_ROOT for short D: paths.
    """
    root=Path(os.environ.get("ETABS_GRAVITY_TEMP_ROOT") or tempfile.gettempdir())
    root=root.expanduser().resolve()/"ETABS_API"
    path=root/("run_"+uuid.uuid4().hex[:12])/"gravity.edb"
    if len(str(path))>=200:
        raise ValueError("ETABS gravity scratch EDB path too long ("+str(len(str(path)))+
                         "); set ETABS_GRAVITY_TEMP_ROOT to a short writable folder such as D:\\\\ETABS_API")
    path.parent.mkdir(parents=True,exist_ok=False)
    shutil.copy2(selected,path)
    if _file_hash(path)!=expected_sha:
        raise IOError("Isolated short-path EDB copy hash verification failed")
    log('ETABS_WORKING_COPY','Created isolated short-path ETABS EDB',
        original_edb=str(selected),working_copy=str(path),
        original_path_length=len(str(selected)),copy_path_length=len(str(path)),
        sha256=expected_sha,warning='Temporary working copy must be retained for native analysis logs')
    return path


def _collect_etabs_solver_logs(working_copy,output_dir,log):
    """Retain lightweight native ETABS log text for postmortem analysis."""
    if working_copy is None:return
    destination=Path(output_dir)/'ETABS_Native_Analysis_Logs'
    destination.mkdir(parents=True,exist_ok=True)
    files=[]
    for pattern in ("*.LOG","*.log","*.txt"):
        files.extend(Path(working_copy).parent.glob(pattern))
    for src in sorted(set(files)):
        try:
            if src.stat().st_size>50*1024*1024:
                log('ETABS_LOG_SKIP','Native log exceeds 50 MB; remains in scratch folder',
                    source=str(src),size=src.stat().st_size)
                continue
            dst=destination/src.name
            shutil.copy2(src,dst)
            log('ETABS_NATIVE_LOG','Saved native ETABS analysis log',
                source=str(src),destination=str(dst),bytes=dst.stat().st_size)
        except OSError as exc:
            log('ETABS_NATIVE_LOG_ERROR','Unable to copy ETABS analysis log',
                source=str(src),error=str(exc))


def connect_and_compare(export_dir,gravity_result_path,case='1. DL + LL',output_dir=None,allow_alternate_edb=False,launch_new_etabs=False,etabs_edb_path=None,etabs_exe_path=None,log_callback=None,run_if_missing=False):
    """Compare the original ETABS source EDB to the OpenSees gravity result.

    [REF components/validation/etabs_direct_api.py connect_and_extract] Audit
    selected results. When run_if_missing is enabled, analyze only an isolated
    EDB copy; never run or save the original source model.
    [REF CSI ETABS OAPI cAnalyze.RunAnalysis] Runs enabled analysis cases.
    """
    from OpenSees_Project_Inputs_V123 import connect_etabs
    from components.inputs.project_workbooks import _source_edb_path
    folder=Path(export_dir)
    gravity=Path(gravity_result_path)
    out=Path(output_dir or gravity.parent/'Gravity_ETABS_OpenSees_Direct')
    out.mkdir(parents=True,exist_ok=True)
    logfile=out/'ETABS_Gravity_Extraction.log'
    events=out/'ETABS_Gravity_Extraction_Events.jsonl'
    def report(stage,message,**fields):
        """Persist events even if ETABS raises before the comparison is exported."""
        record=dict(timestamp=datetime.now(timezone.utc).isoformat(),
                    stage=stage,message=str(message),**fields)
        with events.open('a',encoding='utf8') as stream:
            stream.write(json.dumps(record,default=str,allow_nan=False)+'\n')
        line=f"[{record['timestamp']}] [{stage}] {message}"
        if fields:line+=' | '+json.dumps(fields,default=str,ensure_ascii=False)
        with logfile.open('a',encoding='utf8') as stream:stream.write(line+'\n')
        if log_callback is not None:log_callback(line)
    # Retain separate .log and JSONL files for traceable API operations.
    logfile.write_text('',encoding='utf8')
    events.write_text('',encoding='utf8')
    report('START','Begin ETABS/OpenSees direct gravity comparison',
           case=case,launch_new_etabs=bool(launch_new_etabs),
           allow_alternate_edb=bool(allow_alternate_edb),
           run_if_missing=bool(run_if_missing),
           gravity_json=str(gravity),source_export_folder=str(folder))
    app=None;owned=False;working_copy=None;original_hash=None
    try:
        source=_source_edb_path(folder)
        if not source:raise ValueError('Export lacks source EDB identity; re-export rather than guessing')
        report('SOURCE_EDB','Read original EDB from OpenSees export',path=str(source))
        if not Path(source).is_file():
            raise FileNotFoundError('ETABS source EDB inaccessible: '+str(source))
        if not gravity.is_file():
            raise FileNotFoundError('OpenSees gravity JSON missing: '+str(gravity))
        if launch_new_etabs:
            selected=Path(etabs_edb_path).expanduser().resolve() if etabs_edb_path else Path(source).resolve()
            if not selected.is_file():
                raise FileNotFoundError('Selected gravity EDB missing: '+str(selected))
            if selected!=Path(source).resolve() and not allow_alternate_edb:
                raise ValueError('Different gravity-copy EDB requires explicit diagnostic approval')
            original_hash=_file_hash(selected)
            if run_if_missing:
                # ETABS RunAnalysis can write model/result sidecars; all such
                # writes are confined to this private working directory.
                working_copy=_short_etabs_working_copy(selected,original_hash,report)
                report('ETABS_WORKING_COPY','Analysis sidecars remain beside scratch EDB; native logs copied to evidence folder',
                       working_copy=str(working_copy),
                       path_length=len(str(working_copy)))
            opened_edb=working_copy or selected
            report('ETABS_LAUNCH','Launching private ETABS instance',
                   edb=str(opened_edb),
                   executable=str(etabs_exe_path or 'registered ETABS COM'))
            app=_new_etabs_instance(opened_edb,exe_path=etabs_exe_path)
            owned=True
            report('ETABS_OPEN','Private ETABS instance opened expected EDB',edb=str(opened_edb))
        else:
            report('ETABS_ATTACH','Connecting to already-open ETABS session')
            app=connect_etabs()
            report('ETABS_ATTACH','Connected; this ETABS instance will not be closed')
        if run_if_missing and not owned:
            raise ValueError('Automatic analysis requires a privately launched ETABS instance')
        try:
            data=extract_from_sap(app.SapModel,case,source_edb=source,
                                  allow_alternate_edb=allow_alternate_edb,log=report)
        except RuntimeError as missing:
            # Restrict retries to genuine missing-results errors; unrelated
            # CSI API errors must not trigger an expensive analysis run.
            if not run_if_missing or 'no usable BaseReact results' not in str(missing):
                raise
            if not owned or working_copy is None:
                raise RuntimeError('Refusing to analyze any EDB outside a private verified copy') from missing
            report('ETABS_ANALYZE','Missing gravity results; inspecting working-copy run flags',
                   source_status=str(missing))
            _enable_gravity_cases_on_copy(app.SapModel,report)
            # CSI examples save the model before running. Save is confined to
            # the SHA-verified isolated scratch model, NEVER the original.
            save_ret=app.SapModel.File.Save(str(working_copy))
            if save_ret not in (0,None):
                raise RuntimeError('ETABS File.Save returned '+str(save_ret)+
                                   ' for private gravity analysis scratch EDB')
            report('ETABS_SAVE','Saved private short-path working EDB before analysis',
                   path=str(working_copy),path_length=len(str(working_copy)))
            ret=app.SapModel.Analyze.RunAnalysis()
            if ret not in (0,None):
                raise RuntimeError('ETABS Analyze.RunAnalysis returned '+str(ret)+
                                   ' on isolated EDB: '+str(working_copy))
            try:
                post_status=_get_case_status(app.SapModel)
            except Exception as status_error:
                raise RuntimeError('Analysis returned success but case status cannot be verified: '+
                                   str(status_error)) from status_error
            report('ETABS_ANALYZE','Analysis call completed; checking solved-case status',
                   working_copy=str(working_copy),
                   dead_status=post_status.get('Dead'),
                   live_status=post_status.get('Live'))
            if post_status.get('Dead')!=4 or post_status.get('Live')!=4:
                raise RuntimeError('ETABS RunAnalysis returned 0, but Dead/Live are NOT FINISHED: '+
                                   str({k:post_status.get(k) for k in ('Dead','Live')})+
                                   '. Inspect the working copy ETABS analysis .LOG for warnings and failures.')
            # Running analysis may update the private EDB's saved state;
            # it is still the exact byte-verified source copy at creation.
            # Compare to the working EDB itself at this stage, while retaining
            # original source provenance separately for auditing.
            data=extract_from_sap(app.SapModel,case,
                                  source_edb=working_copy,
                                  allow_alternate_edb=allow_alternate_edb,log=report)
            data['source_model_edb']=str(Path(source).resolve())
            data['source_model_edb_sha256']=_file_hash(source)
            data['model_identity_status']=(
                'ALTERNATE_EDB_UNVERIFIED' if selected!=Path(source).resolve()
                else 'WORKING_COPY_ANALYZED_FROM_SOURCE_EDB')
            data['matched_edb_identity']=False
        if original_hash and _file_hash(selected)!=original_hash:
            raise RuntimeError('Original EDB hash changed unexpectedly during comparison; STOP and audit')
        if working_copy is not None:
            data['analysis_working_copy']=str(working_copy)
            data['original_source_edb_sha256_before']=original_hash
            data['original_source_edb_sha256_after']=_file_hash(selected)
            report('ETABS_PROVENANCE','Verified original EDB unchanged; comparison used isolated copy',
                   original_sha256=original_hash,copy=str(working_copy))
        # Extract native element/material quantity tables from the SAME active
        # ETABS model used for the direct base reaction. Preserve all returned
        # fields and a manifest; optional API failures must be visible.
        try:
            from components.validation.etabs_native_quantity_tables import (
                export_native_quantity_tables)
            previous_units=app.SapModel.GetPresentUnits()
            try:
                _out((app.SapModel.SetPresentUnits(UNITS_KN_M_C),),
                     0,"Set ETABS quantity display units")
                native_tables=export_native_quantity_tables(
                    app.SapModel,out/"ETABS_Native_Quantity_Tables",log=report)
            finally:
                _out((app.SapModel.SetPresentUnits(previous_units),),
                     0,"Restore native quantity display units")
            report("ETABS_NATIVE_QUANTITY_EXTRACTION",
                   "Captured source-model table inventory and available raw quantity tables",
                   count=native_tables["selected_table_count"],
                   directory=str(out/"ETABS_Native_Quantity_Tables"),
                   warning="Native table quantities require per-object alignment before correction")
        except Exception as quantity_exc:
            report("ETABS_NATIVE_QUANTITY_BLOCKED",
                   "Native quantity extraction failed; gravity reaction comparison continues",
                   error_type=type(quantity_exc).__name__,error=str(quantity_exc))
        # Opt-in: native solved EQX/EQY PDelta verification evidence on the
        # exact same ETABS model. Never auto-run seismic cases: the gravity
        # direct workflow otherwise enables/runs only Dead and Live.
        if os.environ.get("ETABS_EQ_PDELTA_EXPORT", "").strip() == "1":
            try:
                from components.validation.etabs_eq_pdelta_native_extract import (
                    export_eq_pdelta_native_evidence)
                eq_native=export_eq_pdelta_native_evidence(
                    app.SapModel,out/"ETABS_EQ_PDelta_Native",
                    log=report)
                report("ETABS_EQ_PDELTA_NATIVE",
                       "Collected available saved ETABS EQX/EQY PDelta cases",
                       case_names=eq_native["selected_eq_case_names"],
                       cases=len(eq_native["selected_eq_case_names"]),
                       note="Does not run missing earthquake cases or modify EDB")
            except Exception as eq_error:
                report("ETABS_EQ_PDELTA_NATIVE_BLOCKED",
                       "Earthquake native audit failed, gravity comparison unaffected",
                       error=type(eq_error).__name__+": "+str(eq_error))
        # Capture the separate OpenSees converted APPLIED nodal force ledger.
        # These values must NOT be equated with support reactions.
        try:
            from components.validation.gravity_node_comparison import export_opensees_applied_nodal_loads
            load_summary=export_opensees_applied_nodal_loads(
                folder/'OpenSees_Complete_Model_Data_V118.json',out)
            report('OPENSEES_NODAL_LOADS','Exported source-pattern equivalent nodal gravity forces',
                   patterns=load_summary['records_by_pattern'],
                   FZ_kN=load_summary['vertical_applied_kN_by_pattern'],
                   note='Do not treat applied nodal force as support reaction')
        except (FileNotFoundError,ValueError,KeyError,TypeError) as exc:
            report('OPENSEES_NODAL_LOADS_BLOCKED',
                   'Nodal source-force ledger missing or incompatible; support audit continues',
                   error=str(exc))
        result=json.loads(gravity.read_text(encoding='utf-8-sig'))
        report('OPENSEES_RESULT','Loaded OpenSees gravity results',
               profile=result.get('gravity_profile'),ok=result.get('ok'))
        comp=compare_existing(data,result)
        from components.validation.gravity_node_comparison import compare_support_nodes,write_node_comparison
        try:
            node_audit=compare_support_nodes(data,result,tolerance_m=0.01)
            topo_path=folder/"OpenSees_Element_Connectivity.json"
            topo=json.loads(topo_path.read_text(encoding="utf-8-sig")) if topo_path.is_file() else None
            write_node_comparison(out,node_audit,etabs=data,
                                  opensees=result,topology=topo)
            report("ALL_NODES_EXCEL","Exported every OpenSees gravity node, ETABS source ID mapping, ranked 76-support comparison",
                   workbook=str(out/"Gravity_Node_Reaction_Comparison.xlsx"),
                   all_node_csv=str(out/"Gravity_All_Model_Nodes.csv"),
                   mapping_count=len((topo or {}).get("node_map",[])),
                   caution="Unrestrained ETABS support reactions and displacements remain blank if not exported")
            comp['node_comparison']={
                k:v for k,v in node_audit.items()
                if k not in ('rows','top_discrepancies','diagnostic_hypotheses')}
            comp['top_node_discrepancies']=node_audit['top_discrepancies'][:10]
            report('NODE_COMPARISON','Compared coordinate-matched support reactions',
                   valid_matches=node_audit['valid_one_to_one_global_z_count'],
                   axes_unverified=node_audit['axis_unverified_count'],
                   ambiguous=node_audit['ambiguous_count'],
                   unmatched_etabs=node_audit['etabs_unmatched_count'],
                   unmatched_opensees=node_audit['opensees_unmatched_count'],
                   matched_sum_difference_kN=node_audit['matched_sum_difference_kN'],
                   largest_differences=node_audit['top_discrepancies'][:8],
                   note='ETABS local F3 is used only when point axes are verified default')
        except (ValueError,KeyError,TypeError) as exc:
            comp['node_comparison']=dict(status='BLOCKED_MISSING_OR_INCOMPATIBLE_EVIDENCE',
                                          reason=str(exc))
            report('NODE_COMPARISON_BLOCKED',
                   'Could not verify support-node comparison; global totals remain separate',
                   error=str(exc))
        report('DIRECT_COMPARISON','Compared ETABS global FZ and OpenSees support RZ',
               etabs_FZ_kN=comp['etabs_base_FZ_kN'],
               opensees_RZ_kN=comp['opensees_support_FZ_kN'],
               difference_kN=comp['difference_kN'],
               difference_percent=comp['percent_difference'],
               identity_status=comp['model_identity_status'])
        export_direct(out,data,comp)
        report('EXPORT','Saved gravity comparison evidence',
               output=str(out),json='etabs_gravity.json',
               note='Individual point reaction values remain in local axes')
        return comp,out
    except Exception as exc:
        report('FAILED','Direct ETABS gravity comparison failed',
               error_type=type(exc).__name__,error=str(exc),
               traceback=traceback.format_exc())
        raise
    finally:
        if owned:
            try:
                report('ETABS_CLOSE','Closing only privately launched ETABS instance, no save')
                _release_owned_instance(app)
                report('ETABS_CLOSE','Private ETABS instance closed without saving')
            except Exception as exc:
                report('ETABS_CLOSE_ERROR','Unable to verify private ETABS close',
                       error_type=type(exc).__name__,error=str(exc))
                raise
        if working_copy is not None:
            _collect_etabs_solver_logs(working_copy,out,report)
        report('END','ETABS direct gravity operation ended',
               log=str(logfile),events=str(events),
               scratch_edb=str(working_copy) if working_copy else None)
