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
    _wall_aw_profile, _continuous_wall_pier_diagnostic, analysis_output_folder,
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
    diagnostic=None
    if profile and not profile.get('uniform_footprint',False):
        # Use the very same base-to-roof height used to create the
        # first-storey wall profile, rather than re-inferring a different
        # datum from the assembled JSON.
        height=_positive(v.get('wall_aw_height_m'))
        if height is None:
            source_model=json.loads(model.read_text(encoding='utf-8-sig'))
            level_roof=max(float(g['master_xyz'][2])
                           for g in source_model['diaphragms'])
            z0=float(source_model.get('base_z_m',
                                     profile['rows'][0]['z_bottom_m']))
            height=level_roof-z0
        if not math.isfinite(height) or height<=0:
            raise ValueError('Invalid seismic height in source OpenSees model')
        diagnostic=_continuous_wall_pier_diagnostic(height,profile)
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
            # Only the continuous through-height projected material is shown
            # as a provisional diagnostic. A partial-height opening is NOT
            # interchangeable with a single NBC §5.1.2 effective wall pier.
            candidate=diagnostic['aw_candidate_m2'][axis] if diagnostic else None
            approved[axis]=candidate
            evidence[axis]={
                'status':('PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC'
                          if candidate is not None else
                          'NO_CONTINUOUS_PIER_IN_THIS_AXIS'),
                'code_accepted':False,
                'full_height_only':True,
                'continuous_pier_candidate_m2':candidate,
                'section_candidates_m2':[r['aw_'+axis.lower()+'_m2']
                                         for r in profile['rows']],
                'matching_workbook_candidate_m2':imported}
        elif imported is not None:
            approved[axis]=None
            evidence[axis]={'status':'WORKBOOK_ONLY_REVIEW_REQUIRED',
                            'matching_workbook_candidate_m2':imported}
        else:
            approved[axis]=None
            evidence[axis]={'status':'NO_SOURCE_VERIFIED_WALL_INDEX'}
    # Optional, manually reviewed connected-wall grouping based on original
    # first-storey source slices. This does NOT mutate the continuous-pier
    # diagnostic or override an EDB-matched original Excel calculation.
    from components.inputs.grouped_wall_aw import source_matched_grouping
    grouped=None
    grouping_error=None
    try:
        grouped=source_matched_grouping(
            folder, state, profile, v.get("wall_aw_height_m"),
            _source_edb_path(folder), _hash(model))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        grouping_error=str(exc)
    if grouped is not None:
        for axis in ('X','Y'):
            candidate=_positive(grouped['aw_candidate_m2'].get(axis))
            if candidate is not None:
                evidence[axis]['historical_ubc_seaoc_grouped_candidate_m2']=candidate
                evidence[axis]['historical_grouped_status']=grouped['status']
                evidence[axis]['code_accepted']=False
                # Source-matched explicit grouping is a more relevant NBC
                # area *candidate* for perforated walls than independently
                # weighted small piers, but never a code PASS.
                approved[axis]=candidate
                evidence[axis]['status']=grouped['status']
        data['notes'].append(
            'Source-matched grouped-wall Aw candidate uses minimum first-storey '
            'area and overall wall length (UBC/SEAOC precedent); engineering '
            'review REQUIRED, not equivalent to physical coupling verification.')
    if grouping_error:
        data['notes'].append('WALL_GROUPING_REVIEW_BLOCKED: ' + grouping_error)
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
        'continuous_pier_diagnostic':diagnostic,
        'grouped_wall_aw_review':grouped,
        'historical_ubc_seaoc_user_example':(
            __import__('components.inputs.grouped_wall_aw',
                fromlist=['wall_aw_example']).wall_aw_example()),
        'grouped_wall_aw_error':grouping_error,
        'opening_reduction_audit':(
            opening_reduction_audit(profile,height)
            if diagnostic is not None else None),
        'rayleigh_s':{axis:_positive(v.get('rayleigh_t'+axis.lower()))
                      for axis in ('X','Y')},
        'notes':data['notes'],
        'source_audit':data['audit']
    }
    return result


def _profile_intervals(profile, z, *, tolerance=1e-6):
    """Physical wall cross section at z, independent of element mesh splits."""
    matches=[r for r in profile.get('rows',[])
             if float(r['z_bottom_m'])-tolerance <= z <= float(r['z_top_m'])+tolerance]
    if len(matches)!=1:
        raise ValueError(f'Wall cross-section at z={z:g} belongs to {len(matches)} slices')
    grouped={}
    for seg in matches[0].get('segments',[]):
        key=(seg['axis'],round(float(seg['plane_m']),6),
             round(float(seg['thickness_m']),6))
        grouped.setdefault(key,[]).append(
            (float(seg['start_m']),float(seg['end_m'])))
    normalized={}
    for key,spans in grouped.items():
        merged=[]
        for a,b in sorted(spans):
            if merged and a <= merged[-1][1]+tolerance:
                merged[-1]=(merged[-1][0],max(merged[-1][1],b))
            else:merged.append((a,b))
        normalized[key]=merged
    return normalized


