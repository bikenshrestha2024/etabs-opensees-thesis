"""Storey gravity ledger from exact assembled source nodal contributions."""
from pathlib import Path
import csv,json,math,hashlib,shutil,datetime,time
from OpenSees_Timing_V130 import timed_outputs

COLUMNS=['beam_self_weight_kN','column_self_weight_kN','brace_self_weight_kN','shear_wall_self_weight_kN','slab_self_weight_kN','other_self_weight_kN','floor_finish_kN','partition_kN','other_dead_kN','live_kN','storage_live_kN','roof_live_kN','unclassified_kN']

def classify(component,pattern,pattern_type=None):
    if component.startswith('self_weight_'):
        kind=component[len('self_weight_'):].replace(' ','_')
        return {'beam':'beam','column':'column','brace':'brace','shear_wall':'shear_wall','slab':'slab','floor':'slab'}.get(kind,'other')+'_self_weight_kN','DEAD'
    name=pattern.casefold().replace('_',' ').replace('-',' ')
    if 'finish' in name:return 'floor_finish_kN','DEAD'
    if 'partition' in name:return 'partition_kN','DEAD'
    if 'roof' in name and ('live' in name or pattern_type==11):return 'roof_live_kN','LIVE'
    if any(label in name.split() for label in ('storage','warehouse','stock')):return 'storage_live_kN','LIVE'
    if 'live' in name or pattern_type in (3,4,11):return 'live_kN','LIVE'
    if pattern_type in (1,2) or name in ('dead','dl','sdl','super dead','superdead'):return 'other_dead_kN','DEAD'
    return 'unclassified_kN','UNCLASSIFIED'

