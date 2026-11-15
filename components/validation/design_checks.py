"""Auditable combination coverage, serviceability and reviewed section checks.
No capacity is inferred from elastic stiffness or analysis convergence.
"""
from pathlib import Path
import csv,json,math,time,datetime,hashlib,itertools
SOURCE='https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf'
COMPONENTS=('N_kN','Vy_kN','Vz_kN','T_kNm','My_kNm','Mz_kNm')
REQUIRED=('axial_biaxial_interaction','shear','torsion','stability','detailing_capacity_design')

def read_rows(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def write_rows(path,rows):
    """Publish derived V135 CSV without partial replacement of prior evidence."""
    if not rows:return
    from components.inputs.output_contract import write_table
    columns=list(dict.fromkeys(k for r in rows for k in r))
    return write_table(path,rows,columns=columns)

def number(x):
    v=float(x)
    if not math.isfinite(v):raise ValueError('Non-finite numerical input')
    return v

def combinations(storage=False,nonparallel=False):
    lam=.6 if storage else .3;out=[]
    for state in ('ULS','SLS'):
        def add(name,factors,clause='3.6.1',note=''):
            out.append(dict(case=state+'_'+name,limit_state=state,factors=factors,clause='NBC 105:2025 '+clause,note=note))
        add('GRAVITY',{'DL':1.2,'LL':1.5})
        for action,factor in [('SNOW',1.2),('LIQUID',1.2),('EARTH',1.5)]:
            add(action,{'DL':1.2,'LL':.5,action:factor},note='Conditional action; confirm applicability, not silently omitted.')
        directions=[(1.,0.),(0.,1.)]
        if nonparallel:directions=[(1.,.3),(.3,1.)]
        for dx,dy in directions:
            for sx,sy in itertools.product((-1,1),repeat=2):
                if (not dx and sx<0) or (not dy and sy<0):continue
                label=f'EX{sx*dx:+g}_EY{sy*dy:+g}'
                for ecc in ('E0','EPLUS','EMINUS'):
                    for base,gravity in [('SEISMIC',{'DL':1.,'LL':lam}),('UPLIFT',{'DL':.9})]:
                        factors=dict(gravity)
                        if dx:factors[state+'_EX_'+ecc]=sx*dx
                        if dy:factors[state+'_EY_'+ecc]=sy*dy
                        add(base+'_'+label+'_'+ecc,factors,'3.6.2' if nonparallel else '3.6.1',
                            'E0 is a centered reference; eccentricity signs use separately solved actions. State-specific seismic action; gravity factors do not multiply ground motion.')
    return out

def combine_actions(rows,cases,model_hash):
    """Signed elastic action superposition only. Same end/station/axes required.
    A second-order/nonlinear total response must be solved as a combination,
    never linearly superposed here. CQC component maxima are not accepted.
    """
    basis={};issues=[]
    for r in rows:
        if r.get('model_sha256')!=model_hash:raise ValueError('Action model SHA256 does not match selected assembly')
        if r.get('response_kind')!='signed_first_order_linear_increment':
            raise ValueError('Combination basis must be signed_first_order_linear_increment; CQC envelopes and total/preloaded responses cannot be superposed.')
        key=(r['limit_state'],r['member'],r['station'],r['axes']);slot=(key,r['basis_case'])
        if slot in basis:raise ValueError('Duplicate action basis '+str(slot))
        if r['axes']!='local':raise ValueError('Only consistently oriented local member actions supported')
        basis[slot]=[number(r[k]) for k in COMPONENTS]
    keys=sorted(set(k for k,b in basis));out=[]
    for c in cases:
        for key in keys:
            if key[0]!=c['limit_state']:continue
            missing=[b for b in c['factors'] if (key,b) not in basis]
            if missing:
                issues.append(dict(case=c['case'],member=key[1],station=key[2],status='NOT EVALUATED',reason='Missing basis: '+', '.join(missing)));continue
            v=[sum(f*basis[key,b][i] for b,f in c['factors'].items()) for i in range(6)]
            if not all(math.isfinite(component) for component in v):
                issues.append(dict(case=c['case'],member=key[1],
                                   station=key[2],status='NOT EVALUATED',
                                   reason='Nonfinite combined action; finite input can overflow under superposition'))
                continue
            out.append(dict(case=c['case'],limit_state=key[0],member=key[1],station=key[2],axes=key[3],**dict(zip(COMPONENTS,v)),scope='FIRST ORDER ACTION COMBINATION ONLY; second-order and capacity checks separate'))
    return out,issues

def evaluate_checks(rows,model_hash,kind):
    out=[]
    for r in rows:
        q=dict(r);reason='';ratio=None
        try:
            if r.get('model_sha256')!=model_hash:raise ValueError('Model fingerprint mismatch')
            if r.get('reviewed','').lower()!='true':raise ValueError('Evidence not reviewed')
            if not r.get('source') or not r.get('clause') or not r.get('result_file'):raise ValueError('Missing source, clause or result file')
            if r.get('limit_state') not in ('ULS','SLS'):raise ValueError('Missing ULS/SLS context')
            if not r.get('unit'):raise ValueError('Missing compatible demand/capacity unit')
            if not Path(r['result_file']).is_file():raise ValueError('Result evidence file does not exist')
            if kind=='nonlinear' and (not r.get('performance_objective') or r.get('control_type') not in ('force','deformation') or not r.get('suite_statistic')):raise ValueError('Nonlinear check requires performance objective, force/deformation control and suite statistic')
            demand=abs(number(r['demand']));limit=number(r['limit'])
            if limit<=0:raise ValueError('Limit must be positive')
            if kind in ('section','nonlinear') and not r.get('concurrent_action_id'):raise ValueError('Missing concurrent action/station/time or approved envelope-method reference')
            ratio=demand/limit
            if not math.isfinite(ratio):
                ratio=None
                raise ValueError('Nonfinite demand/limit utilization; computed ratio overflow')
            status='PASS' if ratio<=1 else 'FAIL'
        except (ValueError,KeyError,TypeError) as e:status='NOT EVALUATED';reason=str(e)
        q.update(utilization=ratio,status=status,reason=reason,scope='Reviewed supplied criterion only; not whole-section certification' if kind=='section' else 'Reviewed nonlinear performance criterion; not whole-building acceptance' if kind=='nonlinear' else 'Reviewed project deflection criterion')
        out.append(q)
    return out

def scan_drift(folder):
    out=[];issues=[]
    for p in sorted(Path(folder).rglob('*.csv')):
        if 'Design_Checks_V135' in p.parts:continue
        if not (p.name.startswith('Drift_Check_') or p.name.startswith('Floor_Edge_Drift_')):continue
        try:
            if p.is_symlink():
                raise ValueError('Linked drift CSV source refused')
            parsed=[]
            for r in read_rows(p):
                state=r.get('limit_state','').upper()
                if state not in ('ULS','SLS'):raise ValueError('Drift result lacks limit_state')
                d=abs(number(r['design_drift_ratio']));limit=.025 if state=='ULS' else .006
                utilization=d/limit
                if not math.isfinite(utilization):
                    raise ValueError('Nonfinite CSV drift utilization from finite demand')
                parsed.append(dict(file=str(p),case=p.stem,limit_state=state,storey=r.get('story_number',r.get('story','')),axis=r.get('axis',''),edge=r.get('edge','master'),demand=d,limit=limit,utilization=utilization,status='PASS' if d<=limit else 'FAIL',clause='NBC 105:2025 5.5.3',scope='Saved-result check; verify selected current model and completed case. Not a section strength result.'))
            out.extend(parsed)
        except Exception as e:issues.append(dict(file=str(p),status='NOT EVALUATED',reason=str(e)))
    # MRSM stores story checks in result JSON, without separate drift CSV.
    for p in sorted(Path(folder).rglob('MRSM_Results_V132.json')):
        try:
            if p.is_symlink():
                raise ValueError('Linked MRSM JSON source refused')
            results=json.loads(p.read_text(encoding='utf-8-sig'))
            if not isinstance(results,dict):
                raise ValueError('MRSM case result must be a JSON object')
            parsed=[]
            for case,r in results.items():
                state=r['limit_state'];limit={'ULS':.025,'SLS':.006}[state]
                for s in r['stories']:
                    d=abs(number(s['design_drift_ratio']))
                    utilization=d/limit
                    if not math.isfinite(utilization):
                        raise ValueError('Nonfinite MRSM drift utilization from finite demand')
                    parsed.append(dict(file=str(p),case=case,limit_state=state,storey=s.get('story_number',''),axis=r.get('axis',''),edge='CQC design drift',demand=d,limit=limit,utilization=utilization,status='PASS' if d<=limit else 'FAIL',clause='NBC 105:2025 5.5.3',scope='Saved CQC drift; no force-only scale applied to displacement. Verify source model.'))
            out.extend(parsed)
        except Exception as e:issues.append(dict(file=str(p),status='NOT EVALUATED',reason=str(e)))
    return out,issues

def templates(folder):
    from components.inputs.output_contract import _refuse_linked_output_target
    folder=Path(folder)
    # Criteria templates are written into the canonical diagnostics tree,
    # never through a linked path into user-owned source workbooks.
    _refuse_linked_output_target(folder)
    folder.mkdir(parents=True,exist_ok=True)
    definitions={
      'Nonlinear_Performance_V135.csv':['performance_objective','control_type','suite_statistic','limit_state','case','member','check','demand','limit','unit','concurrent_action_id','model_sha256','reviewed','source','clause','result_file'],
      'Section_Criteria_V135.csv':['limit_state','case','member','check','demand','limit','unit','concurrent_action_id','model_sha256','reviewed','source','clause','result_file'],
      'Deflection_Criteria_V135.csv':['limit_state','case','member','check','demand','limit','unit','model_sha256','reviewed','source','clause','result_file'],
      'Action_Basis_V135.csv':['limit_state','basis_case','member','station','axes','response_kind','model_sha256',*COMPONENTS]}
    for name,fields in definitions.items():
        path=folder/name
        _refuse_linked_output_target(path)
        if not path.exists():
            # Exclusive creation avoids truncating a concurrent criteria edit.
            try:
                with path.open('x',encoding='utf-8-sig',newline='') as f:
                    csv.writer(f).writerow(fields)
            except FileExistsError:
                # Another writer created this input template: keep it intact.
                pass
    return folder

def design_check_locations(folder):
    """[REF docs/source/components/validation/design_checks.py.md]
    Return a canonical derived-report directory and the historical editable
    criteria directory. Do not move/delete original project criteria.
    """
    from components.inputs.output_layout import export_root_for
    root=export_root_for(folder)
    return (root/'09_SOFTWARE_DIAGNOSTICS'/'DESIGN_CHECKS_V135',
            root/'OpenSees_Analysis_Results'/'Design_Checks_V135')



def saved_drift_solver_status(response_file):
    """[REF docs/source/components/validation/design_checks.py.md]
    Read saved run completion without inferring status from filename or drift.

    An archived result with no run manifest is unverified, not zero response.
    """
    path=Path(response_file).expanduser().resolve()
    from components.inputs.output_contract import inspect_case_manifest
    for parent in (path.parent,*path.parents):
        manifest=parent/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
        if manifest.is_file() or manifest.is_symlink():
            # A scalar solver status and matching SHA in a forged/misfiled
            # manifest do NOT prove that this exact canonical run completed.
            review=inspect_case_manifest(parent)
            return (review["solver_status"] if review["valid"] else
                    "INVALID_RUN_MANIFEST")
        if parent.name.casefold() in ("03_esm","05_mrsm",
                "06_linear_time_history","07_nonlinear_time_history",
                "opensees_analysis_results"):
            break
    return "NO_RUN_COMPLETION_MANIFEST"


def discover_design_drift(folder):
    """[REF docs/source/components/validation/design_checks.py.md]
    Discover verified-on-disk report paths, not a structural PASS.

    Archived review snapshots and diagnostic copies must not count as new
    solver responses. Preserve status and path for individual case review.
    """
    from components.inputs.output_layout import result_roots
    found=[];issues=[];seen=set()
    for root in result_roots(folder,stages=('ESM','MRSM','LTHA','NLTHA')):
        if not root.is_dir():continue
        # scan_drift is a trusted input parser but scans deep directories;
        # only actual production roots are eligible.
        data,warnings=scan_drift(root)
        for item in data:
            p=Path(item['file']).resolve()
            if any(x.casefold() in {'review_snapshots','organized_results','zip_exports',
                    'seismic_review_packages','gravity_evidence_upload'} for x in p.parts):
                continue
            identity=(str(p),item['case'],item['limit_state'],
                      str(item['storey']),item['axis'],str(item['demand']))
            if identity not in seen:
                seen.add(identity);found.append(item)
        issues.extend(warnings)
    return found,issues


def run(folder,storage=False,nonparallel=False):
    from components.inputs.output_layout import export_root_for
    start=time.perf_counter();started=datetime.datetime.now().astimezone().isoformat()
    folder=export_root_for(folder)
    model=folder/'OpenSees_Complete_Model_Data_V118.json'
    if model.is_symlink():
        raise ValueError('Refusing linked authoritative serialized model source')
    if not model.is_file():raise ValueError('Select export folder containing OpenSees_Complete_Model_Data_V118.json')
    # Hash precisely the bytes parsed below; a file replaced between two
    # independent reads must not acquire a fingerprint for another payload.
    source_bytes=model.read_bytes()
    digest=hashlib.sha256(source_bytes).hexdigest()
    data=json.loads(source_bytes.decode('utf-8-sig'))
    if not isinstance(data,dict):
        raise ValueError('Serialized model must contain a JSON object')
    output,legacy=design_check_locations(folder)
    # Prefer user-edited criteria in the original legacy directory until
    # migrated explicitly. Blank canonical templates must not replace them.
    output=templates(output);cases=combinations(storage,nonparallel)
    drift,issues=discover_design_drift(folder)
    # A numerically low drift does not establish that the selected ETABS
    # export produced it. Reuse the V142 source fingerprint gate and ensure
    # legacy records without trusted identity cannot silently be marked PASS.
    from components.validation.saved_case_identity import identity_screen
    drift,source_issues=identity_screen(drift,expected_model_sha=digest)
    issues.extend(dict(check="Seismic drift source identity",
                       status=item["status"],
                       reason=item.get("reason",""),
                       file=item.get("file",""),
                       case=item.get("case",""),
                       manifest_model_sha256=item.get("manifest_model_sha256",""),
                       payload_model_sha256=item.get("payload_model_sha256",""),
                       result_model_sha256=item.get("result_model_sha256",""))
                  for item in source_issues)
    unknown_drift=0
    incomplete_drift=0
    for row in drift:
        row["run_completion_status"]=saved_drift_solver_status(row["file"])
        source_unknown=(row.get("source_identity_status")=="NOT_VERIFIED")
        run_incomplete=(row["run_completion_status"] not in (
            "COMPLETED_SOLVER_ONLY","VERIFIED_ETABS_EQUIVALENCE"))
        if source_unknown or run_incomplete:
            row["raw_limit_status"]=row.get("status")
            if row.get("status")=="PASS":
                row["status"]="NOT EVALUATED"
            row["scope"]=str(row.get("scope","")) + (
                " MISSING SOURCE IDENTITY OR RUN COMPLETION: this is a"
                " numerical drift-limit comparison, not verified acceptance.")
            unknown_drift+=int(source_unknown)
            incomplete_drift+=int(run_incomplete)
    if unknown_drift or incomplete_drift:
        issues.append(dict(check="Unverified saved drift source or completion",
                           status="NOT EVALUATED",
                           reason=(f"{unknown_drift} rows lack matching model SHA; "
                                   f"{incomplete_drift} rows have no completed run manifest."
                                   " Numeric drift-limit PASS withheld.")))
    input_sources={}
    def input_rows(filename):
        # Prefer actual edited canonical input; fall back to nonempty legacy
        # input, never discard/edit it or treat a header-only file as evidence.
        fresh=output/filename
        old=legacy/filename
        # Do not cross a linked criteria path even when a later fallback is
        # available; silent fallback could obscure conflicting user edits.
        from components.inputs.output_contract import _refuse_linked_output_target
        for candidate in (fresh,old):
            if candidate.is_symlink():
                raise ValueError('Refusing linked editable criteria input: '+str(candidate))
        fresh_rows=read_rows(fresh) if fresh.is_file() else []
        old_rows=read_rows(old) if old.is_file() else []
        if fresh_rows:
            input_sources[filename]=str(fresh.resolve())
            return fresh_rows
        if old_rows:
            input_sources[filename]=str(old.resolve())
            return old_rows
        input_sources[filename]=None
        return []
    criteria=evaluate_checks(input_rows('Section_Criteria_V135.csv'),digest,'section')
    nonlinear=evaluate_checks(input_rows('Nonlinear_Performance_V135.csv'),digest,'nonlinear')
    deflections=evaluate_checks(input_rows('Deflection_Criteria_V135.csv'),digest,'deflection')
    from components.validation.response_inventory import available_response_rows
    recorded_deflections,recorded_actions=available_response_rows(folder)
    deflections.extend(recorded_deflections)
    if not criteria:
        criteria=recorded_actions or [dict(status='CAPACITY REQUIRED',reason='No section capacities or recorded member actions found. Run analysis and supply actual reinforcement/design criteria.')]
    combined,missing=combine_actions(input_rows('Action_Basis_V135.csv'),cases,digest)
    inventory=[]
    for kind,items in [('FRAME',data.get('frames',[])),('AREA',data.get('shells',[]))]:
        for item in items:
            member=kind+':'+str(item['object'])
            if any(r['member']==member for r in inventory):continue
            found=[r for r in criteria if r.get('member')==member]
            failed=any(r['status']=='FAIL' for r in found)
            # Per-member summary never promotes a partial list to whole-section PASS.
            inventory.append(dict(member=member,category=item.get('category',''),section=item.get('properties',{}).get('section',item.get('properties',{}).get('property','')),status='FAIL' if failed else 'NOT EVALUATED',checks_supplied=len(found),required_checks=', '.join(REQUIRED),reason='A supplied criterion fails' if failed else 'Whole-section design requires all governing combinations, stations, interactions, stability and detailing evidence; individual checks listed separately.'))
    coverage=[]
    for c in cases:
        n=sum(r['case']==c['case'] for r in combined)
        coverage.append(dict(case=c['case'],limit_state=c['limit_state'],expression=' + '.join(f'{f:g} {b}' for b,f in c['factors'].items()),clause=c['clause'],action_rows=n,status='PARTIAL FIRST ORDER ACTIONS' if n else 'NOT EVALUATED',note=c['note']))
    for name,note in [('Vertical earthquake','NBC 3.6.3 / 4.3 applicability and signed vertical actions must be reviewed'),('Wind','Applicable wind code and combinations require separate project basis'),('Long-term vertical deflection','Creep, shrinkage, construction stages, finishes/partitions and support-chord reference required'),('Nonlinear component acceptance','Force-controlled brittle actions and deformation-controlled ductile actions require calibrated acceptance limits, suite coverage and performance objective; no automatic IO/LS/CP thresholds'),('Linear reinforcement demand','Requires approved RC material strengths, actual bar layout, cover, transverse steel, concurrent axial/biaxial actions and material-code design engine; illustrative fiber templates are insufficient'),('ULS stability and capacity design','Buckling, P-Delta, joints, anchorage, ductile detailing and capacity-design checks are separate from drift')]:
        issues.append(dict(check=name,status='NOT EVALUATED',reason=note))
    if not drift:issues.append(dict(check='Seismic drift',status='NOT EVALUATED',reason='No saved drift results found; run ULS and SLS analysis cases'))
    for state in ('ULS','SLS'):
        if not any(r['limit_state']==state for r in drift):issues.append(dict(check=state+' drift coverage',status='NOT EVALUATED',reason='No saved results in this limit state'))
    from components.validation.settings_audit import audit
    settings=audit(folder)
    issues.extend(dict(check=r['item'],status=r['status'],reason=r['basis']) for r in settings['rows'] if r['status'] not in ('CODE LIMIT REFERENCE','IMPLEMENTATION REFERENCE'))
    tables={'Combination coverage':coverage,'Seismic drift':drift,'Project deflection':deflections,'Section checks':criteria,'Nonlinear performance':nonlinear,'Section inventory':inventory,'Combined actions':combined,'Missing action basis':missing,'Open items':issues}
    for name,rows in tables.items():write_rows(output/(name.replace(' ','_')+'.csv'),rows)
    elapsed=time.perf_counter()-start
    report=dict(input_criteria_sources=input_sources,report_directory=str(output),
                drift_source_mismatch_excluded_count=len(source_issues),
                drift_source_unverified_row_count=unknown_drift,
                drift_run_completion_unverified_row_count=incomplete_drift,
                evidence_status='SOURCE_IDENTITIES_REQUIRE_REVIEW',
                model_sha256=digest,started=started,finished=datetime.datetime.now().astimezone().isoformat(),elapsed_s=elapsed,overall='INCOMPLETE' if not any(r.get('status')=='FAIL' for rows in tables.values() for r in rows) else 'FAIL / INCOMPLETE',sources=[SOURCE],tables=tables,scope='No whole-section PASS is inferred. Existing analysis outputs are checked without rerunning the solver. MRSM force envelopes and nonlinear totals are never superposed as linear increments.')
    from components.inputs.output_contract import atomic_json
    atomic_json(output/'Design_Check_Report_V135.json',report)
    from openpyxl import Workbook
    wb=Workbook();wb.remove(wb.active)
    for name,rows in tables.items():
        ws=wb.create_sheet(name[:31]);fields=list(dict.fromkeys(k for r in rows for k in r))
        if fields:
            ws.append(fields)
            for r in rows:ws.append([r.get(k) for k in fields])
            ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
            for col in ws.columns:ws.column_dimensions[col[0].column_letter].width=min(55,max(14,max(len(str(c.value or '')) for c in list(col)[:100])+2))
        else:ws.append(['NOT EVALUATED - no supplied/current results'])
    ws=wb.create_sheet('Basis and timing');ws.append(['Source',SOURCE]);ws.append(['Model SHA256',digest]);ws.append(['Started',started]);ws.append(['Elapsed before workbook (s)',elapsed]);ws.append(['Scope',report['scope']])
    from components.inputs.output_contract import style_workbook
    style_workbook(wb)
    # Do not truncate the last valid design-check workbook on a failed save.
    import os,tempfile
    from components.inputs.output_contract import _refuse_linked_output_target
    workbook_path=output/'Design_Check_Report_V135.xlsx'
    _refuse_linked_output_target(workbook_path)
    fd,staged_name=tempfile.mkstemp(prefix='.design_checks_',
                                   suffix='.xlsx',dir=output)
    os.close(fd)
    staged=Path(staged_name)
    try:
        wb.save(staged)
        _refuse_linked_output_target(workbook_path)
        os.replace(staged,workbook_path)
    finally:
        staged.unlink(missing_ok=True)
    elapsed=time.perf_counter()-start;report['elapsed_s']=elapsed
    report['finished']=datetime.datetime.now().astimezone().isoformat()
    from components.inputs.output_contract import atomic_json
    atomic_json(output/'Design_Check_Report_V135.json',report)
    # Declare exactly which derived CSVs belong to this refresh; empty
    # tables retain historical CSVs but are explicitly NOT CURRENT outputs.
    generated_index={}
    for table_name,table_rows in tables.items():
        filename=table_name.replace(' ','_')+'.csv'
        generated_index[table_name]={
            'csv':filename,
            'current_row_count':len(table_rows),
            'status':('CURRENT_DERIVED_TABLE' if table_rows else
                      'NO_CURRENT_ROWS_PRIOR_CSV_NOT_REPLACED'),
        }
    atomic_json(output/'Design_Check_Output_Index_V135.json',{
        'schema':'V135_DERIVED_REPORT_INDEX_V1',
        'model_sha256':digest,
        'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'tables':generated_index,
        'report_json':'Design_Check_Report_V135.json',
        'report_excel':'Design_Check_Report_V135.xlsx',
        'source_status':'DERIVED_SOFTWARE_REPORT_NOT_ENGINEERING_ACCEPTANCE',
        'note':('Rows absent in current run must not be inferred from any '
                'older same-name CSV retained for historical compatibility.'),
    })
    # Stage the display-only log before replacing it; do not truncate a
    # previously complete log because of an interrupted write.
    log_path=output/'Design_Check_V135.log'
    _refuse_linked_output_target(log_path)
    fd,log_temp=tempfile.mkstemp(prefix='.design_check_log_',
                                 suffix='.partial',dir=output)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as writer:
            writer.write(f"{started}\nModel SHA256: {digest}\n"
                         f"{report['overall']}\nElapsed including workbook: "
                         f"{elapsed:.3f} s\nFinished: {report['finished']}\n")
            writer.flush()
            os.fsync(writer.fileno())
        _refuse_linked_output_target(log_path)
        os.replace(log_temp,log_path)
    finally:
        Path(log_temp).unlink(missing_ok=True)
    return report,output

def launch(parent,folder):
    import tkinter as tk
    from tkinter import ttk,messagebox
    import os
    win=tk.Toplevel(parent);win.title('ULS / SLS combination, serviceability and section checks - V135');win.geometry('1250x780')
    path=tk.StringVar(value=str(folder));storage=tk.BooleanVar();np=tk.BooleanVar();summary=tk.StringVar(value='A section passes only after its governing strength, stability and detailing checks are completed. Drift PASS is separate.')
    ttk.Entry(win,textvariable=path).pack(fill='x',padx=8,pady=5)
    bar=ttk.Frame(win);bar.pack(fill='x');ttk.Checkbutton(bar,text='Storage occupancy (lambda 0.6; otherwise 0.3)',variable=storage).pack(side='left');ttk.Checkbutton(bar,text='Nonparallel lateral systems (100% + 30%)',variable=np).pack(side='left')
    ttk.Label(win,textvariable=summary,wraplength=1200).pack(fill='x',padx=8,pady=4)
    active_path=tk.StringVar(value='Runtime: '+str(Path(__file__).resolve()))
    ttk.Label(win,textvariable=active_path,wraplength=1150,foreground='#82501c').pack(fill='x',padx=8)
    book=ttk.Notebook(win);book.pack(fill='both',expand=True);state={'output':None}
    def refresh():
        try:
            report,output=run(path.get(),storage.get(),np.get());state['output']=output
            for tab in book.tabs():book.forget(tab)
            for name,rows in report['tables'].items():
                if not rows:rows=[dict(status='NOT EVALUATED',reason='No supplied criteria or matching saved results. Open report/input templates for required inputs.')]
                frame=ttk.Frame(book);book.add(frame,text=name);fields=list(dict.fromkeys(k for r in rows for k in r)) or ['status']
                tree=ttk.Treeview(frame,columns=fields,show='headings');xs=ttk.Scrollbar(frame,orient='horizontal',command=tree.xview);ys=ttk.Scrollbar(frame,command=tree.yview);tree.configure(xscrollcommand=xs.set,yscrollcommand=ys.set)
                tree.grid(row=0,column=0,sticky='nsew');ys.grid(row=0,column=1,sticky='ns');xs.grid(row=1,column=0,sticky='ew');frame.rowconfigure(0,weight=1);frame.columnconfigure(0,weight=1)
                for f in fields:tree.heading(f,text=f);tree.column(f,width=180,stretch=False)
                for r in rows:tree.insert('', 'end',values=[r.get(f,'') for f in fields])
            from components.ui.nbc105_settings_panel import design_check_output_diagnostic
            location=design_check_output_diagnostic(path.get())
            active_path.set("Running module: "+str(Path(__file__).resolve())
                            +" | NEW output: "+str(output)
                            +" | legacy audit: "+location["status"])
            summary.set(f"{report['overall']} | {len(report['tables']['Seismic drift'])} saved drift checks | {len(report['tables']['Section checks'])} section/action review rows | elapsed {report['elapsed_s']:.2f} s | Model SHA: {report['model_sha256'][:16]}. New reports are in 09_SOFTWARE_DIAGNOSTICS, NOT the legacy results folder.")
        except Exception as e:messagebox.showerror('Check inputs',str(e),parent=win)
    def open_output():
        from components.inputs.output_layout import export_root_for
        target=state['output'] or design_check_locations(export_root_for(path.get()))[0]
        if not Path(target).is_dir():
            messagebox.showwarning('No new V135 report','Run Refresh checks first to generate a current V135 report in 09_SOFTWARE_DIAGNOSTICS.',parent=win)
            return
        try:
            os.startfile(str(target))
        except (OSError,AttributeError) as exc:
            messagebox.showerror('Cannot open V135 output',str(exc)+'\nFolder: '+str(target),parent=win)
    ttk.Button(bar,text='Refresh checks + export Excel',command=refresh).pack(side='left',padx=8);ttk.Button(bar,text='Open report / input templates',command=open_output).pack(side='left')
    win.after(100,refresh);return win
