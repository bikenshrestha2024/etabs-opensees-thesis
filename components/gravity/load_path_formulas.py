"""Formula trace of applied shell loads; does not invent equivalent beam UDLs."""
from pathlib import Path
import json
from components.nbc105.constants import GRAVITY_M_S2


def recovered_vertical_transfers(payload, elevations_m):
    """Recover global Fz at horizontal mesh boundaries from static end forces.

    Uses OpenSees eleForce, six DOFs per node (kN, kN-m). The cut is just
    above each elevation; only elements crossing that boundary contribute.
    Lower-node resisting Fz is reported with its solver sign. This is a
    discrete interface resultant, not an interior-joint support reaction or
    interpolation through an element. Incomplete force vectors are rejected.
    [REF docs/source/components/gravity/load_path_formulas.py.md]
    """
    import math
    def index_unique(records, field, label):
        indexed={}
        for record in records:
            tag=int(record[field])
            if tag in indexed:
                raise ValueError('Duplicate '+label+' tag: '+str(tag))
            indexed[tag]=record
        return indexed
    nodes=index_unique(payload['nodes'],'tag','node')
    edges=index_unique(payload['elements'],'tag','element')
    forces=index_unique(payload.get('global_end_forces',[]),'tag','global force')
    if set(forces)!=set(edges) or payload.get('missing_global_forces'):
        raise ValueError('Complete frame and shell global end forces required; rerun gravity with current recorder')
    # Validate every force vector even when no requested interface crosses it,
    # and when called by vertical_joint_balance with an empty level list.
    for tag, element in edges.items():
        connected=list(map(int,element['nodes']))
        if not connected or len(set(connected))!=len(connected):
            raise ValueError('Duplicate or missing element endpoint tags: '+str(tag))
        if any(node not in nodes for node in connected):
            raise ValueError('Element references absent node: '+str(tag))
        vector=forces[tag]
        if list(map(int,vector['nodes']))!=connected or len(vector['forces'])!=6*len(connected):
            raise ValueError('Global end-force node ordering/length mismatch: '+str(tag))
        if not all(math.isfinite(float(v)) for v in vector['forces']):
            raise ValueError('Nonfinite global end-force vector: '+str(tag))
    edges={tag:list(map(int,element['nodes'])) for tag,element in edges.items()}
    for node in nodes.values():
        if not math.isfinite(float(node['z_m'])):
            raise ValueError('Nonfinite node elevation')
    rows=[]
    levels=set(map(float,elevations_m))
    if not all(math.isfinite(level) for level in levels):
        raise ValueError('Nonfinite requested floor elevation')
    for level in sorted(levels):
        total=0.;count=0
        for tag,tags in edges.items():
            z=[float(nodes[n]['z_m']) for n in tags]
            if min(z)>level+1e-7 or max(z)<=level+1e-7:continue
            e=forces[tag];v=e['forces']
            if list(map(int,e['nodes']))!=tags or len(v)!=6*len(tags):
                raise ValueError('Global end-force node ordering/length mismatch')
            if not all(math.isfinite(float(x)) for x in v):raise ValueError('Nonfinite element force')
            total+=sum(float(v[6*i+2]) for i,zz in enumerate(z) if zz<=level+1e-7)
            count+=1
        rows.append(dict(elevation_m=level,crossing_elements=count,lower_face_resisting_Fz_kN=total,
                         basis='RECOVERED_GLOBAL_ELEMENT_END_FORCES_AT_MESH_INTERFACE'))
    return rows


def vertical_joint_balance(payload, applied_fz_kN):
    """Signed static joint balance: element Fz minus applied Fz minus reaction.

    Forces in kN, downward applied loads negative. Interior residuals are
    equilibrium checks, not support reactions. Requires all frame/shell ends.
    [REF docs/source/components/gravity/load_path_formulas.py.md]
    """
    import math
    recovered_vertical_transfers(payload, [])  # completeness gate
    totals={int(n['tag']):0. for n in payload['nodes']}
    for element in payload['global_end_forces']:
        tags=element['nodes'];values=element['forces']
        if len(values)!=6*len(tags):raise ValueError('Invalid global force vector')
        for i,tag in enumerate(tags):
            fz=float(values[6*i+2])
            if not math.isfinite(fz):raise ValueError('Nonfinite element force')
            totals[int(tag)]+=fz
    reactions={}
    for row in payload['reactions']:
        tag=int(row['node_tag'])
        if tag in reactions:
            raise ValueError('Duplicate support reaction node tag: '+str(tag))
        reaction=float(row['rz_kN'])
        if tag not in totals or not math.isfinite(reaction):
            raise ValueError('Invalid support reaction node/value: '+str(tag))
        reactions[tag]=reaction
    applied={}
    for raw_tag, raw_value in applied_fz_kN.items():
        tag=int(raw_tag)
        if tag in applied:
            raise ValueError('Duplicate applied-load node tag: '+str(tag))
        force=float(raw_value)
        if tag not in totals or not math.isfinite(force):
            raise ValueError('Invalid applied-load node/value: '+str(tag))
        applied[tag]=force
    rows=[]
    for node in payload['nodes']:
        tag=int(node['tag']);force=applied.get(tag,0.);reaction=reactions.get(tag,0.)
        rows.append(dict(node_tag=tag,z_m=node['z_m'],is_support=tag in reactions,
                         element_resisting_Fz_kN=totals[tag],applied_Fz_kN=force,
                         support_Rz_kN=reaction,residual_Fz_kN=totals[tag]-force-reaction))
    return rows

