"""Saved response inventory. Missing design capacities remain explicit."""
from pathlib import Path
import json,math

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))

def available_response_rows(folder):
 """[REF docs/source/components/validation/response_inventory.py.md]
 Read compatible saved responses from canonical and historical roots.

 An inventory is not structural acceptance; saved load case, support, source
 model hash and units still require engineering comparison before design.
 """
 from components.inputs.output_layout import result_roots
 roots=result_roots(folder, stages=("GRAVITY","ESM","MRSM","LTHA","NLTHA"))
 deflections=[]
 actions=[]
 seen=set()
 def eligible(path):
  return not any(part.casefold() in {
      "review_snapshots","organized_results","zip_exports","zip_exports",
      "gravity_evidence_upload"} for part in path.parts)
 for root in roots:
  for gravity in sorted(root.rglob('Gravity_Result_V110.json')):
   if not eligible(gravity) or gravity.resolve() in seen:continue
   seen.add(gravity.resolve())
   try:
    d=read(gravity)
    nodes=d.get('nodes',[])
    for z in sorted(set(round(n['z_m'],6) for n in nodes)):
     level=[n for n in nodes if abs(n['z_m']-z)<1e-5]
     critical=min(level,key=lambda n:n['uz_m'])
     deflections.append(dict(limit_state='AS_CONFIGURED',case='Gravity preload',
         member='NODE:'+str(critical['tag']),check='Recorded total vertical displacement',
         demand=abs(critical['uz_m']),limit=None,unit='m',status='LIMIT REQUIRED',
         reason='Total displacement, not beam chord-relative or long-term deflection. Confirm source model/support/load identity; project limit required.',
         result_file=str(gravity)))
    for row in d.get('local_forces',[]):
     actions.append(dict(limit_state='AS_CONFIGURED',case='Gravity preload',
         member='ELEMENT:'+str(row['tag']),check='Concurrent local end actions available',
         status='CAPACITY REQUIRED',
         reason='Not a DL-only basis or ULS/SLS design combination. Verify source model, support case, reinforcement and section capacity.',
         result_file=str(gravity),**{k:v for k,v in row.items() if k!='tag'}))
   except (ValueError,TypeError,KeyError):
    # Unknown or stale file must not produce invented results.
    continue
  for p in sorted(root.rglob('Deformation_*.json')):
   if not eligible(p) or p.resolve() in seen:continue
   seen.add(p.resolve())
   try:
    d=read(p)
    state=d.get('limit_state') or ('ULS' if '_ULS_' in p.name else 'SLS' if '_SLS_' in p.name else 'UNKNOWN')
    values=[(n,u) for n,u in d.get('displacements',{}).items()
            if len(u)>=2 and all(math.isfinite(float(v)) for v in u[:2])]
    for j,axis in [(0,'X'),(1,'Y')]:
     if values:
      n,u=max(values,key=lambda pair:abs(float(pair[1][j])))
      deflections.append(dict(limit_state=state,case=p.stem,member='NODE:'+str(n),
          check='Saved displacement '+axis,demand=abs(float(u[j])),
          limit=None,unit='m',status='LIMIT REQUIRED',
          reason=str(d.get('note',''))+' | Model SHA and case provenance must be reviewed; do not combine mismatched cases.',
          result_file=str(p)))
   except (ValueError,KeyError,TypeError,OverflowError):
    continue
 return deflections,actions
