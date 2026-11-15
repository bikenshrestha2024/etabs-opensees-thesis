"""Search source IDs independently of model assembly success. Units: kN, m, s."""

__release__ = '161'
from pathlib import Path
import json
import html

def export_id_audit(folder, payload=None, report=None):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    folder=Path(folder)
    read=lambda name: json.loads((folder/name).read_text(encoding="utf-8-sig")) if (folder/name).is_file() else {}
    topology=read("OpenSees_Element_Connectivity.json")
    metadata=read("OpenSees_Source_Model_Metadata_V118.json")
    # Non-destructive labels are extra lookup metadata, never OpenSees tags.
    from components.model.display_ids import build_labels, member_identity
    # User-reviewed role mapping uses ETABS UNIQUE object IDs only, never
    # topology preview or numerical OpenSees solver tags.
    cfg=read("OpenSees_Complete_Model_Config_V118.json")
    role_overrides=cfg.get("display_member_roles", {}) or {}
    if not isinstance(role_overrides, dict):
        raise ValueError("display_member_roles must map ETABS object IDs to BR/CO/BT/CT")
    if any(str(value).strip().upper() not in {"BR", "CO", "BT", "CT"}
           for value in role_overrides.values()):
        raise ValueError("Invalid display_member_roles value; expected BR/CO/BT/CT")
    nodes=[dict(n) for n in topology.get("node_map",[])]
    def valid_floor(value):
        try:
            result=int(value)
            return result if result>=0 else None
        except (ValueError,TypeError):
            return None
    node_records=[
        dict(native_id=n["opensees_node_tag"],category="NODE",
             storey=valid_floor(n.get("etabs_storey_number")))
        for n in nodes if valid_floor(n.get("etabs_storey_number")) is not None
    ]
    node_labels=build_labels(node_records)
    for n in nodes:
        n["display_label"]=node_labels.get(str(n["opensees_node_tag"]),"UNCLASSIFIED_LEVEL")
    structural_categories={"BEAM","BRACE","COLUMN","SHEAR WALL","FLOOR",
        "CONVENTIONAL OUTRIGGER","BELT TRUSS","CAP TRUSS","FVD","BRB"}
    elements=[dict(e) for e in topology.get("elements",[])]
    classified=[]
    source_ids={str(e.get("etabs_object")) for e in elements}
    unrecognized=set(map(str,role_overrides))-source_ids
    if unrecognized:
        raise ValueError("display_member_roles references absent ETABS IDs: "
                         + ", ".join(sorted(unrecognized)[:20]))
    for element in elements:
        category=str(element.get("category","")).upper().strip()
        storey=valid_floor(element.get("storey_number"))
        override=role_overrides.get(str(element.get("etabs_object")))
        if category in structural_categories:
            identity=member_identity(category, override)
            element["member_family"]=identity["family"]
            element["brace_role"]=identity["brace_role"]
            element["display_category"]=identity["prefix"]
            if storey is not None:
                # The grouping is based on the explicit role, preserving
                # independent per-storey CO, BT, CT and ordinary BR counters.
                classified.append(dict(
                    native_id=str(element.get("dimension"))+":"+str(element.get("etabs_object")),
                    category=("BRACE" if identity["prefix"]=="BR" else
                              next((k for k,v in {"CONVENTIONAL OUTRIGGER":"CO","BELT TRUSS":"BT",
                                                 "CAP TRUSS":"CT"}.items() if v==identity["prefix"]),category)),
                    storey=storey))
        else:
            element["member_family"]="UNCLASSIFIED"
            element["brace_role"]=""
            element["display_category"]="UNCLASSIFIED"
            if override is not None:
                raise ValueError("Role override requires classified brace member: "
                                 +str(element.get("etabs_object")))
    element_labels=build_labels(classified)
    for element in elements:
        key=str(element.get("dimension"))+":"+str(element.get("etabs_object"))
        element["display_label"]=element_labels.get(key,"UNCLASSIFIED_MEMBER")
    reverse={str(n["opensees_node_tag"]):str(n["etabs_point_name"]) for n in nodes}
    rows=[]
    assembled={}
    for index,element in enumerate((payload or {}).get("frames",[]),100001):
        assembled.setdefault(str(element.get("object")),[]).append(index)
    assembled_area={}
    for index,element in enumerate((payload or {}).get('shells',[]),100001+len((payload or {}).get('frames',[]))):
        assembled_area.setdefault(str(element.get('object')),[]).append(index)
    for e in elements:
        rows.append([str(e.get("etabs_object","")),e.get("dimension"),e.get("category"),e.get("storey_number"),e.get("assigned_section",e.get("assigned_property","")),e.get("element_tag"),json.dumps(e.get("node_names",[])),json.dumps(e.get("node_tags",[])),json.dumps(assembled.get(str(e.get("etabs_object")),[])) if payload else "NOT ASSEMBLED",e.get("display_label","UNCLASSIFIED_MEMBER"),e.get("member_family","UNCLASSIFIED"),e.get("brace_role",""),e.get("display_category","UNCLASSIFIED")])
    wb=Workbook();ws=wb.active;ws.title="Read me"
    for row in [["ETABS / OpenSees identifier audit"],["ETABS unique object name is not an OpenSees element tag."],["Preview tags describe exported topology; assembled tags describe solver elements."],["Gravity support input uses OpenSees node tags, never ETABS point names."],["Support rows are source restraints even if assembly fails; they do not prove a runnable model."],["Assembly errors",json.dumps((report or {}).get("assembly_errors",[]))]]:ws.append(row)
    def sheet(name,headers,data):
        s=wb.create_sheet(name);s.append(headers)
        for row in data:s.append(row)
        s.freeze_panes="A2";s.auto_filter.ref=s.dimensions
        for c in s[1]:c.font=Font(bold=True,color="FFFFFF");c.fill=PatternFill("solid",fgColor="17365D")
        for column in s.columns:s.column_dimensions[column[0].column_letter].width=min(65,max(18,max(len(str(c.value or "")) for c in column)+2))
    headers=["ETABS unique object name","Dimension","Category","Storey number","ETABS section","OpenSees topology preview tag","ETABS end point names","OpenSees end node tags","Assembled frame element tags","Display label (not solver tag)","Main family","Brace role","Display prefix"]
    sheet("Elements",headers,rows)
    sheet("Nodes",["ETABS point name","OpenSees node tag","Storey","X m","Y m","Z m","Display label (not solver tag)"],[[n["etabs_point_name"],n["opensees_node_tag"],n.get("etabs_storey_number"),*n["coordinates_m"],n.get("display_label","UNCLASSIFIED_LEVEL")] for n in nodes])
    sheet("Supports",["OpenSees node tag","ETABS point name","UX fixed","UY fixed","UZ fixed","RX fixed","RY fixed","RZ fixed"],[[int(tag),reverse.get(str(tag),"generated mesh node"),*flags] for tag,flags in metadata.get("supports",{}).items() if any(flags)])
    wb.save(folder/"OpenSees_ID_and_Support_Audit.xlsx")
    # An editable review *reference*, not an automatic mechanical classifier.
    # A brace on storey 25 is not assumed to be a cap-truss member: project
    # drawings/ETABS groups must establish CO, BT and CT role explicitly.
    import csv
    brace_review=folder/"OpenSees_Brace_Role_Review.csv"
    with brace_review.open("w",newline="",encoding="utf-8-sig") as stream:
        writer=csv.writer(stream)
        writer.writerow(["ETABS unique object name","Storey","ETABS source category",
                         "Main family","Current role","Display label",
                         "Review status","Required evidence"])
        for e in elements:
            if e.get("member_family")!="BRACE":
                continue
            obj=str(e.get("etabs_object"))
            category=str(e.get("category","")).upper().strip()
            explicit=obj in role_overrides or category in (
                "CONVENTIONAL OUTRIGGER","BELT TRUSS","CAP TRUSS")
            writer.writerow([obj,e.get("storey_number"),category,"BRACE",
                             e["brace_role"],e["display_label"],
                             ("SOURCE_ROLE_RECORDED_REVIEW_GEOMETRY" if explicit else
                              "ORDINARY_BRACE_UNLESS_PROJECT_REVIEW_OVERRIDES"),
                             "ETABS object ID, source member group, wall-to-perimeter "
                             "connection (CO), belt perimeter (BT), roof cap at "
                             "storey 25 (CT); confirm drawings and source geometry"])
    body="""<!doctype html><meta charset=utf-8><title>ETABS / OpenSees ID lookup</title><style>body{font:15px Arial;margin:24px}input{padding:10px;width:280px}td,th{padding:8px;border:1px solid #ddd}table{border-collapse:collapse}th{background:#eef}tr.hide{display:none}</style><h2>ETABS / OpenSees exact ID lookup</h2><p>ETABS object unique names and OpenSees tags are independent. Preview tags are not assembled solver tags.</p><label>ETABS unique object name <input id=e placeholder='e.g. 251'></label> <label>OpenSees preview element tag <input id=o></label><button onclick="e.value='';o.value='';filter()">Clear</button><p id=count></p><table><thead><tr>"""+"".join("<th>"+html.escape(h)+"</th>" for h in headers)+"</tr></thead><tbody>"+"".join("<tr>"+"".join("<td>"+html.escape(str(v or ""))+"</td>" for v in r)+"</tr>" for r in rows)+"""</tbody></table><script>const e=document.getElementById('e'),o=document.getElementById('o');function filter(){let n=0;document.querySelectorAll('tbody tr').forEach(r=>{let ok=(!e.value.trim()||r.cells[0].textContent===e.value.trim())&&(!o.value.trim()||r.cells[5].textContent===o.value.trim());r.classList.toggle('hide',!ok);if(ok)n++});document.getElementById('count').textContent=n+' matching objects'}e.oninput=o.oninput=filter;filter()</script>"""
    (folder/"OpenSees_ID_Lookup.html").write_text(body,encoding="utf-8")

    # Same ID selection overlay in every Plotly export, independent of each
    # view's trace grouping (loads, connectivity, floor plans or structure).
    nodes=list(nodes)
    known={str(n['opensees_node_tag']) for n in nodes}
    for tag,point in (payload or {}).get('nodes',{}).items():
        if str(tag) not in known:nodes.append(dict(opensees_node_tag=int(tag),etabs_point_name='generated mesh',coordinates_m=point))
    xyz={str(n["opensees_node_tag"]):n["coordinates_m"] for n in nodes}
    selector_data=dict(nodes=nodes,elements=elements,xyz=xyz,assembled=assembled,assembled_area=assembled_area)
    script="""<script id="shared-id-selector-v121">window.addEventListener('load',()=>{const D=__DATA__;const bar=document.getElementById('shared-id-controls-v122');const gd=document.querySelector('.plotly-graph-div');if(!gd){bar.textContent='ID controls: plot container not found. Regenerate this view.';return;}bar.innerHTML='<div class="viewer-main"><div class="viewer-heading"><strong>ETABS → OpenSees</strong><span>3D element inspector · display labels only</span></div><div class="viewer-members" role="group" aria-label="Member prefix and number"><label for="memberPrefix">Prefix</label><select id="memberPrefix" aria-label="Element classification"><option value="B">B · Beam</option><option value="C">C · Column</option><option value="BR">BR · Brace</option><option value="CO">CO · Core outrigger</option><option value="BT">BT · Belt truss</option><option value="CT">CT · Cap truss</option><option value="FVD">FVD · Damper</option><option value="BRB">BRB · Buckling-restrained brace</option><option value="SW">SW · Shear wall</option><option value="FL">FL · Floor</option></select><label for="memberStorey">Storey</label><select id="memberStorey" aria-label="Filter by storey"><option value="">All</option></select><label for="memberNumber">Element</label><select id="memberNumber" aria-label="Select member number"><option value="">Select element</option></select><button id="memberHighlight" type="button">Highlight</button><button id="memberFocus" type="button">Focus</button><span id="memberCount" class="viewer-count"></span></div><div class="viewer-camera" role="group" aria-label="3D camera"><button id="viewZoomIn" type="button" title="Zoom in">Zoom +</button><button id="viewZoomOut" type="button" title="Zoom out">Zoom −</button><button id="viewFit" type="button">Reset</button><select id="viewPreset" aria-label="Camera orientation"><option>Isometric</option><option>Top (+Z)</option><option>Bottom (-Z)</option><option>Front (-Y)</option><option>Back (+Y)</option><option>Right (+X)</option><option>Left (-X)</option></select></div></div><details class="viewer-advanced" id="viewerAdvanced"><summary>Exact source IDs · Node selection · Advanced</summary><div class="viewer-legacy"><select id="idKind" aria-label="ID namespace"><option value="object">ETABS element unique ID</option><option value="preview">OpenSees topology element tag</option><option value="solver">OpenSees assembled element tag</option><option value="point">ETABS point name</option><option value="node" selected>OpenSees node tag</option></select><input id="idValue" placeholder="Exact ID" aria-label="Exact identifier"><button id="idFind" type="button">Select exact ID</button><button id="idClear" type="button">Clear highlight</button><a href="OpenSees_Property_Element_Load_Audit_V125.xlsx">Excel audit</a><button id="viewZoomNode" type="button">Zoom to Node</button></div></details><div id="idResult" class="viewer-status" role="status" aria-live="polite">Choose a member prefix, storey and number.</div>';const is3d=gd.data.some(t=>t.type==='scatter3d'||t.type==='mesh3d');const floorEdges=gd.data.map((t,i)=>({t,i})).filter(o=>String(o.t.name||'').startsWith('FLOOR |')).map(o=>o.i);if(is3d&&floorEdges.length){const label=document.createElement('label');label.innerHTML='<input type="checkbox"> Slab outline overlay (display only)';bar.appendChild(label);const check=label.querySelector('input');check.onchange=()=>Plotly.restyle(gd,{opacity:check.checked?.35:0},floorEdges);check.onchange();}let zoom=1;function cameraZoom(factor){if(!is3d){const update={};['xaxis','yaxis'].forEach(k=>{const r=gd._fullLayout[k].range,c=(r[0]+r[1])/2,h=(r[1]-r[0])*factor/2;update[k+'.range']=[c-h,c+h]});Plotly.relayout(gd,update);return;}const eye=(gd.layout&&gd.layout.scene&&gd.layout.scene.camera&&gd.layout.scene.camera.eye)||{x:1.7,y:1.7,z:1.25};Plotly.relayout(gd,{'scene.camera.eye':{x:eye.x*factor,y:eye.y*factor,z:eye.z*factor}})}bar.querySelector('#viewZoomIn').onclick=()=>cameraZoom(.8);bar.querySelector('#viewZoomOut').onclick=()=>cameraZoom(1.25);bar.querySelector('#viewFit').onclick=()=>Plotly.relayout(gd,{'scene.camera.eye':{x:1.7,y:1.7,z:1.25},'scene.camera.center':{x:0,y:0,z:0}});const preset=bar.querySelector('#viewPreset');preset.onchange=()=>{const views={'Isometric':[1.7,1.7,1.25],'Top (+Z)':[0,0,2.7],'Bottom (-Z)':[0,0,-2.7],'Front (-Y)':[0,-2.7,0],'Back (+Y)':[0,2.7,0],'Right (+X)':[2.7,0,0],'Left (-X)':[-2.7,0,0]};const p=views[preset.value],up=p[0]===0&&p[1]===0?{x:0,y:1,z:0}:{x:0,y:0,z:1};Plotly.relayout(gd,{'scene.aspectmode':'data','scene.camera':{eye:{x:p[0],y:p[1],z:p[2]},up:up,center:{x:0,y:0,z:0},projection:{type:'orthographic'}}})};bar.querySelector('#viewFit').onclick=()=>{preset.value='Isometric';preset.onchange();Plotly.relayout(gd,{'scene.xaxis.autorange':true,'scene.yaxis.autorange':true,'scene.zaxis.autorange':true,'scene.aspectmode':'data'})};if(is3d){preset.onchange()}else{preset.disabled=true;bar.querySelector('#viewFit').onclick=()=>Plotly.relayout(gd,{'xaxis.autorange':true,'yaxis.autorange':true});}const category=document.createElement('select');category.id='selectionCategory';category.innerHTML='<option value="node">Node selection</option><option value="frame">Frame element selection</option><option value="area">Area selection</option>';bar.querySelector('#idKind').parentNode.insertBefore(category,bar.querySelector('#idKind'));const originalOptions=[...bar.querySelector('#idKind').options].map(o=>({value:o.value,text:o.text}));function setCategory(){const k=bar.querySelector('#idKind');k.innerHTML='';originalOptions.filter(o=>category.value==='node'?['node','point'].includes(o.value):['object','preview','solver'].includes(o.value)).forEach(o=>k.add(new Option(o.text,o.value)));bar.querySelector('#idValue').value='';bar.querySelector('#idResult').textContent='Choose '+category.value+' ID namespace and enter exact ID';}category.onchange=setCategory;setCategory();
const memberPrefix=bar.querySelector('#memberPrefix'),memberStorey=bar.querySelector('#memberStorey'),memberNumber=bar.querySelector('#memberNumber'),memberCount=bar.querySelector('#memberCount');
const memberCandidates=D.elements.map((e,index)=>({e,index})).filter(x=>['B','C','BR','CO','BT','CT','FVD','BRB','SW','FL'].includes(String(x.e.display_category||''))&&String(x.e.display_label||'').startsWith(String(x.e.display_category))&&x.e.display_label!=='UNCLASSIFIED_MEMBER');
function refreshMemberStoreys(){const previous=memberStorey.value,role=memberPrefix.value;const floors=[...new Set(memberCandidates.filter(x=>x.e.display_category===role).map(x=>String(x.e.storey_number)).filter(x=>/^\\d+$/.test(x)))].sort((a,b)=>Number(a)-Number(b));memberStorey.replaceChildren(new Option('All storeys',''),...floors.map(f=>new Option('Storey '+f,f)));if(floors.includes(previous))memberStorey.value=previous;refreshMemberNumbers();}
function refreshMemberNumbers(){const prior=memberNumber.value;const rows=memberCandidates.filter(x=>x.e.display_category===memberPrefix.value&&(!memberStorey.value||String(x.e.storey_number)===memberStorey.value)).sort((a,b)=>Number(a.e.storey_number)-Number(b.e.storey_number)||String(a.e.display_label).localeCompare(String(b.e.display_label),undefined,{numeric:true}));memberNumber.replaceChildren(new Option(rows.length?'Select element number':'No mapped members',''),...rows.map(x=>new Option(x.e.display_label+' · ETABS '+String(x.e.etabs_object),String(x.index))));if([...memberNumber.options].some(o=>o.value===prior&&prior))memberNumber.value=prior;else memberNumber.value='';memberNumber.disabled=!rows.length;memberCount.textContent=rows.length?rows.length+' mapped':memberPrefix.value+' has no source-verified members';bar.querySelector('#memberHighlight').disabled=!rows.length;bar.querySelector('#memberFocus').disabled=!rows.length;}
memberPrefix.onchange=()=>{memberStorey.value='';refreshMemberStoreys();};memberStorey.onchange=refreshMemberNumbers;
function selectedMember(){if(!memberNumber.value){bar.querySelector('#idResult').textContent='Choose an exact '+memberPrefix.value+' element number first.';return null;}const x=D.elements[Number(memberNumber.value)];if(!x||x.display_category!==memberPrefix.value){bar.querySelector('#idResult').textContent='Selection no longer matches this source export.';return null;}return x;}
function highlightMember(){const e=selectedMember();if(!e)return null;category.value=e.dimension==='line_2_node'?'frame':'area';setCategory();bar.querySelector('#idKind').value='object';bar.querySelector('#idValue').value=String(e.etabs_object);bar.querySelector('#idFind').click();bar.querySelector('#idResult').textContent=e.display_label+' | ETABS object '+e.etabs_object+' | topology '+e.element_tag+' | display name, not a solver tag';return e;}
bar.querySelector('#memberHighlight').onclick=highlightMember;
bar.querySelector('#memberFocus').onclick=()=>{const e=highlightMember();if(!e)return;const xyz=(e.node_tags||[]).map(n=>D.xyz[String(n)]).filter(p=>Array.isArray(p)&&p.length===3&&p.every(v=>Number.isFinite(Number(v))));if(!xyz.length){bar.querySelector('#idResult').textContent='No finite mapped coordinates for '+e.display_label;return;}const bounds=[0,1,2].map(axis=>{const vals=xyz.map(p=>Number(p[axis])),lo=Math.min(...vals),hi=Math.max(...vals),pad=Math.max(1,(hi-lo)*.25);return [lo-pad,hi+pad]});const v=is3d?{'scene.xaxis.range':bounds[0],'scene.yaxis.range':bounds[1],'scene.zaxis.range':bounds[2],'scene.aspectmode':'data'}:{'xaxis.range':bounds[0],'yaxis.range':bounds[1]};Plotly.relayout(gd,v);};
memberNumber.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();highlightMember();}};
refreshMemberStoreys();let overlay=null;function clear(){if(overlay!==null){Plotly.deleteTraces(gd,overlay);overlay=null}}bar.querySelector('#idClear').onclick=clear;bar.querySelector('#idFind').onclick=()=>{clear();let kind=bar.querySelector('#idKind').value,id=bar.querySelector('#idValue').value.trim(),coords=[],labels=[];if(kind==='node'||kind==='point'){D.nodes.filter(n=>String(kind==='node'?n.opensees_node_tag:n.etabs_point_name)===id).forEach(n=>{coords.push(n.coordinates_m);labels.push('ETABS point '+n.etabs_point_name+' / OpenSees node '+n.opensees_node_tag+' / '+n.display_label)})}else{D.elements.filter(e=>(category.value==='frame'?e.dimension==='line_2_node':e.dimension!=='line_2_node')).filter(e=>kind==='object'?String(e.etabs_object)===id:kind==='preview'?String(e.element_tag)===id:((e.dimension==='line_2_node'?D.assembled:D.assembled_area)[String(e.etabs_object)]||[]).map(String).includes(id)).forEach(e=>{let ns=e.node_tags||[];ns.forEach(n=>{coords.push(D.xyz[String(n)]);labels.push('ETABS '+e.etabs_object+' / topology '+e.element_tag+' / '+e.display_label)});if(ns.length>2){coords.push(D.xyz[String(ns[0])]);labels.push('ETABS '+e.etabs_object)}coords.push(null);labels.push('')})}bar.querySelector('#idResult').textContent=coords.filter(Boolean).length?' Highlighted matching source geometry':' No matching ID (solver tags require successful assembly)';if(!coords.filter(Boolean).length)return;overlay=gd.data.length;Plotly.addTraces(gd,{type:gd.data.some(t=>t.type==='scatter3d')?'scatter3d':'scatter',mode:'lines+markers',x:coords.map(p=>p?p[0]:null),y:coords.map(p=>p?p[1]:null),z:coords.map(p=>p?p[2]:null),text:labels,hovertemplate:'%{text}<extra></extra>',line:{color:'#ec008c',width:10},marker:{size:14,color:'#ffec00',symbol:'diamond',line:{color:'#9e0070',width:3}},name:'ID selection',showlegend:false})};// V161: center and zoom around an EXACT selected OpenSees/ETABS source node.
const zoomNodeBtn=bar.querySelector('#viewZoomNode');
zoomNodeBtn.onclick=()=>{
  if(!is3d){bar.querySelector('#idResult').textContent='Zoom to Node requires a 3D Plotly view';return;}
  if(category.value!=='node'){bar.querySelector('#idResult').textContent='Select Node selection first';return;}
  const kind=bar.querySelector('#idKind').value;
  const id=bar.querySelector('#idValue').value.trim();
  const matches=D.nodes.filter(n=>String(kind==='point'?n.etabs_point_name:n.opensees_node_tag)===id);
  if(matches.length!==1||!Array.isArray(matches[0].coordinates_m)){
    bar.querySelector('#idResult').textContent='Exactly one mapped source node required; check ID namespace';
    return;
  }
  const p=matches[0].coordinates_m.map(Number);
  if(p.length!==3||!p.every(Number.isFinite)){bar.querySelector('#idResult').textContent='Missing finite source-node coordinates';return;}
  const radius=6;
  // Geometry coordinates are in metres. Plotly uses axis ranges in model
  // units, avoiding camera-center normalization errors for 100 m buildings.
  const range=(value)=>[value-radius,value+radius];
  const update={'scene.xaxis.range':range(p[0]),
                'scene.yaxis.range':range(p[1]),
                'scene.zaxis.range':range(p[2]),
                'scene.aspectmode':'data',
                'scene.camera.eye':{x:1.55,y:1.55,z:1.2},
                'scene.camera.center':{x:0,y:0,z:0}};
  Promise.resolve(Plotly.relayout(gd,update)).then(()=>{
    bar.querySelector('#idResult').textContent=' Zoomed to '+(kind==='point'?'ETABS point ':'OpenSees node ')+id+' at ('+p.map(x=>x.toFixed(3)).join(', ')+') m';
  });
};
const query=new URLSearchParams(window.location.search);if(query.has('idValue')){category.value=['point','node'].includes(query.get('idKind')||'node')?'node':(query.get('category')||'frame');setCategory();bar.querySelector('#idKind').value=query.get('idKind')||'node';bar.querySelector('#idValue').value=query.get('idValue');bar.querySelector('#idFind').onclick();}});</script>""".replace('__DATA__',json.dumps(selector_data))
    import re
    for path in folder.glob('*.html'):
        content=path.read_text(encoding='utf-8-sig')
        if 'plotly-graph-div' not in content: continue
        content=re.sub(r'<script id="shared-id-selector-v121">.*?</script>','',content,flags=re.S)
        content=re.sub(r'<style id="shared-3d-viewer-style-v162">.*?</style>','',content,flags=re.S)
        # Render the controls container in HTML before the plot. It remains
        # visible while Plotly initializes, and startup failures are explicit.
        content=re.sub(r'<div id="shared-id-controls-v122"[^>]*>.*?</div>','',content,flags=re.S)
        viewer_css="<style id=\"shared-3d-viewer-style-v162\">\n#shared-id-controls-v122{display:block!important;position:sticky;top:0;z-index:30;padding:0!important;background:#f6f8fc!important;border-bottom:1px solid #cbd5e1;color:#17273f;font:13px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;box-shadow:0 2px 10px rgba(18,38,65,.08)}\n#shared-id-controls-v122 .viewer-main{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:8px 12px}\n#shared-id-controls-v122 .viewer-heading{display:flex;flex-direction:column;line-height:1.25;min-width:145px}\n#shared-id-controls-v122 .viewer-heading strong{font-size:13px;color:#162d50;letter-spacing:.01em}\n#shared-id-controls-v122 .viewer-heading span{font-size:11px;color:#53647d}\n#shared-id-controls-v122 .viewer-members,#shared-id-controls-v122 .viewer-camera,#shared-id-controls-v122 .viewer-legacy{display:flex;align-items:center;gap:6px;flex-wrap:wrap}\n#shared-id-controls-v122 .viewer-members{flex:1 1 500px}\n#shared-id-controls-v122 .viewer-camera{flex:0 1 auto}\n#shared-id-controls-v122 label{font-size:11px;font-weight:600;color:#425674}\n#shared-id-controls-v122 button,#shared-id-controls-v122 select,#shared-id-controls-v122 input{min-height:31px;box-sizing:border-box;border:1px solid #b7c5d8;background:white;color:#192f4d;border-radius:6px;padding:5px 8px;font:inherit}\n#shared-id-controls-v122 button{cursor:pointer;background:#e8effa;font-weight:600;white-space:nowrap}\n#shared-id-controls-v122 button:hover:not(:disabled){background:#d5e4fc;border-color:#729fd9}\n#shared-id-controls-v122 button:disabled,#shared-id-controls-v122 select:disabled{opacity:.52;cursor:not-allowed}\n#shared-id-controls-v122 button:focus-visible,#shared-id-controls-v122 select:focus-visible,#shared-id-controls-v122 input:focus-visible,#shared-id-controls-v122 summary:focus-visible{outline:3px solid #2762b3;outline-offset:2px}\n#shared-id-controls-v122 #memberPrefix{max-width:200px}\n#shared-id-controls-v122 #memberStorey{max-width:122px}\n#shared-id-controls-v122 #memberNumber{max-width:230px;min-width:135px}\n#shared-id-controls-v122 .viewer-count{font-size:11px;color:#475b78;font-variant-numeric:tabular-nums}\n#shared-id-controls-v122 .viewer-advanced{padding:0 12px 5px}\n#shared-id-controls-v122 .viewer-advanced summary{width:max-content;cursor:pointer;font-size:12px;color:#234a7b;padding:3px 0}\n#shared-id-controls-v122 .viewer-legacy{margin:6px 0 4px}\n#shared-id-controls-v122 .viewer-legacy a{color:#1d559e;text-decoration:underline;text-underline-offset:3px}\n#shared-id-controls-v122 .viewer-legacy input{width:132px}\n#shared-id-controls-v122 .viewer-status{padding:4px 12px 6px;min-height:22px;color:#405575;font-size:12px;border-top:1px solid #e3e9f1}\n@media(max-width:1024px){#shared-id-controls-v122 .viewer-main{align-items:flex-start}#shared-id-controls-v122 .viewer-members{flex-basis:100%}#shared-id-controls-v122 .viewer-camera{flex:1 1 100%}}\n@media(max-width:600px){#shared-id-controls-v122 .viewer-heading{width:100%}#shared-id-controls-v122 .viewer-members{gap:5px}#shared-id-controls-v122 #memberNumber{flex:1 1 145px;max-width:none}}\n</style>"
        container='<div id="shared-id-controls-v122">ETABS / OpenSees exact selection controls — initializing...</div>'
        content=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+viewer_css+container,content,count=1,flags=re.I)
        safe_script=script
        path.write_text(content.replace('</body>',safe_script+'</body>'),encoding='utf-8')