def add_formula_audit(wb,folder,data=None,cfg=None,progress=None):
    from openpyxl.styles import Font,PatternFill
    from openpyxl.workbook.properties import CalcProperties
    folder=Path(folder)
    def read(name):
        path=folder/name
        return json.loads(path.read_text(encoding='utf-8-sig')) if path.is_file() else {}
    data=read('OpenSees_Complete_Model_Data_V118.json') if data is None else data;cfg=read('OpenSees_Complete_Model_Config_V118.json') if cfg is None else cfg;audit=read('OpenSees_Load_Conversion_Audit.json')
    if not data:return
    reduced_slab_weight = data.get(
        'joint_volume_weight_policy', cfg.get('joint_volume_weight_policy')
    ) == 'VERIFIED_SINGLE_OWNER'
    # Formula arithmetic replaces only derived cells, never recorded solver DOFs.
    for title in ('Source detail','Source load detail'):
        if title in wb:
            ws=wb[title];cols={c.value:c.column for c in ws[1]}
            if all(k in cols for k in ('gravity_factor','unfactored_kN','applied_kN')):
                from openpyxl.utils import get_column_letter as letter
                for row in range(2,ws.max_row+1):ws.cell(row,cols['applied_kN'],f'={letter(cols["gravity_factor"])}{row}*{letter(cols["unfactored_kN"])}{row}')
    for title in ('Surface load formulas','Loaded node path','Member weight formulas','Vertical load path'):
        if title in wb:del wb[title]
    ws=wb.create_sheet('Surface load formulas');ws.append(['Source area','Component','Pattern','Mesh cell','Area m2','Downward q kN per m2','Gravity factor','Mass factor','Q unfactored kN','Applied kN','Mass tonnes','Node share kN','Nodes','Origin','Physical thickness m','Unit weight kN per m3','Self-weight multiplier'])
    # Excel's hard row ceiling is 1,048,576 including the header. A 16x16
    # slab mesh can produce >1M per-node pressure paths; partition without
    # truncating the data or referring to nonexistent worksheet rows.
    from openpyxl.xml.constants import MAX_ROW
    node_headers=['Source area','Pattern','Cell row','Node','X m','Y m','Z m','Applied nodal Fz kN downward','Connected beam solver tags','Connected wall solver tags','Role']
    links=wb.create_sheet('Loaded node path')
    links.append(node_headers)
    node_sheet_number=1
    node_sheet_row=1
    def append_node_path(record):
        nonlocal links,node_sheet_number,node_sheet_row
        # Worksheet.max_row scans all existing cells. Calling it for every
        # node made this mesh ledger quadratic in its number of rows.
        if node_sheet_row>=MAX_ROW:
            node_sheet_number+=1
            links=wb.create_sheet(f'Loaded node path {node_sheet_number:02d}')
            links.append(node_headers)
            node_sheet_row=1
        links.append(record)
        node_sheet_row+=1
    adjacency={};walls={}
    for tag,e in enumerate(data.get('frames',[]),100001):
        if e['category']=='BEAM':
            for n in e['nodes']:adjacency.setdefault(int(n),[]).append(tag)
    for tag,e in enumerate(data.get('shells',[]),100001+len(data.get('frames',[]))):
        if e['category']=='SHEAR WALL':
            for n in e['nodes']:walls.setdefault(int(n),[]).append(tag)
    pressure={}
    for item in audit.get('applied_area_loads',[]):pressure.setdefault(str(item['object']),[]).append(item)
    multipliers={r['pattern']:float(r['multiplier']) for r in audit.get('etabs_load_pattern_self_weight_multipliers',[]) if r.get('multiplier') is not None}
    surface_row=1
    if callable(progress):
        progress('Excel: generating source pressure and loaded-node formulas')
    for index,cell in enumerate(data.get('shells',[]),1):
        if callable(progress) and index % 10000 == 0:
            progress(f'Excel: processed {index:,} of {len(data.get("shells", [])):,} assembled shell cells')
        if cell.get('category')!='FLOOR':continue
        entries=[]
        for item in pressure.get(str(cell['object']),[]):entries.append((item['pattern'],'area_load',float(item['value'])*(1 if int(item['direction_code'])==10 else -1),item.get('load_set') or item.get('api','source')))
        for pattern,mult in multipliers.items():
            if mult:entries.append((pattern,'self_weight_floor',cell['properties']['thickness']*cell['properties']['weight']*mult,'physical thickness * source unit weight * ETABS self-weight multiplier'))
        for pattern,component,q,origin in entries:
            surface_row+=1;row=surface_row;own=component=='self_weight_floor';ws.append([cell['object'],component,pattern,index,cell['area'],f'=O{row}*P{row}*Q{row}' if own else q,1.0,cfg['mass_factors'].get(pattern,0),f'=E{row}*F{row}',f'=I{row}*G{row}',f'=I{row}*H{row}/{GRAVITY_M_S2!r}',f'=J{row}/4',','.join(map(str,cell['nodes'])),origin,cell['properties']['thickness'] if own else None,cell['properties']['weight'] if own else None,multipliers.get(pattern) if own else None])
            for node in cell['nodes']:
                xyz=data['nodes'].get(int(node),data['nodes'].get(str(node))); beams=adjacency.get(int(node),[]);wall=walls.get(int(node),[])
                append_node_path([cell['object'],pattern,row,node,*xyz,f"='Surface load formulas'!L{row}",','.join(map(str,beams)),','.join(map(str,wall)),'beam joint' if beams else 'wall joint' if wall else 'slab interior / other joint'])
    # Independent workbook ledger for full node-path coverage, including all
    # overflow sheets. Never describe an incomplete mesh model as verified.
    sheet_index=wb.create_sheet('Loaded node path index')
    sheet_index.append(['Worksheet','Data rows','Meaning'])
    for item in wb.worksheets:
        if (item.title=='Loaded node path' or
            (item.title.startswith('Loaded node path ') and
             item.title.removeprefix('Loaded node path ').isdecimal())):
            sheet_index.append([item.title,item.max_row-1,'Untruncated node-level slab pressure load path'])
    # The primary worksheet is the full-gravity validation load path (1.0D
    # + 1.0L). Preserve a separate configured seismic-preload view; mass
    # factors remain an independent column in BOTH sheets.
    if callable(progress):
        progress(f'Excel: created {surface_row-1:,} surface pressure rows; duplicating seismic preload sheet')
    seismic=wb.copy_worksheet(ws)
    seismic.title='Surface seismic preload'
    for row in range(2,seismic.max_row+1):
        pattern=str(seismic.cell(row,3).value)
        if pattern not in cfg['gravity_factors']:
            raise ValueError('Slab seismic preload has no gravity factor for pattern '+pattern)
        seismic.cell(row,7,float(cfg['gravity_factors'][pattern]))
    # Make the validated 1.0D+1.0L sheet appear first for users opening
    # the workbook in Excel, rather than showing 0.3 as the gravity case.
    ws.sheet_view.showGridLines=True
    seismic.sheet_view.showGridLines=True
    weights=wb.create_sheet('Member weight formulas');weights.append(['Source frame','Solver tag','Category','Area m2','Length m','Unit weight kN per m3','Volume m3','Gross physical weight kN','Note'])
    for tag,e in enumerate(data.get('frames',[]),100001):
        r=tag-100001+2;weights.append([e['object'],tag,e['category'],e['properties']['A'],e['length'],e['properties']['weight'],f'=D{r}*E{r}',f'=G{r}*F{r}','Before self-weight pattern multiplier and gravity factor; overlap conventions require review'])
    floor_objects={str(e['object']) for e in data.get('shells',[]) if e.get('category')=='FLOOR'}
    for title in ('Source detail','Source load detail'):
        if title not in wb:continue
        sheet=wb[title];cols={c.value:c.column for c in sheet[1]}
        if not all(key in cols for key in ('source','pattern','component','unfactored_kN')):continue
        from openpyxl.utils import get_column_letter as letter
        end=ws.max_row
        for row in range(2,sheet.max_row+1):
            obj=str(sheet.cell(row,cols['source']).value).removeprefix('AREA:')
            comp=sheet.cell(row,cols['component']).value
            # The assembled source ledger already includes retained volume.
            # A gross cell sum would discard that correction.
            if reduced_slab_weight and comp == 'self_weight_floor':
                continue
            if obj in floor_objects and comp in ('area_load','self_weight_floor'):
                pattern=f'{letter(cols["pattern"])}{row}';component=f'{letter(cols["component"])}{row}'
                sheet.cell(row,cols['unfactored_kN'],f'=SUMIFS(\'Surface load formulas\'!I$2:I${end},\'Surface load formulas\'!A$2:A${end},"{obj}",\'Surface load formulas\'!C$2:C${end},{pattern},\'Surface load formulas\'!B$2:B${end},{component})')
    notes=wb.create_sheet('Vertical load path')
    for line in [
        'Area pressure -> shell mesh equivalent nodal loads -> shell bending/shear and connected beam/wall/column stiffness -> supports.',
        'rigidDiaphragm(3) constrains UX, UY and RZ. It does not constrain UZ or carry vertical pressure.',
        'A uniform four-node parallelogram shell has Q=q*A and a Q/4 vertical equivalent load at each mesh node. This is a finite-element load vector, not tributary beam UDL.',
        'No second q*tributary-width beam load is added: that would double-count the same area pressure.',
        'Loaded node path lists the actual connected beam and wall solver tags. Interior shell nodes transfer through shell stiffness.',
        'A corner-only panel at column joints cannot resolve beam-span bending. V141 adds floor subdivisions (default 4 per source-panel direction) and splits connected beams at shared mesh nodes.',
        'Refinement is a numerical choice, not an NBC-prescribed mesh. Compare 4/8/16 subdivisions using separately assembled/solved models; check beam moments, slab deflection and reactions before design use.',
        'Gravity_Beam_End_Actions_ULS_V141.csv / SLS equivalent are written by complete-model preload. Gravity GUI action tabs also show local shears and bending moments. Beam end actions and shell forces are solver outputs; they cannot be replaced by q*A arithmetic or treated as a unique tributary UDL. Use gravity action reports for actual response.',
        'Surface load formulas: FULL GRAVITY 1.0D+1.0L; all included assigned floor live and roof live at 1.0. It is a separate diagnostic from the configured seismic gravity preload.',
        'Surface seismic preload: configured analysis gravity fractions, for example Live 0.3, while Mass factor remains an independent column in both worksheets.',
        'Do NOT interpret a seismic mass factor of 0.3 as the full gravity live load. Mass factors are unchanged by the gravity runtime profile.',
        'Re-export this workbook after updating the repository; previously saved Slab_Load_Path_Formulas_V141.xlsx will not update automatically.',
        'https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html',
        'https://opensees.berkeley.edu/OpenSees/api/doxygen2/html/RigidDiaphragm_8cpp-source.html',
        'https://opensees.berkeley.edu/OpenSees/api/doxygen2/html/ShellMITC4_8cpp-source.html'] :notes.append([line])
    if reduced_slab_weight:
        notes.append([
            'Floor self-weight rows on both surface sheets and in Loaded node path '
            'are gross-weight diagnostics before single-owner volume corrections. '
            'Source details and storey totals retain the assembled reduced self-weight.'
        ])
    # Display the actual assembled mesh identity, not merely a GUI selection.
    mesh=wb.create_sheet('Mesh identity',0)
    mesh.append(['Parameter','Value','Interpretation'])
    from components.gravity.mesh_cases import validated_mesh_size
    mesh.append(['Subdivisions per source-panel direction',validated_mesh_size(cfg.get('floor_subdivisions',4)),'Actual case must match model-data config SHA256'])
    mesh.append(['Assembled shell cell count',len(data.get('shells',[])),'Includes floors and walls; see Source load detail for floor cells'])
    mesh.append(['Assembly config SHA256',data.get('config_sha256',''),'Hash of config used when assembled model was generated'])
    mesh.append(['Model evidence status','REQUIRES ETABS + SOLVER COMPARISON','Formulas and connectivity alone do not establish gravity load-path equivalence'])
    mesh.append(['Study mode','ONE MESH PER WORKBOOK','4/8/16 require separate rebuilt assembled model runs'])
    mesh.column_dimensions['A'].width=39;mesh.column_dimensions['B'].width=81;mesh.column_dimensions['C'].width=95
    mesh.freeze_panes='A2'
    import csv
    for state in ('ULS','SLS'):
        path=folder/('Gravity_Beam_End_Actions_'+state+'_V141.csv')
        if path.is_file():
            title='Beam end actions '+state
            if title in wb:del wb[title]
            output=wb.create_sheet(title)
            with path.open(encoding='utf-8-sig',newline='') as stream:
                for row in csv.reader(stream):output.append(row)
            output.freeze_panes='A2';output.auto_filter.ref=output.dimensions
    notes.column_dimensions['A'].width=140
    node_sheets=[sheet for sheet in wb.worksheets if
                 sheet.title=='Loaded node path' or
                 (sheet.title.startswith('Loaded node path ') and
                  sheet.title.removeprefix('Loaded node path ').isdecimal())]
    for sheet in (ws,*node_sheets,weights):
        sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
        for c in sheet[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='1E3A5F')
        # Width depends only on the header; iterating sheet.columns walks
        # every data cell and becomes very expensive for MESH_16.
        for header in sheet[1]:
            sheet.column_dimensions[header.column_letter].width=min(55,max(16,len(str(header.value))+2))
    seismic.freeze_panes='A2'
    seismic.auto_filter.ref=seismic.dimensions
    seismic.column_dimensions['G'].width=22
    from openpyxl.utils import get_column_letter as letter
    source_title='Source load detail' if 'Source load detail' in wb else 'Source detail' if 'Source detail' in wb else None
    if source_title:
        detail=wb[source_title];dc={c.value:letter(c.column) for c in detail[1]};last=detail.max_row
        def rng(key):return "'"+source_title+"'!"+dc[key]+"$2:"+dc[key]+"$"+str(last)
        for title in ('Storey totals','Storey load breakdown'):
            if title not in wb:continue
            sheet=wb[title];sc={c.value:c.column for c in sheet[1]}
            for row in range(2,sheet.max_row+1):
                st=letter(sc['storey'])+str(row)
                for key,col in sc.items():
                    if key in ('storey','elevation_m'):continue
                    applied=key.startswith('applied_');amount='applied_kN' if applied else 'unfactored_kN'
                    formula='=SUMIFS('+rng(amount)+','+rng('storey')+','+st
                    if key in ('dead_total_kN','applied_dead_kN'):formula+=','+rng('load_class')+',"DEAD"'
                    elif key in ('live_total_kN','applied_live_kN'):formula+=','+rng('load_class')+',"LIVE"'
                    elif key=='applied_unclassified_kN':formula+=','+rng('load_class')+',"UNCLASSIFIED"'
                    elif key not in ('unfactored_total_kN','applied_total_kN'):formula+=','+rng('classification')+',"'+key+'"'
                    sheet.cell(row,col,formula+')')
            if 'Summary' in wb and title=='Storey load breakdown':
                col=letter(sc['applied_total_kN']);wb['Summary']['B4']=f"=SUM('{title}'!{col}2:{col}{sheet.max_row})"
    if 'Summary' in wb and 'Support Reactions' in wb:
        wb['Summary']['B5']=f"=SUM('Support Reactions'!D2:D{wb['Support Reactions'].max_row})"
        wb['Summary']['B6']='=IF(B4=0,"REVIEW ZERO LOAD",ABS(B5-B4)/ABS(B4)*100)'
    from OpenSees_Mapping_Audit_V125 import parameter_sources,source_parameter_inventory
    title='Material unit formulas'
    if title in wb:del wb[title]
    units=wb.create_sheet(title);units.append(['Family','Parameter','Source value','Source unit','Target unit','Converted value','Validation status','Source'])
    for item in parameter_sources()+source_parameter_inventory(folder,data):
        value=item.get('value');unit=item.get('unit')
        if not isinstance(value,(float,int)) or unit not in ('MPa','ksi','kN/m2','mm'):continue
        row=units.max_row+1;target='m' if unit=='mm' else 'kN/m2' if unit=='MPa' else 'MPa'
        expr=f'=C{row}*1000' if unit=='MPa' else f'=C{row}*6.894757293' if unit=='ksi' else f'=C{row}/1000'
        units.append([item.get('family'),item.get('parameter'),value,unit,target,expr,item.get('status'),item.get('source')])
    units.freeze_panes='A2';units.auto_filter.ref=units.dimensions
    if callable(progress):
        progress('Excel: worksheet formulas complete; ready for .xlsx serialization')
    wb.calculation=CalcProperties(calcId=191029,fullCalcOnLoad=True)


