"""Read-only OpenSees-first NBC 105 project input synchronization.

Source priority:
1. Current exported OpenSees model, first-storey shell geometry and hashed
   source-matched Rayleigh results.
2. Explicitly verified source-matched workbook inputs (independent evidence).
3. Optional read-only, currently open ETABS OAPI wall extraction.

This NEVER changes original .EDB or response-spectrum scaling and NEVER
promotes a wall with nonuniform height slices to an adopted NBC Aw.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from components.inputs.project_workbooks import (
    import_project_inputs, require_source_state, _source_edb_path,
    _wall_aw_profile, analysis_output_folder,
)

def _hash(path):
    p=Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def _positive(value):
    try:
        value=float(value)
        return value if math.isfinite(value) and value>0 else None
    except (TypeError,ValueError,OverflowError):
        return None


def _source_snapshot(export_dir,state):
    folder=Path(export_dir).resolve()
    state=str(state).upper().strip()
    if state not in ('ULS','SLS'):
        raise ValueError('Select one source state: Ultimate→ULS or Service→SLS.')
    require_source_state(folder,state)
    model=folder/'OpenSees_Complete_Model_Data_V118.json'
    ledger=folder/'NBC105_ESM_Story_Weights_Assembled_V118.csv'
    if not model.is_file() or not ledger.is_file():
        raise FileNotFoundError('Current assembled OpenSees model and story-weight ledger required.')
    data=import_project_inputs(Path(__file__).resolve().parents[2],folder,state)
    v=data['values']
    profile=v.get('wall_aw_profile')
    approved={}
    evidence={}
    for axis in ('X','Y'):
        key='aw'+axis.lower()
        geometric=_positive(v.get('geometry_aw_'+axis.lower()))
        workbook=_positive(v.get('workbook_'+key))
        imported=_positive(v.get(key))
        if geometric is not None and (not profile or profile.get('uniform_footprint')):
            if imported is not None and not math.isclose(imported,geometric,rel_tol=1e-6,abs_tol=1e-9):
                approved[axis]=None
                evidence[axis]={'status':'CONFLICT_GEOMETRY_VS_WORKBOOK',
                    'open_sees_candidate_m2':geometric,'matching_workbook_candidate_m2':imported}
            else:
                approved[axis]=geometric
                evidence[axis]={'status':'OPEN_SEES_GEOMETRY_CANDIDATE_REVIEW_REQUIRED',
                    'open_sees_candidate_m2':geometric}
        elif profile and not profile.get('uniform_footprint',False):
            # Different first-storey horizontal sections CANNOT be merged into
            # one validated NBC wall area. Show ALL slice candidates to reviewer.
            approved[axis]=None
            evidence[axis]={
                'status':'NONUNIFORM_WALL_OPENING_REVIEW_REQUIRED',
                'section_candidates_m2':[r['aw_'+axis.lower()+'_m2'] for r in profile['rows']],
                'matching_workbook_candidate_m2':imported}
        elif imported is not None:
            approved[axis]=None
            evidence[axis]={'status':'WORKBOOK_ONLY_REVIEW_REQUIRED',
                            'matching_workbook_candidate_m2':imported}
        else:
            approved[axis]=None
            evidence[axis]={'status':'NO_SOURCE_VERIFIED_WALL_INDEX'}
    roof_height=None
    stories=None
    try:
        with ledger.open(newline='',encoding='utf-8-sig') as handle:
            rows=list(csv.DictReader(handle))
        roof_height=max(float(r['height_m']) for r in rows)
        stories=len(rows)
    except (OSError,KeyError,ValueError,TypeError) as exc:
        data['notes'].append('Story ledger could not establish H/stories: '+str(exc))
    result={
        'workflow':'OPEN_SEES_FIRST_NBC105_INPUT_SYNC',
        'classification':'RESEARCH_INPUT_AUDIT_NOT_NBC_ACCEPTANCE',
        'limit_state':state,
        'source_edb':_source_edb_path(folder),
        'assembled_model_sha256':_hash(model),
        'story_weights_sha256':_hash(ledger),
        'source_export_directory':str(folder),
        'story_count':stories,'seismic_height_m':roof_height,
        'source_parameters':{k:v.get(k) for k in
            ('soil','Z','I','rmu','omegau','omegas','period_factor')},
        'aw_candidate_m2':approved,
        'aw_evidence':evidence,
        'wall_aw_profile':profile,
        'rayleigh_s':{axis:_positive(v.get('rayleigh_t'+axis.lower()))
                      for axis in ('X','Y')},
        'notes':data['notes'],
        'source_audit':data['audit']
    }
    return result


def _etabs_numeric_triplet(response,expected=3):
    if not isinstance(response,(list,tuple)):
        raise ValueError('ETABS returned unexpected coordinate response')
    # In the standard COM tuple the first three values are X/Y/Z and the
    # final field is a return code. Never mistake the trailing 0 for Z.
    if len(response)<expected:
        raise ValueError('ETABS returned too few coordinates')
    values=[float(x) for x in response[:expected]]
    if not all(math.isfinite(v) for v in values):
        raise ValueError('ETABS returned nonfinite coordinates')
    return values


def read_etabs_wall_profile(export_dir, *, sap=None):
    """Optional direct ETABS read-only cross-check. No OpenFile/Save/RunAnalysis.

    Connect ONLY to the existing current instance; fail if the displayed
    EDB does not match the original export source. ETABS is not required for
    the primary OpenSees sync. A height-varying footprint still blocks Aw.
    """
    folder=Path(export_dir).resolve()
    expected=_source_edb_path(folder)
    if not expected:
        raise ValueError('Missing original EDB reference in current OpenSees export')
    if sap is None:
        import comtypes.client
        try:
            helper=comtypes.client.CreateObject('ETABSv1.Helper')
            sap=helper.GetObject('CSI.ETABS.API.ETABSObject').SapModel
        except Exception:
            sap=comtypes.client.GetActiveObject('CSI.ETABS.API.ETABSObject').SapModel
    filename=sap.GetModelFilename()
    if isinstance(filename,(list,tuple)):filename=filename[0]
    if not filename or str(Path(str(filename)).resolve()).casefold()!=str(Path(expected).resolve()).casefold():
        raise ValueError('ETABS active EDB differs from OpenSees export source; no fallback imported. '
                         f'Active={filename!r}, expected={expected!r}')
    try:original_units=sap.GetPresentUnits()
    except Exception:original_units=None
    if isinstance(original_units,(list,tuple)):original_units=original_units[0]
    patches=[];errors=[];skipped=0
    try:
        ret=sap.SetPresentUnits(6)  # kN-m-C; restore in finally
        if isinstance(ret,int) and ret!=0:raise RuntimeError('Cannot set ETABS kN-m-C read units')
        names=sap.AreaObj.GetNameList()
        names=next((part for part in names if isinstance(part,(list,tuple))
                    and part and all(isinstance(v,str) for v in part)),[])
        for name in names:
            try:
                prop=sap.AreaObj.GetProperty(name)
                prop=next((v for v in prop if isinstance(v,str) and v.strip()),'')
                if not prop:continue
                wall=sap.PropArea.GetWall(prop)
                if len(wall)<4 or not isinstance(wall[3],(float,int)):continue
                thickness=float(wall[3])
                if not .001<thickness<10:continue
                pnames=sap.AreaObj.GetPoints(name)
                pnames=next((v for v in pnames if isinstance(v,(tuple,list))
                            and len(v)>=3 and all(isinstance(p,str) for p in v)),[])
                if len(pnames)<3:continue
                xyz=[_etabs_numeric_triplet(sap.PointObj.GetCoordCartesian(p)) for p in pnames]
                xx=[v[0] for v in xyz];yy=[v[1] for v in xyz];zz=[v[2] for v in xyz]
                dx=max(xx)-min(xx);dy=max(yy)-min(yy)
                if dx>1e-6 and dy<1e-6:axis='X';plane=round(yy[0],6);start=min(xx);end=max(xx)
                elif dy>1e-6 and dx<1e-6:axis='Y';plane=round(xx[0],6);start=min(yy);end=max(yy)
                else:
                    skipped+=1;continue
                patches.append((axis,plane,thickness,start,end,min(zz),max(zz)))
            except Exception as exc:
                errors.append(f'ETABS area {name}: {exc}')
        if not patches:raise ValueError('No axis-aligned ETABS wall panels available')
        model=json.loads((folder/'OpenSees_Complete_Model_Data_V118.json').read_text(encoding='utf-8-sig'))
        base=float(model.get('base_z_m',min(p[5] for p in patches)))
        levels=sorted(float(g['master_xyz'][2]) for g in model.get('diaphragms',[])
                      if float(g['master_xyz'][2])>base+1e-6)
        if not levels:raise ValueError('No OpenSees first-storey diaphragm elevation')
        first=levels[0]
        H=max(levels)-base
        clipped=[p for p in patches if p[5]>=base-1e-6 and p[6]<=first+1e-6]
        result=_wall_aw_profile(H,base,first,clipped)
        return {'source':'READ_ONLY_ETABS_OAPI','source_edb':expected,
                'source_edb_sha256':_hash(expected),
                'profile':result,'skipped_nonorthogonal':skipped,
                'errors':errors[:100], 'status':('UNIFORM_CANDIDATE_REVIEW_REQUIRED'
                  if result['uniform_footprint'] else 'NONUNIFORM_OPENINGS_REVIEW_REQUIRED')}
    finally:
        if isinstance(original_units,int) and original_units>0:
            try:sap.SetPresentUnits(original_units)
            except Exception:pass


def export_sync_report(report, output_dir, template=None):
    """Write local JSON + a NEW Excel copy; original source never overwritten."""
    from openpyxl import Workbook,load_workbook
    from openpyxl.styles import Font,PatternFill,Alignment
    output=Path(output_dir)
    output.mkdir(parents=True,exist_ok=True)
    json_path=output/'NBC105_OpenSees_Input_Sync.json'
    excel_path=output/'NBC105_OpenSees_Input_Sync.xlsx'
    if json_path.exists() or excel_path.exists():
        raise FileExistsError('Sync evidence exists; choose a new output folder to retain provenance')
    wb=load_workbook(template) if template else Workbook()
    if template and Path(template).resolve()==excel_path.resolve():
        raise ValueError('Input template and output paths must differ')
    if not template:wb.active.title='Workbook Notes'
    name='OpenSees Source Sync'
    if name in wb.sheetnames:raise ValueError('Template already contains OpenSees sync; do not overwrite')
    ws=wb.create_sheet(name,0)
    rows=[
        ('OPENSees-FIRST NBC 105 INPUT SYNCHRONIZATION','SOURCE EVIDENCE ONLY'),
        ('Limit state',report['limit_state']),
        ('Source EDB',report['source_edb']),
        ('Model SHA256',report['assembled_model_sha256']),
        ('Story weight SHA256',report['story_weights_sha256']),
        ('Storeys',report['story_count']),
        ('Seismic H (m)',report['seismic_height_m']),
        ('Directional wall index','X','Y'),
        ('Candidate Aw (m²)',report['aw_candidate_m2']['X'],report['aw_candidate_m2']['Y']),
        ('Evidence status',report['aw_evidence']['X']['status'],report['aw_evidence']['Y']['status']),
        ('Rayleigh period (s)',report['rayleigh_s']['X'],report['rayleigh_s']['Y']),
        ('REVIEW REQUIRED','Do not use a nonuniform wall opening slice as adopted NBC Aw.')
    ]
    for row in rows:ws.append(list(row))
    ws.append([])
    ws.append(['Wall slice z-bottom (m)','z-top (m)','Aw-X candidate (m²)','Aw-Y candidate (m²)','X piers','Y piers'])
    for p in (report.get('wall_aw_profile') or {}).get('rows',[]):
        ws.append([p['z_bottom_m'],p['z_top_m'],p['aw_x_m2'],p['aw_y_m2'],
                   p['x_segment_count'],p['y_segment_count']])
    ws.append([])
    ws.append(['Axis','Plane (m)','Start (m)','End (m)','Thickness (m)','Length (m)','Aw contribution (m²)','z-bottom','z-top'])
    for p in (report.get('wall_aw_profile') or {}).get('rows',[]):
        for seg in p['segments']:
            ws.append([seg['axis'],seg['plane_m'],seg['start_m'],seg['end_m'],
                       seg['thickness_m'],seg['wall_length_m'],seg['Aw_contribution_m2'],
                       p['z_bottom_m'],p['z_top_m']])
    notes=wb.create_sheet('Source Review Notes')
    for line in report['notes']:notes.append([str(line)])
    for col,width in [('A',37),('B',55),('C',32),('D',20),('E',20),('F',20),('G',24)]:
        ws.column_dimensions[col].width=width
    ws.freeze_panes='B8'
    for rownum in (1,8,14):
        for cell in ws[rownum]:
            cell.fill=PatternFill('solid',fgColor='17365D')
            cell.font=Font(color='FFFFFF',bold=True)
            cell.alignment=Alignment(wrap_text=True)
    ws.sheet_view.showGridLines=False
    notes.column_dimensions['A'].width=115
    notes.sheet_view.showGridLines=False
    # Existing Calculator formulas and ETABS result tables are intentionally
    # preserved without replacement; the new sheet carries candidates.
    wb.save(excel_path)
    json_path.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    return json_path,excel_path


def synchronize(export_dir,state='ULS',template=None,output_dir=None,etabs_fallback=False):
    report=_source_snapshot(export_dir,state)
    if etabs_fallback:
        try:
            report['etabs_fallback']=read_etabs_wall_profile(export_dir)
        except Exception as exc:
            report['etabs_fallback']={'status':'NOT_AVAILABLE','reason':str(exc)}
    if output_dir is None:
        output_dir=analysis_output_folder(export_dir,state)/'NBC105_Input_Sync'
    paths=export_sync_report(report,output_dir,template=template)
    return report,paths


def main(argv=None):
    import argparse
    p=argparse.ArgumentParser(description='OpenSees-first NBC input audit; optional read-only ETABS fallback')
    p.add_argument('--export',required=True,help='Current ETABS-to-OpenSees export directory')
    p.add_argument('--state',choices=['ULS','SLS'],default='ULS')
    p.add_argument('--template',help='Optional source NBC calculator .xlsx; preserved in new output copy')
    p.add_argument('--output',help='Fresh local audit output folder')
    p.add_argument('--etabs-fallback',action='store_true',help='Attach to existing matching EDB read-only')
    args=p.parse_args(argv)
    report,paths=synchronize(args.export,args.state,args.template,args.output,args.etabs_fallback)
    print(json.dumps({'state':report['limit_state'],'aw_evidence':report['aw_evidence'],
        'rayleigh_s':report['rayleigh_s'],'files':list(map(str,paths)),
        'classification':report['classification']},indent=2))


if __name__=='__main__':
    main()