def compare_wall_profiles(opensees_profile, etabs_profile, *, tolerance_m=0.001):
    """Exact source-slice geometry comparison, not independent NBC acceptance.

    For every combined floor-slice boundary compare the unioned physical
    projected intervals on each (direction, wall plane, thickness). A mismatch
    in any X/Y pier or opening is a failure. The tolerance is a numerical
    geometry screening setting (1 mm default), NOT an NBC acceptance tolerance.
    """
    if not math.isfinite(tolerance_m) or tolerance_m<=0:
        raise ValueError('Geometry comparison tolerance must be positive')
    a=opensees_profile.get('rows',[]);b=etabs_profile.get('rows',[])
    if not a or not b:
        return dict(status='NO_COMMON_SOURCE_GEOMETRY',max_difference_m=None,
                    mismatches=[{'reason':'Missing elevation slices'}],checked_slices=0)
    z1=(float(a[0]['z_bottom_m']),float(a[-1]['z_top_m']))
    z2=(float(b[0]['z_bottom_m']),float(b[-1]['z_top_m']))
    if any(abs(x-y)>tolerance_m for x,y in zip(z1,z2)):
        return dict(status='MISMATCHED_STORY_ELEVATIONS',checked_slices=0,
                    max_difference_m=max(abs(x-y) for x,y in zip(z1,z2)),
                    mismatches=[{'open_sees':z1,'etabs':z2}])
    cuts=sorted(set(
        [z1[0],z1[1]]+
        [float(r['z_bottom_m']) for r in a+b]+
        [float(r['z_top_m']) for r in a+b]))
    issues=[];maxdiff=0.;checked=0
    for lower,upper in zip(cuts,cuts[1:]):
        if upper-lower<=1e-8:continue
        z=(lower+upper)/2
        left=_profile_intervals(opensees_profile,z)
        right=_profile_intervals(etabs_profile,z)
        checked+=1
        for key in sorted(set(left)|set(right)):
            spans_a=left.get(key,[]);spans_b=right.get(key,[])
            if len(spans_a)!=len(spans_b):
                issues.append({'z_mid_m':z,'axis':key[0],'plane_m':key[1],
                               'thickness_m':key[2],'open_sees':spans_a,
                               'etabs':spans_b,'reason':'Pier/opening interval count differs'})
                continue
            for la,lb in zip(spans_a,spans_b):
                diff=max(abs(la[0]-lb[0]),abs(la[1]-lb[1]))
                maxdiff=max(maxdiff,diff)
                if diff>tolerance_m:
                    issues.append({'z_mid_m':z,'axis':key[0],'plane_m':key[1],
                                   'thickness_m':key[2],'open_sees':la,
                                   'etabs':lb,'reason':'Pier boundary discrepancy'})
    return dict(status=('GEOMETRY_MATCHED_REVIEW_REQUIRED' if not issues else
                        'GEOMETRY_MISMATCH'),checked_slices=checked,
                tolerance_m=tolerance_m,max_difference_m=maxdiff,
                mismatches=issues[:200],total_mismatches=len(issues),
                disclaimer='Geometry matching does not establish code-effective '
                           'wall-pier grouping, coupling, materials or actual '
                           'ETABS analysis equivalence.')


