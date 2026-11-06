"""Explicit Excel → GUI mapping. Workbook formulas are not evaluated by openpyxl.

Imported data remain attributed project inputs; no import certifies code
compliance or replaces the independent ETABS/OpenSees reconciliation.
"""

__release__ = '134'
from pathlib import Path
import json
import math
import re

CALCULATOR='NBC105_2025_Seismic_Calculator_ETABS_Direct Interaction - Copy.xlsx'
SCALING='ULTIMATE LOAD  - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS_NBC105_RS_Scaling.xlsx'


SERVICE_SCALING='SERVICE LOAD  - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS_NBC105_RS_Scaling_2.xlsx'

def _source_edb_path(export_dir):
    folder=Path(export_dir)
    for name in ('OpenSees_Element_Connectivity.json','OpenSees_Section_Assignment_Audit.json'):
        path=folder/name
        if path.is_file():
            value=json.loads(path.read_text(encoding='utf-8-sig')).get('source_edb')
            if value:return str(value)
    return ''


def _portable_source_stem(path):
    """Interpret ETABS .EDB filenames consistently on Windows and Linux CI.

    A Windows source path stored inside a JSON export can otherwise be
    interpreted as one literal filename on Posix, corrupting the ESM
    result-folder name and source-model identity.
    """
    normalized=str(path).replace('\\','/').rstrip('/')
    return Path(normalized).stem


def _model_floor(export_dir,source_edb=''):
    for value in (_portable_source_stem(source_edb),Path(export_dir).name):
        match=re.search(r'(?i)(?:^|[-_\s])(\d{1,2})(?=[-_\s]+(?:BELT\s+TRUSS|OUTRIGGER))',value)
        if match:return match.group(1)
    return ''


def source_limit_state(export_dir):
    """Infer a single model's ULS/SLS identity from its ETABS source filename.

    Returns (state, evidence), with state 'ULS', 'SLS', or None. It does
    not infer stiffness from a successful gravity analysis. Ambiguous and
    unlabelled EDBs require explicit user review rather than silently using
    a case from the wrong stiffness model.
    """
    path=_source_edb_path(export_dir)
    if not path:
        return None,'No source_edb in the ETABS export manifests'
    stem=_portable_source_stem(path).casefold()
    uls=bool(re.search(r'(?<![a-z])(ultimate|uls)(?![a-z])',stem))
    sls=bool(re.search(r'(?<![a-z])(service|sls)(?![a-z])',stem))
    if uls and sls:
        return None,'Ambiguous EDB state contains both ULS/Ultimate and SLS/Service: '+path
    if uls:return 'ULS','Source EDB is labelled Ultimate/ULS: '+path
    if sls:return 'SLS','Source EDB is labelled Service/SLS: '+path
    return None,'Source EDB does not identify Ultimate or Service: '+path


def require_source_state(export_dir,selected_state):
    """Prevent accidental cross-stiffness apples-to-oranges analysis."""
    source,note=source_limit_state(export_dir)
    selected=str(selected_state).strip().upper()
    if selected not in ('ULS','SLS'):
        raise ValueError('Select one limit state (ULS or SLS) for a source-matched comparison.')
    if source and selected!=source:
        raise ValueError(f'Selected {selected} conflicts with the source model {source}. '+note)
    return note


def analysis_output_folder(export_dir,limit_state='ULS'):
    """Return a separate, source-identifiable result folder inside the shared results root."""
    folder=Path(export_dir)
    source_edb=_source_edb_path(folder)
    stem=_portable_source_stem(source_edb) if source_edb else folder.name
    floor=_model_floor(folder,source_edb)
    state=str(limit_state).strip().upper()
    state='ULS_SLS' if state in ('BOTH','ULS/SLS','ULS_SLS') else state
    if state not in ('ULS','SLS','ULS_SLS'):raise ValueError('limit_state must be ULS, SLS, or Both')
    slug=re.sub(r'[^A-Za-z0-9]+','_',stem).strip('_')[:72].rstrip('_') or 'ETABS_Model'
    floor_label='Floor_'+floor if floor else 'Floor_Unspecified'
    return folder/'OpenSees_Analysis_Results'/f'{state}_{floor_label}_{slug}'