@timed_outputs('Storey gravity load classification and workbook','folder')
def export_storey_gravity(folder,data,config,pattern_types=None,*,generate_workbook=True):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);pattern_types=pattern_types or {}
    groups=sorted(data.get('diaphragms',[]),key=lambda g:g['master_xyz'][2]);nodes=data['nodes'];base=float(data['base_z_m'])
    rows={};details={}
    def row(key,z):
        if key not in rows:rows[key]=dict(storey=key,elevation_m=z,**{c:0. for c in COLUMNS},dead_total_kN=0.,live_total_kN=0.,unfactored_total_kN=0.,applied_dead_kN=0.,applied_live_kN=0.,applied_unclassified_kN=0.,applied_total_kN=0.)
        return rows[key]
    for item in data.get('load_provenance',[]):
        xyz=nodes.get(item['node'],nodes.get(str(item['node'])));z=float(xyz[2])
        g=next((g for g in groups if g['master_xyz'][2]>=z-1e-7),None)
        label='BASE' if z<=base+1e-7 else ('Storey '+str(g['storey_number']) if g else 'UNASSIGNED ABOVE FLOORS')
        level=base if label=='BASE' else (g['master_xyz'][2] if g else z)
        out=row(label,level);column,kind=classify(item.get('component','unknown'),item['pattern'],pattern_types.get(item['pattern']))
        value=item['downward_kN'];factor=float(config['gravity_factors'][item['pattern']]);applied=value*factor
        out[column]+=value;out['unfactored_total_kN']+=value;out['applied_total_kN']+=applied
        if kind=='DEAD':out['dead_total_kN']+=value;out['applied_dead_kN']+=applied
        elif kind=='LIVE':out['live_total_kN']+=value;out['applied_live_kN']+=applied
        else:out['applied_unclassified_kN']+=applied
        key=(label,item.get('source','unknown'),item.get('component','unknown'),item['pattern'],column,kind,factor)
        details[key]=details.get(key,0.)+value
    table=sorted(rows.values(),key=lambda r:r['elevation_m'])
    actual=sum(r['applied_total_kN'] for r in table);expected=float(data['total_downward_load_kN'])
    if not math.isclose(actual,expected,rel_tol=1e-10,abs_tol=1e-6):raise ValueError(f'Storey gravity ledger mismatch: {actual} vs {expected}')
    detail=[dict(storey=k[0],source=k[1],component=k[2],pattern=k[3],classification=k[4],load_class=k[5],gravity_factor=k[6],unfactored_kN=v,applied_kN=v*k[6]) for k,v in sorted(details.items())]
    note='Equivalent source nodal weights assigned to next diaphragm level above each node; base-node shares retained in BASE. Member weights spanning floors are apportioned by their consistent nodal forces. This is applied load by level, not storey axial force or cumulative storey reaction. Signed downward positive; upward negative. Unknown patterns remain unclassified.'
    # The configured model load and the full independent gravity benchmark
    # are distinct purposes. Do not change the actual model factors here.
    full_total=sum(r['unfactored_total_kN'] for r in table)
    report=dict(rows=table,details=detail,total_applied_kN=actual,assembled_total_kN=expected,
                reconciliation_error_kN=actual-expected,convention=note,
                load_purpose='CONFIGURED_MODEL_LOAD_LEDGER_NOT_SOLVER_RESULT',
                configured_gravity_factors=dict(config['gravity_factors']),
                full_unfactored_gravity_total_kN=full_total,
                configured_minus_full_gravity_kN=actual-full_total,
                beam_weight_policy=config.get('etabs_beam_weight_policy','UNKNOWN'),
                source_model_config_sha256=data.get('config_sha256'),
                solver_status='NOT_ASSESSED_BY_LOAD_LEDGER')
    (folder/'Gravity_Storey_Load_Breakdown_V131.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    for name,values in [('Gravity_Storey_Load_Breakdown_V131.csv',table),('Gravity_Source_Load_Detail_V131.csv',detail)]:
        if values:
            with (folder/name).open('w',newline='',encoding='utf-8-sig') as f:
                w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)
    xlsx=folder/'Gravity_Storey_Load_Breakdown_V131.xlsx'
    status=folder/'Gravity_Storey_Workbook_Status_V131.json'
    if not generate_workbook:
        # A previous run's Excel must never masquerade as the current
        # gravity case after rebuilding a source export in the same folder.
        archived=None
        if xlsx.exists():
            if xlsx.is_symlink() or not xlsx.is_file():
                raise ValueError('Previous storey workbook is not a regular source file')
            backup=folder/'09_SOFTWARE_DIAGNOSTICS'/'DEFERRED_GRAVITY_WORKBOOKS'
            backup.mkdir(parents=True,exist_ok=True)
            token=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            archived=backup/('Gravity_Storey_Load_Breakdown_V131_'+token+'.xlsx')
            shutil.move(str(xlsx),str(archived))
        status.write_text(json.dumps({
            'status':'DEFERRED_FORMULA_WORKBOOK_NOT_A_MODEL_FAILURE',
            'reason':'Expensive openpyxl mesh-cell/node formula expansion deliberately separated from mandatory analysis assembly.',
            'original_xlsx_archived_at':str(archived) if archived else None,
            'source_model_config_sha256':data.get('config_sha256'),
            'gravity_total_kN':expected,
            'storey_rows':len(table),
            'detail_rows':len(detail),
            'generation_command':'python -m components.gravity.storey_loads --workbook "'+str(folder)+'"',
            'csv_json_ledger_verified':True},indent=2),encoding='utf-8')
        print(f'[STOREY GRAVITY] {len(table)} levels | applied={actual:.6f} kN | '
              f'reconciliation={actual-expected:.6g} kN | '
              'FORMULA_XLSX=DEFERRED (CSV/JSON verified)',flush=True)
        return report
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill
    wb=Workbook();wb.remove(wb.active)
    for title,values in [('Storey totals',table),('Source detail',detail)]:
        ws=wb.create_sheet(title)
        if values:
            ws.append(list(values[0]))
            for item in values:ws.append(list(item.values()))
            ws.freeze_panes='B2';ws.auto_filter.ref=ws.dimensions
            for c in ws[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='1E3A5F')
            # Header-only sizing: ws.columns materializes every cell in a
            # large source detail sheet and added minutes to large exports.
            for header in ws[1]:
                ws.column_dimensions[header.column_letter].width=min(42,max(16,len(str(header.value))+2))
    readme=wb.create_sheet('Read me')
    readme.append([note])
    for key in ('load_purpose','configured_gravity_factors','full_unfactored_gravity_total_kN',
                'total_applied_kN','configured_minus_full_gravity_kN','beam_weight_policy',
                'source_model_config_sha256','solver_status'):
        value=report[key]
        readme.append([key,json.dumps(value) if isinstance(value,dict) else value])
    # A formula workbook may be hundreds of MB. Never save directly over a
    # previously valid artifact or hash the entire XLSX in RAM. The status
    # distinguishes a currently regenerating workbook from a verified one.
    if xlsx.is_symlink() or status.is_symlink():
        raise ValueError('Refusing linked gravity workbook/status destination')
    status.write_text(json.dumps({
        'status':'FORMULA_WORKBOOK_GENERATING',
        'source_model_config_sha256':data.get('config_sha256'),
        'gravity_total_kN':expected,
        'previous_workbook_retained_until_commit':xlsx.exists()
    },indent=2),encoding='utf-8')
    try:
        from OpenSees_Load_Path_V141 import add_formula_audit
        _formula_started=time.perf_counter()
        print('[OPTIONAL EXCEL START] Mesh cell/node formula sheets',flush=True)
        add_formula_audit(wb,folder,data,config)
        print(f'[OPTIONAL EXCEL DONE] Formula construction: '
              f'{time.perf_counter()-_formula_started:.3f}s',flush=True)
        from components.gravity.workbook_publishing import publish_workbook
        _save_started=time.perf_counter()
        print('[OPTIONAL EXCEL START] Atomic XLSX serialization and SHA256',flush=True)
        digest=publish_workbook(wb,xlsx)
        print(f'[OPTIONAL EXCEL DONE] Atomic XLSX serialization and SHA256: '
              f'{time.perf_counter()-_save_started:.3f}s',flush=True)
        status.write_text(json.dumps({
            'status':'FORMULA_WORKBOOK_READY',
            'source_model_config_sha256':data.get('config_sha256'),
            'gravity_total_kN':expected,
            'workbook_sha256':digest,
            'source_detail_rows':len(detail)},indent=2),encoding='utf-8')
    except Exception as exc:
        status.write_text(json.dumps({
            'status':'FORMULA_WORKBOOK_EXPORT_FAILED',
            'source_model_config_sha256':data.get('config_sha256'),
            'gravity_total_kN':expected,
            'error_type':type(exc).__name__,
            'previous_workbook_preserved':xlsx.exists()
        },indent=2),encoding='utf-8')
        raise
    print(f'[STOREY GRAVITY] {len(table)} levels | applied={actual:.6f} kN | reconciliation={actual-expected:.6g} kN | FORMULA_XLSX=READY',flush=True)
    return report