def opening_reduction_audit(profile, height_m):
    """Compute gross plan projection and continuous pier contribution separately.

    Gross: union of *all* material projected at any first-storey elevation.
    Net: intersection of physical material available at *every* elevation.
    The difference is a geometry reduction in cross-section contribution;
    it is NOT the vertical opening area nor a blanket NBC deduction rule.
    """
    from components.inputs.project_workbooks import (
        _wall_aw_from_lines,_continuous_wall_pier_diagnostic)
    grouped={}
    for row in profile.get('rows',[]):
        for seg in row['segments']:
            key=(seg['axis'],float(seg['plane_m']),float(seg['thickness_m']))
            grouped.setdefault(key,[]).append(
                (float(seg['start_m']),float(seg['end_m'])))
    if not grouped:
        return {'status':'NO_GEOMETRY','axes':{}}
    gross,segments=_wall_aw_from_lines(height_m,grouped)
    continuous=_continuous_wall_pier_diagnostic(height_m,profile)
    net=continuous['aw_candidate_m2']
    axes={}
    for axis in ('X','Y'):
        g=float(gross[axis]);n=net.get(axis)
        # No full-height walls in a direction means net=0 for audit; it
        # remains a null candidate for a prospective NBC input.
        nvalue=float(n) if n is not None else 0.
        axes[axis]={'gross_projected_Aw_m2':g,
                    'continuous_pier_Aw_m2':n,
                    'excluded_noncontinuous_Aw_m2':max(0.,g-nvalue),
                    'excluded_fraction_of_gross':((g-nvalue)/g if g>0 else None),
                    'gross_segments':[v for v in segments if v['axis']==axis],
                    'continuous_segments':[v for v in continuous['continuous_segments']
                                           if v['axis']==axis]}
    return {'status':'OPENING_DEDUCTION_GEOMETRY_AUDIT',
            'axes':axes,'continuous_pier_status':continuous['status'],
            'disclaimer':'Gross-minus-through-height difference is only an '
                         'opening/discontinuity *geometric* exclusion; it is '
                         'not gross opening area and not an NBC-certified Aw.'}


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
        ('Continuous-pier diagnostic Aw (m²)',
         (report.get('continuous_pier_diagnostic') or {}).get('aw_candidate_m2',{}).get('X'),
         (report.get('continuous_pier_diagnostic') or {}).get('aw_candidate_m2',{}).get('Y')),
        ('Reviewed source-matched grouped Aw (m²)',
         (report.get('grouped_wall_aw_review') or {}).get('aw_candidate_m2',{}).get('X'),
         (report.get('grouped_wall_aw_review') or {}).get('aw_candidate_m2',{}).get('Y')),
        ('ILLUSTRATIVE example: 4 X doors + 3 solid Y walls (m²)',
         (report.get('historical_ubc_seaoc_user_example') or {}).get('X'),
         (report.get('historical_ubc_seaoc_user_example') or {}).get('Y')),
        ('Grouped wall status',
         (report.get('grouped_wall_aw_review') or {}).get('status',
                  'NO_SOURCE_MATCHED_GROUP_MANIFEST'),
         report.get('grouped_wall_aw_error') or ''),
        ('REFERENCE: UBC 1997 §1628/§1630.2.2 and SEAOC Vol I Example 19',
         'Historical net-minimum-area and gross-length analogy, NOT NBC acceptance'),
        ('REVIEW REQUIRED',
         'Verify original ULS/SLS EDB, first-storey door/spandrel grouping; '
         'continuous piers and illustrative values are not accepted NBC Aw.')
    ]
    for row in rows:ws.append(list(row))
    ws.append([])
    ws.append(['Wall slice z-bottom (m)','z-top (m)','Aw-X candidate (m²)','Aw-Y candidate (m²)','X piers','Y piers'])
    for p in (report.get('wall_aw_profile') or {}).get('rows',[]):
        ws.append([p['z_bottom_m'],p['z_top_m'],p['aw_x_m2'],p['aw_y_m2'],
                   p['x_segment_count'],p['y_segment_count']])
    ws.append([])
    ws.append(['OPENING REDUCTION: gross projected versus continuous-through-height'])
    for axis,items in (report.get('opening_reduction_audit') or {}).get('axes',{}).items():
        ws.append([axis,'Gross Aw (m²)',items['gross_projected_Aw_m2'],
                   'Continuous Aw (m²)',items['continuous_pier_Aw_m2'],
                   'Excluded (m²)',items['excluded_noncontinuous_Aw_m2']])
    ws.append([])
    ws.append(['ETABS ↔ OpenSees wall-pier geometry crosscheck'])
    cross=report.get('geometry_crosscheck') or {}
    ws.append(['Status',cross.get('status'),'Slices checked',cross.get('checked_slices'),
               'Tolerance (m)',cross.get('tolerance_m')])
    for mismatch in cross.get('mismatches',[])[:100]:
        ws.append(['Mismatch',str(mismatch)])
    ws.append([])
    ws.append(['CONTINUOUS THROUGH-HEIGHT PIER DIAGNOSTIC — NOT CODE ACCEPTED'])
    for seg in (report.get('continuous_pier_diagnostic') or {}).get('continuous_segments',[]):
        ws.append(['FULL HEIGHT',seg['axis'],seg['plane_m'],seg['start_m'],
                   seg['end_m'],seg['thickness_m'],seg['wall_length_m'],
                   seg['Aw_contribution_m2']])
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
            fallback=read_etabs_wall_profile(export_dir)
            report['etabs_fallback']=fallback
            if report.get('wall_aw_profile') is not None:
                audit=compare_wall_profiles(report['wall_aw_profile'],fallback['profile'])
                if fallback.get('errors') or fallback.get('skipped_nonorthogonal'):
                    audit['status']='INCOMPLETE_ETABS_EXTRACTION'
                    audit['reason']='ETABS skipped/failed area objects: '
                    audit['reason']+=str(fallback.get('errors',[])[:5])
                report['geometry_crosscheck']=audit
                # Source confidence is upgraded only for full matching
                # projected geometry, not for arbitrary comparable Aw numbers.
                for axis in ('X','Y'):
                    report['aw_evidence'][axis]['geometry_crosscheck']=audit['status']
                    report['aw_evidence'][axis]['code_accepted']=False
        except Exception as exc:
            report['etabs_fallback']={'status':'NOT_AVAILABLE','reason':str(exc)}
            report['geometry_crosscheck']={
                'status':'NOT_AVAILABLE','reason':str(exc)}
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