def _wall_aw_from_lines(height_m, lines):
    height=float(height_m)
    if not math.isfinite(height) or height<=0:raise ValueError('Seismic height must be finite and positive.')
    aw={'X':0.,'Y':0.};segments=[]
    for (axis,plane,thickness),intervals in lines.items():
        t=float(thickness)
        if axis not in aw:raise ValueError(f'Unsupported wall direction: {axis}')
        if not math.isfinite(t) or t<=0:raise ValueError('Wall thickness must be finite and positive.')
        merged=[]
        for start,end in sorted(intervals):
            start=float(start);end=float(end)
            if not math.isfinite(start) or not math.isfinite(end) or end<=start:
                raise ValueError('Wall segment coordinates must be finite with positive length.')
            if merged and start<=merged[-1][1]+1e-8:
                merged[-1]=(merged[-1][0],max(end,merged[-1][1]))
            else:
                merged.append((start,end))
        for start,end in merged:
            length=end-start
            area=t*length
            contribution=area*(.2+min(length/height,.9)**2)
            aw[axis]+=contribution
            segments.append(dict(axis=axis,plane_m=plane,start_m=start,end_m=end,
                                 thickness_m=t,wall_length_m=length,
                                 wall_area_m2=area,Aw_contribution_m2=contribution))
    return aw,segments


def _wall_aw_from_patches(height_m, first_base_m, first_top_m, patches):
    """Conservatively audit first-storey projected Aw through its full height.

    A partial-height opening may produce different effective wall segments at
    distinct z slices. Combining their 2D projections would count wall
    material that is missing at some elevations. In that case the automatic
    estimate is unsafe; require an independently reviewed effective-wall Aw.
    Each patch has (axis, plane, thickness, start, end, zmin, zmax).
    """
    base=float(first_base_m); top=float(first_top_m)
    if not math.isfinite(base) or not math.isfinite(top) or top<=base:
        raise ValueError("First storey has invalid base/top elevations.")
    if not patches:
        raise ValueError("No first-storey wall patches were found.")
    cuts=sorted({base,top,*(float(p[5]) for p in patches),
                *(float(p[6]) for p in patches)})
    reference_signature=None
    reference_result=None
    for za,zb in zip(cuts,cuts[1:]):
        if zb-za<=1e-8:
            continue
        mid=(za+zb)/2.
        lines={}
        for axis,plane,thickness,start,end,zmin,zmax in patches:
            if zmin<=mid+1e-8 and zmax>=mid-1e-8:
                lines.setdefault((axis,plane,thickness),[]).append((start,end))
        area,segments=_wall_aw_from_lines(height_m,lines)
        signature=tuple(sorted((row["axis"],round(row["plane_m"],6),
                         round(row["thickness_m"],6),round(row["start_m"],6),
                         round(row["end_m"],6)) for row in segments))
        if reference_signature is None:
            reference_signature=signature
            reference_result=(area,segments)
        elif signature!=reference_signature:
            raise ValueError(
                "First-storey wall footprint changes with elevation (possible "
                "partial-height opening or discontinuity); automatic Aw cannot "
                "merge these wall patches. Review effective first-storey wall "
                "areas and openings against ETABS under NBC §5.1.2.")
    if reference_result is None:
        raise ValueError("No first-storey wall height intervals were available.")
    return reference_result

def _same_edb_file_content(source_edb, workbook_edb):
    """Allow path-renamed .EDB copies only with matching on-disk SHA256.

    A matching name after dropping '- Copy' is not evidence of equivalent
    model stiffness, masses or geometry. Never trust that heuristic.
    """
    import hashlib
    left=Path(str(source_edb));right=Path(str(workbook_edb))
    if not (left.is_file() and right.is_file()):return False
    try:
        if left.stat().st_size!=right.stat().st_size:return False
        def digest(path):
            h=hashlib.sha256()
            with path.open('rb') as handle:
                for block in iter(lambda:handle.read(1024*1024),b''):h.update(block)
            return h.digest()
        return digest(left)==digest(right)
    except (OSError,PermissionError):
        return False