def main(argv=None):
    """[REF docs/source/components/gravity/storey_loads.py.md] Build Excel without ETABS."""
    import argparse
    parser=argparse.ArgumentParser(description='Generate optional mesh-level storey gravity Excel from a finished source export')
    parser.add_argument('--workbook',action='store_true',required=True)
    parser.add_argument('export_folder')
    args=parser.parse_args(argv)
    folder=Path(args.export_folder).expanduser().resolve()
    report_path=folder/'OpenSees_Complete_Export_Report_V118.json'
    model_path=folder/'OpenSees_Complete_Model_Data_V118.json'
    config_path=folder/'OpenSees_Complete_Model_Config_V118.json'
    if not all(path.is_file() and not path.is_symlink()
               for path in (report_path,model_path,config_path)):
        raise ValueError('Completed source report, assembled model and config required')
    report=json.loads(report_path.read_text(encoding='utf-8-sig'))
    if report.get('assembly_errors') or report.get('elastic_assembled') is not True:
        raise ValueError('Source assembled export is incomplete or has assembly errors')
    data=json.loads(model_path.read_text(encoding='utf-8-sig'))
    cfg=json.loads(config_path.read_text(encoding='utf-8-sig'))
    if data.get('config_sha256')!=hashlib.sha256(config_path.read_bytes()).hexdigest():
        raise ValueError('Config changed since model assembly; refuse stale mesh workbook')
    if not (folder/'OpenSees_Load_Conversion_Audit.json').is_file():
        raise ValueError('Missing original ETABS load audit')
    metadata_path=folder/'OpenSees_Source_Model_Metadata_V118.json'
    metadata=json.loads(metadata_path.read_text(encoding='utf-8-sig')) if metadata_path.is_file() else {}
    result=export_storey_gravity(folder,data,cfg,
                                pattern_types=metadata.get('pattern_types',{}),
                                generate_workbook=True)
    print(json.dumps({
        'status':'FORMULA_WORKBOOK_READY',
        'gravity_total_kN':result['total_applied_kN'],
        'workbook':str(folder/'Gravity_Storey_Load_Breakdown_V131.xlsx')},
        indent=2))


if __name__=='__main__':
    main()