def export(folder, *, output_root=None, progress=None):
    """Verified mesh-specific formula workbook from *matching* assembled model.

    Validate the config SHA and mesh size BEFORE generating any workbook cells.
    `output_root` lets isolated 4/8/16 run directories place their reports
    beside one another rather than nesting another 02_MODEL path.
    """
    from openpyxl import Workbook
    import hashlib
    folder=Path(folder)
    cfg_path=folder/'OpenSees_Complete_Model_Config_V118.json'
    model_path=folder/'OpenSees_Complete_Model_Data_V118.json'
    if not cfg_path.is_file() or not model_path.is_file():
        raise ValueError('Source configuration and assembled model missing. Use "Build selected mesh + export workbook" to create an isolated current mesh run.')
    cfg=json.loads(cfg_path.read_text(encoding='utf-8-sig'))
    model_bytes=model_path.read_bytes()
    data=json.loads(model_bytes.decode('utf-8-sig'))
    from components.gravity.mesh_cases import validated_mesh_size
    n=validated_mesh_size(cfg.get('floor_subdivisions',4))
    actual=hashlib.sha256(cfg_path.read_bytes()).hexdigest()
    if data.get('config_sha256')!=actual:
        raise ValueError('Model config changed after assembly. Do not label old slab cells with new mesh size; choose "Build selected mesh + export workbook" to assemble a matching model.')
    if not any(e.get('category')=='FLOOR' for e in data.get('shells',[])):
        raise ValueError('No assembled FLOOR shell cells found: a mesh-size-specific workbook would be misleading.')
    wb=Workbook();wb.remove(wb.active)
    add_formula_audit(wb,folder,data=data,cfg=cfg,progress=progress)
    if not wb.worksheets:raise ValueError('Complete model does not contain enough source load-path data')
    root=Path(output_root) if output_root is not None else folder/'02_MODEL'/'SLAB_LOAD_PATH'/f'MESH_{n:02d}'
    excel_dir=root/'EXCEL';json_dir=root/'JSON'
    from components.inputs.output_contract import (
        _refuse_linked_output_target,atomic_json)
    _refuse_linked_output_target(excel_dir)
    _refuse_linked_output_target(json_dir)
    excel_dir.mkdir(parents=True,exist_ok=True);json_dir.mkdir(parents=True,exist_ok=True)
    from datetime import datetime
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    path=excel_dir/f'Slab_Load_Path_MESH_{n:02d}_{stamp}_V141.xlsx'
    if callable(progress):
        progress('Excel: saving large .xlsx workbook to disk')
    from components.gravity.workbook_publishing import publish_workbook
    workbook_sha256=publish_workbook(wb,path,temp_prefix='.mesh_')
    if callable(progress):
        progress('Excel: validated .xlsx workbook atomically saved successfully')
    record=dict(mesh_subdivisions=n,config_sha256=actual,
                assembled_model=str(model_path),workbook=str(path),
                assembled_model_sha256=hashlib.sha256(model_bytes).hexdigest(),
                workbook_sha256=workbook_sha256,
                floor_shell_cells=sum(e.get('category')=='FLOOR' for e in data.get('shells',[])),
                total_shell_cells=len(data.get('shells',[])),
                validity='FORMULA_AUDIT_ONLY_NOT_SOLVER_VERIFICATION',
                warning='No reactions, beam forces or mesh-convergence results are inferred. Run separate matching gravity solves with ETABS response comparison')
    atomic_json(json_dir/f'Slab_Load_Path_MESH_{n:02d}_{stamp}_MANIFEST.json',record)
    return path