def scaling_workbook_diagnostics(root,export_dir,limit_state='ULS'):
    """Review candidates without treating unmatched workbooks as valid data."""
    from openpyxl import load_workbook
    export_dir=Path(export_dir);root=Path(root)
    selected=export_dir/'NBC105_Workbook_Source.json'
    roots=[export_dir/'Project_Input_Workbooks',export_dir,
           root/'Project_Input_Workbooks',Path(r'D:/Thesis/Main Python Programs/Excel Sheets')]
    candidates=[]
    if selected.is_file():
        try:
            references=json.loads(selected.read_text(encoding='utf-8-sig'))
            candidates.extend(Path(p) for p in references.get('workbooks',[]))
        except (OSError,ValueError) as exc:
            return ['Saved workbook selection is invalid: '+str(exc)]
    for directory in roots:
        if directory.is_dir():
            candidates.extend(directory.glob('*.xlsx'))
    expected=_source_edb_path(export_dir)
    notes=[]
    for path in dict.fromkeys(candidates):
        if not path.is_file():continue
        try:
            wb=load_workbook(path,read_only=True,data_only=True)
            if 'SCALING SUMMARY' not in wb:
                wb.close();continue
            source=str(wb['SCALING SUMMARY']['B4'].value or '').strip()
            wb.close()
            if source and expected and _portable_source_stem(source).casefold()!=_portable_source_stem(expected).casefold():
                identical=_same_edb_file_content(expected,source)
                notes.append(f'{path.name}: B4 source EDB differs from selected model: {source!r}; '+
                             ('files are byte-identical (SHA256 verified)' if identical else
                              'NO verified equality: do not import this workbook as current-model Aw/T.'))
        except (OSError,ValueError,KeyError) as exc:
            notes.append(f'{path.name}: cannot read scaling sheet: {exc}')
    if not candidates:notes.append('No candidate Excel workbooks found. Select the actual NBC calculator and scaling workbook.')
    return notes


def source_workbooks(root, export_dir,limit_state='ULS'):
    """Discover explicit or model-matched current Excel calculation inputs.

    Inputs: project root and ETABS export directory (Path-like), ULS/SLS state.
    Returns: [NBC Calculator workbook Path|None, scaling workbook Path|None].
    The SCALING SUMMARY B4 EDB identity and source floor/state are more
    authoritative than a similar workbook filename. A stored Windows path
    MUST be normalized on Linux CI as well as Windows Spyder. No workbook
    calculations are evaluated: openpyxl reads cached formula values.
    Selecting a workbook is NOT physical validation of wall Aw or periods;
    use the per-cell audit from import_project_inputs and real ETABS checks.
    Read source files only; never modify their values or formula caches.
    """
    root=Path(root);export_dir=Path(export_dir)
    state=str(limit_state).strip().upper()
    if state=='BOTH':state='ULS'
    if state not in ('ULS','SLS'):raise ValueError('limit_state must be ULS or SLS')
    # ETABS source exports and the legacy scaling workbooks are frequently
    # stored in adjacent folders rather than inside the same export folder.
    # Search a bounded directory set, and validate sheet + B4 model identity
    # before choosing anything. Never recursively search an entire drive.
    search=[export_dir/'Project_Input_Workbooks',export_dir,
            export_dir.parent/'Project_Input_Workbooks',export_dir.parent,
            root/'Project_Input_Workbooks',root,
            Path(r'D:/Thesis/Main Python Programs/Excel Sheets')]
    selected=export_dir/'NBC105_Workbook_Source.json'
    if selected.is_file():
        names=json.loads(selected.read_text(encoding='utf-8-sig'))
        explicit=[Path(p) for p in names.get('workbooks',[]) if Path(p).is_file()]
    else:explicit=[]

    candidates=[]
    for directory in search:
        if directory.is_dir():
            candidates.extend(path for path in directory.glob('*.xlsx') if path.is_file())
    candidates=list(dict.fromkeys(explicit+candidates))
    # Explicit choices take priority; do not hide the other workbook type
    # when the user selects only a scaling file or only a calculator.
    expected_source=_source_edb_path(export_dir)
    expected_edb=_portable_source_stem(expected_source).casefold()
    expected_floor=_model_floor(export_dir,expected_source)
    state_tokens=('service','sls') if state=='SLS' else ('ultimate','uls')

    def workbook_info(path):
        try:
            from openpyxl import load_workbook
            wb=load_workbook(path,data_only=True,read_only=True)
            sheets=set(wb.sheetnames)
            source=''
            if 'SCALING SUMMARY' in sheets:
                source=str(wb['SCALING SUMMARY']['B4'].value or '').strip()
            wb.close()
            return sheets,source
        except (OSError,ValueError,KeyError):
            return set(),''

    records=[]
    for path in candidates:
        sheets,source=workbook_info(path)
        if sheets:records.append((path,sheets,source))

    calculator=next((path for path,sheets,_ in records
                     if 'NBC Calculator' in sheets and
                     (path.name==CALCULATOR or path in explicit)),None)
    if calculator is None:
        calculator=next((path for path,sheets,_ in records if 'NBC Calculator' in sheets),None)

    scaling=[record for record in records if 'SCALING SUMMARY' in record[1]]
    def score(record):
        path,_,source=record
        # An explicit stored EDB path for a different building is a hard
        # mismatch even when the scaling workbook has a plausible filename.
        if expected_edb and source and _portable_source_stem(source).casefold()!=expected_edb:
            # Only a binary-identical EDB copy can inherit workbook geometry
            # provenance despite a changed filename. Never drop a 'Copy'
            # suffix and assume source-model equivalence.
            if not _same_edb_file_content(_source_edb_path(export_dir),source):
                return -1
        name=(path.stem+' '+source).casefold()
        has_sls=any(token in name for token in ('service','sls'))
        has_uls=any(token in name for token in ('ultimate','uls'))
        if state=='SLS' and has_uls and not has_sls:
            return -1
        if state=='ULS' and has_sls and not has_uls:
            return -1
        # Match the EDB's floor identifier using the EDB path itself.
        # The source cell often uses Windows backslashes, which are not
        # generic regex word separators on Linux GitHub Actions.
        source_floor=_model_floor(export_dir,source) if source else ''
        filename_floor=_model_floor(export_dir,path.stem)
        actual_floor=source_floor or filename_floor
        if expected_floor and actual_floor and actual_floor != expected_floor:
            return -1
        if expected_floor and not actual_floor:
            return -1
        exact=int(bool(expected_edb) and _portable_source_stem(source).casefold()==expected_edb)
        config_tokens=[token for token in ('belt','truss','outrigger','cap') if token in expected_edb]
        config_matches=sum(token in name for token in config_tokens)
        return (exact*100+config_matches*10+
                int(any(token in path.name.casefold() for token in state_tokens))+
                (50 if path in explicit else 0))

    ranked=sorted(((score(record),record) for record in scaling),key=lambda item:item[0],reverse=True)
    scaling_book=None
    if ranked and ranked[0][0]>=0:
        best=ranked[0][0]
        matches=[record[0] for value,record in ranked if value==best]
        if len(matches)==1:
            scaling_book=matches[0]
        elif explicit:
            scaling_book=next((path for path in explicit if path in matches),None)
    if scaling_book is None:
        default_name=SERVICE_SCALING if state=='SLS' else SCALING
        # Do not bypass the source/floor/limit-state identity check through a
        # hard-coded filename fallback. This previously selected wrong-model
        # ESM Aw and adopted-period reference cells without warning.
        fallback_candidates=[record for record in scaling if record[0].name==default_name]
        valid_fallbacks=[record for record in fallback_candidates if score(record)>=0]
        if len(valid_fallbacks)==1:
            scaling_book=valid_fallbacks[0][0]
    return [calculator,scaling_book]