def launch(parent,folder):
    """2 Model: nonblocking, isolated three-mesh load-path review interface."""
    import os
    import threading
    import queue
    import time
    import tkinter as tk
    from tkinter import ttk, messagebox
    from components.gravity.mesh_cases import prepared_configs, build_case, case_base, package_mesh_case, recover_assembled_mesh_workbook

    folder=Path(folder)
    config=folder/'OpenSees_Complete_Model_Config_V118.json'
    cfg=json.loads(config.read_text(encoding='utf-8-sig')) if config.is_file() else {}
    win=tk.Toplevel(parent)
    win.title('02 Model | Slab mesh and load-path study')
    win.geometry('920x570')
    win.minsize(680,440)
    outer=ttk.Frame(win,padding=14)
    outer.pack(fill='both',expand=True)
    ttk.Label(outer,text='SLAB MESH & LOAD-PATH STUDY',
              font=('Segoe UI',14,'bold')).pack(anchor='w',pady=(0,6))
    ttk.Label(outer,wraplength=870,
              text='Four, eight and sixteen subdivisions are independent models. '
              'Saved mesh configurations are NOT assembled ShellMITC4 cells. '
              'Rebuild each size from the same ETABS source audit before exporting '
              'its formula workbook; later run independent gravity analysis for '
              'load transfer and ETABS equivalence.').pack(anchor='w',pady=(0,10))
    header=ttk.Frame(outer)
    header.pack(fill='x',pady=(0,9))
    ttk.Label(header,text='Selected mesh subdivisions:').pack(side='left')
    choice=tk.StringVar(value=str(cfg.get('floor_subdivisions',4)) if
                        cfg.get('floor_subdivisions',4) in (4,8,16) else '4')
    mesh_selector=ttk.Combobox(
        header,textvariable=choice,
        values=['Current root (hash-checked)','4','8','16'],
        state='readonly',width=8)
    mesh_selector.pack(side='left',padx=9)
    current=ttk.Label(header,text='Current root config: '+str(cfg.get('floor_subdivisions','unknown')))
    current.pack(side='left',padx=10)

    status=tk.StringVar(value='READY | Select mesh and build a fresh independent model.')
    ttk.Label(outer,textvariable=status,wraplength=875).pack(fill='x',pady=(0,7))
    controls=ttk.Frame(outer)
    controls.pack(fill='x',pady=(0,8))
    ttk.Label(controls,text='1  PREPARE',font=('Segoe UI',10,'bold')).grid(row=0,column=0,sticky='w')
    ttk.Label(controls,text='2  ASSEMBLE + EXPORT',font=('Segoe UI',10,'bold')).grid(row=0,column=1,sticky='w',padx=12)
    ttk.Label(controls,text='3  INSPECT',font=('Segoe UI',10,'bold')).grid(row=0,column=2,sticky='w')
    buttons=[]

    def log(message):
        text.configure(state='normal')
        text.insert('end',message+'\n')
        text.see('end')
        text.configure(state='disabled')

    def prepare():
        try:
            paths=prepared_configs(folder)
            status.set('PREPARED ONLY | MESH_04, MESH_08, MESH_16 settings saved; no analysis was run.')
            log('PREPARED CONFIGS: '+', '.join(str(p) for p in paths))
        except Exception as exc:
            status.set('BLOCKED | '+str(exc))
            messagebox.showerror('Prepare mesh configurations',str(exc),parent=win)

    def start_build():
        if choice.get()=='Current root (hash-checked)':
            current_workbook()
            return
        size=int(choice.get())
        events = queue.SimpleQueue()
        started_at = time.monotonic()
        state = {'stage': 'Preparing mesh case'}
        def receive_progress(message, elapsed):
            # Only enqueue from background thread. Never mutate Tk directly.
            events.put((message, elapsed))
        def poll_progress():
            if not win.winfo_exists():
                return
            while not events.empty():
                message, elapsed = events.get_nowait()
                state['stage'] = message
                log(f'[{elapsed:.1f}s] {message}')
            if any(b.cget('state') == 'disabled' for b in buttons):
                elapsed = int(time.monotonic()-started_at)
                status.set(f'RUNNING MESH_{size:02d} | {elapsed}s elapsed | '
                           + state['stage'] + ' | GUI active')
                win.after(500, poll_progress)
        win.after(500, poll_progress)
        # Separate run snapshots preserve all three models and permit
        # comparison later; no root config, EDB or existing gravity results are
        # changed. Model generation can take time, so never block Tk's loop.
        def report_failure(exc):
            mesh_selector.configure(state='readonly')
            for b in buttons:b.configure(state='normal')
            status.set('FAILED | '+str(exc))
            log('FAILED MESH_'+str(size).zfill(2)+': '+str(exc))
            messagebox.showerror('Mesh assembly / workbook export failed',
                                 str(exc)+'\n\nIf a model assembled successfully, select "Retry Excel from assembled mesh (no rebuild)" to avoid reassembling it.',parent=win)
        def report_success(result):
            mesh_selector.configure(state='readonly')
            for b in buttons:b.configure(state='normal')
            status.set('FORMULA EXPORTED | MESH_'+str(size).zfill(2)+' (gravity/ETABS verification still required)')
            log('MESH_'+str(size).zfill(2)+' ASSEMBLED: '+result['assembled_model'])
            log('WORKBOOK: '+result['workbook'])
            log('REVIEW: no independent gravity solver run / reaction match performed')
            messagebox.showinfo('Mesh formula workbook created',
                'Saved a new assembled model and formula workbook.\\n\\n'
                +result['workbook']+
                '\\n\\nThis is NOT an independently solved gravity or NBC acceptance case.',
                parent=win)
        mesh_selector.configure(state='disabled')  # capture exact run size; prevent misleading changes mid-run
        for b in buttons:b.configure(state='disabled')
        status.set('RUNNING | Fresh MESH_'+str(size).zfill(2)+' assembly from saved source audit ...')
        log('START | MESH_'+str(size).zfill(2)+' | new independent model run, not just a renamed spreadsheet')
        def work():
            try:
                result=build_case(folder,size,progress=receive_progress)
            except Exception as exc:
                try:win.after(0,lambda e=exc:report_failure(e))
                except tk.TclError:pass
            else:
                try:win.after(0,lambda r=result:report_success(r))
                except tk.TclError:pass
        threading.Thread(target=work,name='slab_mesh_'+str(size),daemon=True).start()

    def _workbook_job(work,on_success,label):
        """[REF docs/source/components/gravity/load_path_formulas.py.md]
        Run heavy workbook work off Tk; deliver every GUI update by main-loop polling.
        """
        if any(b.cget('state')=='disabled' for b in buttons):
            return  # independent build/recovery/export already owns these controls
        events=queue.SimpleQueue()
        mesh_selector.configure(state='disabled')
        for b in buttons:b.configure(state='disabled')
        status.set(label)
        def worker():
            try:
                result=work(lambda message:events.put(('progress',message)))
            except Exception as exc:
                events.put(('error',f'{type(exc).__name__}: {exc}'))
            else:
                events.put(('done',result))
        def poll():
            if not win.winfo_exists():return
            while True:
                try:kind,value=events.get_nowait()
                except queue.Empty:break
                if kind=='progress':
                    status.set(value);log(value)
                    continue
                mesh_selector.configure(state='readonly')
                for b in buttons:b.configure(state='normal')
                if kind=='error':
                    status.set('WORKBOOK FAILED | '+value);log('WORKBOOK FAILED: '+value)
                else:on_success(value)
                return
            win.after(250,poll)
        threading.Thread(target=worker,daemon=True,name='mesh_workbook_export').start()
        win.after(250,poll)

    def recover_workbook():
        if choice.get()=='Current root (hash-checked)':
            current_workbook()
            return
        size=int(choice.get())
        def complete(result):
            status.set('FORMULA RECOVERED | '+str(result['workbook']))
            log('FORMULA WORKBOOK RECREATED: '+str(result['workbook']))
        _workbook_job(
            lambda progress:recover_assembled_mesh_workbook(folder,size,progress=progress),
            complete,f'RECOVERING | MESH_{size:02d} already-assembled model...')

    def current_workbook():
        def complete(workbook):
            status.set('FORMULA EXPORTED | Original assembled root model; gravity not verified.')
            log('CURRENT MODEL WORKBOOK: '+str(workbook))
            if hasattr(os,'startfile'):os.startfile(str(workbook))
            else:messagebox.showinfo('Workbook exported','Saved: '+str(workbook),parent=win)
        _workbook_job(lambda progress:export(folder,progress=progress),complete,
                      'EXPORTING | Existing root mesh workbook...')
    def open_cases():
        root=folder/'02_MODEL'/'SLAB_LOAD_PATH'
        if not root.is_dir():
            messagebox.showinfo('Mesh cases','Prepare or build the cases first.',parent=win)
        elif hasattr(os,'startfile'):os.startfile(str(root))
        else:messagebox.showinfo('Mesh case folder',str(root),parent=win)
    def export_zip():
        if choice.get()=='Current root (hash-checked)':
            status.set('Select 4, 8, or 16 for an independent diagnostic ZIP.')
            return
        size=int(choice.get())
        def run():
            try:
                result=package_mesh_case(folder,size)
            except Exception as exc:
                win.after(0,lambda e=exc:(status.set('ZIP FAILED | '+str(e)),log('ZIP FAILED: '+str(e))))
            else:
                win.after(0,lambda p=result:(status.set('ZIP CREATED | '+str(p)),log('ZIP: '+str(p))))
        threading.Thread(target=run,daemon=True,name='mesh_diagnostic_zip').start()

    ttk.Button(header,text='ZIP selected mesh',command=export_zip).pack(side='right',padx=8)
    prep_button=ttk.Button(controls,text='Prepare 4 / 8 / 16 configs',command=prepare)
    build_button=ttk.Button(controls,text='Build selected mesh / verified root + Excel',command=start_build)
    open_button=ttk.Button(controls,text='Open case output folders',command=open_cases)
    prep_button.grid(row=1,column=0,sticky='ew',pady=5)
    build_button.grid(row=1,column=1,sticky='ew',padx=12,pady=5)
    open_button.grid(row=1,column=2,sticky='ew',pady=5)
    recover_button=ttk.Button(controls,text='Retry Excel from assembled mesh (no rebuild)',command=recover_workbook)
    recover_button.grid(row=2,column=1,sticky='ew',padx=12,pady=2)
    controls.columnconfigure(0,weight=1);controls.columnconfigure(1,weight=1);controls.columnconfigure(2,weight=1)
    buttons.extend((prep_button,build_button,recover_button))
    advanced=ttk.LabelFrame(outer,text='Existing root export — only if it is already rebuilt',padding=9)
    advanced.pack(fill='x',pady=(2,7))
    root_workbook_button=ttk.Button(advanced,text='Export root assembled mesh workbook (hash-checked)',
                                    command=current_workbook)
    root_workbook_button.pack(side='left')
    buttons.append(root_workbook_button)
    ttk.Label(advanced,text='Choose Current root in the mesh dropdown for a hash-checked root export. A changed mesh setting invalidates older assembly.',
              wraplength=440).pack(side='left',padx=10)
    ttk.Label(outer,text='Run log (copyable)',font=('Segoe UI',10,'bold')).pack(anchor='w')
    panel=ttk.Frame(outer)
    panel.pack(fill='both',expand=True)
    text=tk.Text(panel,height=8,wrap='none',state='disabled')
    vert=ttk.Scrollbar(panel,orient='vertical',command=text.yview)
    horiz=ttk.Scrollbar(outer,orient='horizontal',command=text.xview)
    text.configure(yscrollcommand=vert.set,xscrollcommand=horiz.set)
    text.pack(side='left',fill='both',expand=True)
    vert.pack(side='right',fill='y')
    horiz.pack(fill='x')
    log('Each mesh run has its own source snapshot, model config hash, build status, and Excel/JSON evidence.')
    log('Gravity reactions and recovered shell/frame forces must be calculated separately, per mesh.')
    return win