def import_project_inputs(root, export_dir,limit_state='ULS'):
    """Read source-attributed ESM inputs and optionally audit wall geometry.

    Inputs: ETABS export JSONs + selected or auto-discovered spreadsheets.
    Output: {values, audit, notes}, where audit retains source/sheet/cell and
    geometry terms are separately labeled rather than silently overriding
    workbook Aw. The first story is determined using diaphragm elevations,
    with z-varying wall footprints rejected for automatic Aw computation.
    This screen does not decide physical wall grouping, construction-stage
    seismic base or the actual effective area at openings (NBC §5.1.2).
    Rayleigh cache values are accepted only when model/weight/state/Aw hashes
    and metadata match; ETABS eigenperiods remain references, not Rayleigh T.
    Side effects: none on the source ETABS files or Excel workbooks.
    """
    from openpyxl import load_workbook
    state=str(limit_state).strip().upper()
    if state not in ('ULS','SLS'):raise ValueError('limit_state must be ULS or SLS')
    require_source_state(export_dir,state)
    values={};audit=[];notes=[]
    # Prevent cached Excel labels and formula-error strings (e.g. 'Aw (m²)')
    # from appearing as valid wall indices or periods in the ESM GUI.
    positive_fields={
        'awx','awy','rayleigh_tx','rayleigh_ty','workbook_adopted_tx',
        'workbook_adopted_ty','Z','I','period_factor','rmu','omegau','omegas',
        'reference_base_shear_X','reference_base_shear_Y',
    }
    def put(key,value,path,sheet,cell):
        if value is None or (isinstance(value,str) and value.startswith('=')):return
        if key in positive_fields:
            try:
                numeric=float(value)
            except (ValueError,TypeError,OverflowError):
                notes.append(f'Invalid {key} in {Path(path).name} {sheet}!{cell}: {value!r}; requires a finite positive number, not a label/formula error.')
                return
            if not math.isfinite(numeric) or numeric<=0:
                notes.append(f'Invalid {key} in {Path(path).name} {sheet}!{cell}: {value!r}; must be finite and positive.')
                return
            value=numeric
        values[key]=value
        audit.append(dict(field=key,value=value,source=str(path),sheet=sheet,cell=cell))
    source_books=source_workbooks(root,export_dir,limit_state)
    if source_books[1] is None:
        notes.append('No source-verified SCALING SUMMARY workbook selected. Inspect candidate B4, B14, B15 values and the current wall geometry audit. Manual reviewed Aw inputs remain available.')
        notes.extend(scaling_workbook_diagnostics(root,export_dir,limit_state))
    if source_books[0] is None:
        notes.append('No NBC Calculator workbook selected: soil, Z, I and system factors require reviewed inputs.')
    for path in source_books:
        if path is None:continue
        wb=load_workbook(path,data_only=True,read_only=True)
        if 'NBC Calculator' in wb:
            ws=wb['NBC Calculator']
            for key,cell in {'soil':'B9','Z':'B10','I':'B11','period_factor':'B15','system_excel':'E10'}.items():put(key,ws[cell].value,path,ws.title,cell)
            system=ws['E10'].value
            if 'NBC Parameters' in wb:
                for row in wb['NBC Parameters'].iter_rows(min_row=16,max_row=36,max_col=4):
                    if row[0].value==system:
                        for key,c in zip(('rmu','omegau','omegas'),row[1:]):put(key,c.value,path,'NBC Parameters',c.coordinate)
            # B16/B17 are ambiguously labelled ETABS/Rayleigh in the workbook.
            # Import neither as Rayleigh without its force/displacement evidence.
            if ws['B16'].value or ws['B17'].value:notes.append('Workbook B16/B17 need a method/source classification; not assigned as Rayleigh periods.')
        if 'SCALING SUMMARY' in wb:
            ws=wb['SCALING SUMMARY']
            for key,cell in {'awx':'B14','awy':'B15','workbook_adopted_tx':'C14','workbook_adopted_ty':'C15','reference_base_shear_X':'E7','reference_base_shear_Y':'E8','source_edb':'B4'}.items():put(key,ws[cell].value,path,ws.title,cell)
        wb.close()
    folder=Path(export_dir)
    topology=folder/'OpenSees_Element_Connectivity.json'
    if topology.is_file():
        topo=json.loads(topology.read_text(encoding='utf-8-sig'));xyz=[n['coordinates_m'] for n in topo.get('node_map',[])]
        if xyz:
            values['breadth_X']=max(p[1] for p in xyz)-min(p[1] for p in xyz)
            values['breadth_Y']=max(p[0] for p in xyz)-min(p[0] for p in xyz)
            notes.append('Plan breadth is computed from the selected source geometry; confirm per-floor accidental eccentricity for setbacks.')
            # Recalculate effective wall areas from current first-story
            # geometry. Each continuous segment keeps its own Lwi; openings
            # and physical gaps split segments instead of using gross bay length.
            try:
                from OpenSees_Complete_Export_V118 import _area_property
                assignments=json.loads((folder/'OpenSees_Section_Assignment_Audit.json').read_text(encoding='utf-8-sig'))
                area_rows={str(r.get('etabs_area_object')):r for r in assignments['area_assignments']}
                assembled=folder/'OpenSees_Complete_Model_Data_V118.json'
                shell_thickness={}
                if assembled.is_file():
                    model=json.loads(assembled.read_text(encoding='utf-8-sig'))
                    for shell in model.get('shells',[]):
                        if shell.get('category')=='SHEAR WALL':
                            thickness=shell.get('properties',{}).get('thickness')
                            if thickness is not None:
                                shell_thickness.setdefault(str(shell.get('object')),float(thickness))
                coords={n['opensees_node_tag']:n['coordinates_m'] for n in topo['node_map']}
                base=min(p[2] for p in xyz);roof=max(p[2] for p in xyz);H=roof-base
                levels=sorted({g['master_xyz'][2] for g in topo['rigid_diaphragm_groups'] if g['master_xyz'][2]>base+1e-6})
                if not math.isfinite(H) or H<=0:raise ValueError('Source model has no positive base-to-roof height.')
                if not levels:raise ValueError('No source first-storey diaphragm elevation.')
                first=levels[0];lines={};patches=[]
                for e in topo['elements']:
                    if e['category']!='SHEAR WALL':continue
                    q=[coords[n] for n in e['node_tags']]
                    zmin=min(p[2] for p in q);zmax=max(p[2] for p in q)
                    if zmax<=base+1e-6 or zmin>=first-1e-6:continue
                    if zmin<base-1e-6 or zmax>first+1e-6:
                        raise ValueError('A wall shell crosses the first-storey bounds; review its floor/mesh assignment.')
                    dx=max(p[0] for p in q)-min(p[0] for p in q);dy=max(p[1] for p in q)-min(p[1] for p in q)
                    if dx>1e-6 and dy<1e-6:axis='X';along=0;across=1
                    elif dy>1e-6 and dx<1e-6:axis='Y';along=1;across=0
                    else:raise ValueError('Non-axis-aligned wall: directional projected properties need separate review.')
                    assignment=area_rows.get(str(e['etabs_object']),{})
                    try:
                        thickness=_area_property(assignment,{})['thickness']
                    except (KeyError,TypeError,ValueError):
                        thickness=shell_thickness.get(str(e['etabs_object']))
                        if thickness is None or not math.isfinite(thickness) or thickness<=0:
                            raise ValueError(f"Wall {e['etabs_object']} has no positive thickness in the source audit or assembled shell model.")
                    plane=round(q[0][across],6)
                    start=min(p[along] for p in q);end=max(p[along] for p in q)
                    lines.setdefault((axis,plane,thickness),[]).append((start,end))
                    patches.append((axis,plane,thickness,start,end,zmin,zmax))
                aw,segments=_wall_aw_from_patches(H,base,first,patches)
                if not all(v>0 for v in aw.values()):raise ValueError('Both directions need recognized first-story walls.')
                for axis in ('X','Y'):
                    key='aw'+axis.lower()
                    geometry_key='geometry_aw_'+axis.lower()
                    values[geometry_key]=aw[axis]
                    audit.append(dict(field=geometry_key,value=aw[axis],source=str(topology),
                                      sheet='first-story wall geometry',
                                      cell='Σ Awi·[0.2+min(Lwi/H,0.9)^2], NBC 105:2025 §5.1.2'))
                    if key in values:
                        values['workbook_'+key]=values[key]
                        try:
                            workbook_aw=float(values[key])
                            if not math.isfinite(workbook_aw) or workbook_aw<=0:
                                notes.append(f'Workbook {key.upper()} must be a finite positive area before use; review the source cell.')
                            elif not math.isclose(workbook_aw,aw[axis],rel_tol=1e-6,abs_tol=1e-9):
                                notes.append(f'Workbook {key.upper()} ({workbook_aw:g} m²) differs from the independent exported-geometry estimate ({aw[axis]:g} m²). The reviewed workbook input is preserved; reconcile wall grouping, openings, and Lwi before adopting either value.')
                        except (TypeError,ValueError):
                            notes.append(f'Workbook {key.upper()} is not numeric; review the source cell before period calculations.')
                    else:
                        values[key]=aw[axis]
                        audit.append(dict(field=key,value=aw[axis],source=str(topology),
                                          sheet='first-story wall geometry',
                                          cell='automatic fallback to geometry_aw_'+axis.lower()))
                values['wall_geometry_segments']=segments
                notes.append('The automatic geometry estimate merges shell mesh subdivisions and treats separated wall segments independently; it is an audit/fallback, not an interpretation of how to group perforated walls for NBC Aw. A reviewed workbook Aw is preserved for period calculations. Confirm wall/opening grouping, directional Lwi, and whether seismic height H excludes qualifying basements under NBC 105:2025 §5.1.2.')
            except Exception as exc:
                notes.append('Live wall Aw reconstruction unavailable; imported workbook Aw remains a review input: '+str(exc))
    ray_name='NBC105_Rayleigh_Preliminary_V123'+('_SLS' if state=='SLS' else '')+'.json'
    ray=analysis_output_folder(folder,state)/ray_name
    if not ray.is_file():
        ray=folder/'OpenSees_Analysis_Results'/ray_name
    data=folder/'OpenSees_Complete_Model_Data_V118.json'
    if ray.is_file() and data.is_file():
        import hashlib
        result=json.loads(ray.read_text(encoding='utf-8-sig'))
        ledger=folder/'NBC105_ESM_Story_Weights_Assembled_V118.csv'
        valid=(result.get('method_version',0)>=125 and result.get('limit_state')==state
               and result.get('model_sha256')==hashlib.sha256(data.read_bytes()).hexdigest()
               and ledger.is_file()
               and result.get('story_weights_sha256')==hashlib.sha256(ledger.read_bytes()).hexdigest())
        if valid:
            for axis in ('X','Y'):
                axis_result=result[axis]
                period=axis_result.get('period_s')
                aw=values.get('aw'+axis.lower())
                if (not isinstance(period,(int,float)) or not math.isfinite(period) or period<=0
                        or not isinstance(axis_result.get('Aw_m2'),(int,float))
                        or not math.isfinite(axis_result['Aw_m2']) or axis_result['Aw_m2']<=0
                        or (aw is not None and not math.isclose(axis_result['Aw_m2'],float(aw),rel_tol=1e-8,abs_tol=1e-9))):
                    valid=False
                    break
            if valid:
                for axis in ('X','Y'):put('rayleigh_t'+axis.lower(),result[axis]['period_s'],ray,axis,'period_s')
        if not valid:notes.append(f'Saved {state} Rayleigh results are stale, incomplete, or inconsistent with the current model, seismic weights, or wall Aw; rerun the preliminary analysis.')
    notes.append('Regularity is not inferred from Excel or model symmetry. Confirm NBC §5.4 for the asymmetric building.')
    return dict(values=values,audit=audit,notes=notes)


def populate(gui, root, folder):
    state=getattr(gui,'ls',getattr(gui,'limit_state',getattr(gui,'state',None)))
    state=state.get() if state is not None else 'ULS'
    import_state='ULS' if str(state).strip().upper()=='BOTH' else state
    data=import_project_inputs(root,folder,import_state);v=data['values']
    if str(state).strip().upper()=='BOTH':
        data['notes'].append('Both ULS and SLS selected; shared project/workbook inputs are sourced from the ULS case. State-specific Rayleigh results remain separate.')
    for key in ('soil','Z','I','awx','awy','rmu','omegau','omegas','period_factor','rayleigh_tx','rayleigh_ty'):
        var=getattr(gui,key,None)
        if var is not None and key in v:var.set(str(v[key]))
    # The project's explicitly stated location, not a municipality inferred
    # from a filename or an unverified zoning lookup.
    if hasattr(gui,'location') and not gui.location.get():gui.location.set('Kirtipur')
    if 'Dual' in str(v.get('system_excel','')) and 'Shear wall' in str(v.get('system_excel','')):
        if hasattr(gui,'system'):gui.system.set('RC dual system with shear wall')
    for target,source in [('aw_x','awx'),('aw_y','awy'),('tr_x','rayleigh_tx'),('tr_y','rayleigh_ty')]:
        if hasattr(gui,target) and source in v:getattr(gui,target).set(str(v[source]))
    if hasattr(gui,'bdim'):
        gui.bdim.set(str(v.get('breadth_'+gui.direction.get(),'')))
    gui.project_input_audit=data
    return data


def connect_etabs():
    """Use CSI Helper attachment first; tolerate ROT registration differences."""
    import comtypes.client
    errors=[]
    try:
        helper=comtypes.client.CreateObject('ETABSv1.Helper')
        try:
            from comtypes.gen import ETABSv1
            helper=helper.QueryInterface(ETABSv1.cHelper)
        except ImportError:pass
        etabs=helper.GetObject('CSI.ETABS.API.ETABSObject')
        if etabs is not None:return etabs
    except Exception as exc:errors.append(str(exc))
    try:return comtypes.client.GetActiveObject('CSI.ETABS.API.ETABSObject')
    except Exception as exc:raise RuntimeError('ETABS attachment failed. Use the same Windows account and elevation for ETABS and Python. Cached workbook inputs remain available. '+str(exc)+'; '+ '; '.join(errors)) from exc
