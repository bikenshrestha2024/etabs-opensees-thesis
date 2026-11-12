"""Isolated FIRST-STOREY wall-mesh-panel OpenSeesPy diagnostic (NOT a full floor).

[REF R01 Kolozvari, Orakcal & Wallace (2015) PEER 2015/12 Appendix B.3]
[REF Kolozvari, Lopez & Massone (2023), DOI 10.1016/j.engstruct.2023.116700]
[REF https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html]

This model takes exactly one source-wall quadrilateral from the first storey,
NOT all columns, spandrels, openings, diaphragms, gravity load paths or frame
mass. It tests one element and its specimen-material implementation only.
No single-storey response is extrapolated to the full 25-storey building.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path


def select_first_storey_panel(data, *, property_name=None):
    """Select a 4-node planar wall quad at the lowest physical storey.

    [REF docs/source/components/nonlinear_time_history/one_storey_wall_probe.py.md]
    No synthetic coordinates, wall thickness or reinforcement schedule.
    Rejected geometry is not silently repaired by triangulation/remeshing.
    """
    xyz=data['nodes']
    candidates=[]
    for shell in data.get('shells',[]):
        if shell.get('category')!='SHEAR WALL':continue
        if property_name is not None and shell['properties'].get('property')!=property_name:continue
        tags=shell.get('nodes',[])
        if len(tags)!=4 or len(set(map(int,tags)))!=4:continue
        try:points=[tuple(map(float,xyz[str(n)])) for n in tags]
        except (KeyError,TypeError,ValueError):continue
        z_low=min(v[2] for v in points);z_high=max(v[2] for v in points)
        if z_high-z_low<=1.e-6:continue
        bottoms=[(int(n),p) for n,p in zip(tags,points) if abs(p[2]-z_low)<1.e-5]
        tops=[(int(n),p) for n,p in zip(tags,points) if abs(p[2]-z_high)<1.e-5]
        if len(bottoms)!=2 or len(tops)!=2:continue
        length_axis=(0 if max(p[0] for p in points)-min(p[0] for p in points)>
                     max(p[1] for p in points)-min(p[1] for p in points) else 1)
        cross_axis=1-length_axis
        if max(p[cross_axis] for p in points)-min(p[cross_axis] for p in points)>1.e-5:
            continue
        bottoms.sort(key=lambda x:x[1][length_axis])
        tops.sort(key=lambda x:x[1][length_axis])
        width=bottoms[-1][1][length_axis]-bottoms[0][1][length_axis]
        if width<=1.e-5:continue
        if any(abs(tops[i][1][length_axis]-bottoms[i][1][length_axis])>1.e-4
               for i in range(2)):continue
        thickness=float(shell['properties']['thickness'])
        if not math.isfinite(thickness) or thickness<=0:continue
        # CCW order when looking along wall normal: bottom-left, bottom-right,
        # top-right, top-left. Original node IDs are kept in provenance.
        order=[bottoms[0],bottoms[1],tops[1],tops[0]]
        candidates.append(dict(property=shell['properties']['property'],
            source_tag=shell.get('tag',shell.get('id')),
            tags=[n for n,_ in order],original_coordinates=[p for _,p in order],
            width_m=width,height_m=z_high-z_low,thickness_m=thickness,
            horizontal_axis='X' if length_axis==0 else 'Y',
            base_elevation_m=z_low,upper_elevation_m=z_high))
    if not candidates:raise ValueError(
        'No eligible first-storey 4-node wall quadrilateral. Inspect SHEAR WALL shell '
        'tags, shared node coordinates and mesh; do not invent a replacement panel.')
    candidates.sort(key=lambda c:(c['base_elevation_m'],c['upper_elevation_m'],
                                  str(c['property']),str(c['tags'])))
    return candidates[0]


def prepare(source_folder, output_folder, *, property_name=None):
    """Write source-hashed geometry and PEER material provenance without approval.

    [REF R01 PEER 2015/12 Appendix B.3; docs/source/components/nonlinear_time_history/one_storey_wall_probe.py.md]
    """
    from components.nonlinear_time_history.material_source_sets import peer_single_source
    source=Path(source_folder).resolve()
    output=Path(output_folder).resolve()
    source_file=source/'OpenSees_Complete_Model_Data_V118.json'
    if not source_file.is_file():raise FileNotFoundError(source_file)
    if output==source or output==source.parent:
        raise ValueError('Diagnostic output must be separate from the source model folder')
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('One-storey diagnostic output must be a new empty folder: '+str(output))
    raw=source_file.read_bytes()
    panel=select_first_storey_panel(json.loads(raw.decode('utf-8-sig')),
                                    property_name=property_name)
    peer=peer_single_source()
    report=dict(status='PREPARED_NOT_RUN',scope='ONE_SOURCE_FIRST_STOREY_WALL_QUAD',
        original_model_sha256=hashlib.sha256(raw).hexdigest(),
        panel=panel,material_basis='PEER_2015_12_SINGLE_SOURCE',
        concrete=peer['wall_concrete'],steel=peer['wall_steel'],fsam=peer['fsam'],
        material_source_table=peer['rows'],specimen=peer['specimen'],
        source=peer['source'],source_locator='PEER 2015/12 Appendix B.3',
        element_source='https://doi.org/10.1016/j.engstruct.2023.116700',
        warnings=[
          'One shell is NOT the entire first storey: adjacent shell continuity, piers, '
          'coupling beams, frame stiffness, columns, mass, accidental torsion and '
          'gravity flow are intentionally omitted.',
          'The PEER specimen concrete and steel are NOT calibrated to project M30/Fe500.',
          'FSAM rho_x/rho_y are research specimen/patch assumptions, not ETABS reinforcement.',
          'No axial-load/initial P-Delta, cyclic degradation or earthquake record is modeled.',
          'The E-SFI model comes from a 2023 element paper; not the 2015 material paper.',
        ])
    output.mkdir(parents=True,exist_ok=True)
    path=output/'One_Storey_Wall_Probe_Inputs.json'
    path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    return path


def run(source_folder, output_folder, *, property_name=None):
    """Attempt small-load first-storey quad smoke test using real OpenSeesPy.

    [REF OpenSees E_SFI_MVLEM_3D command, DOI 10.1016/j.engstruct.2023.116700]
    Solver or element failure produces FAILED evidence, never invented PASS.
    """
    path=prepare(source_folder,output_folder,property_name=property_name)
    data=json.loads(path.read_text(encoding='utf-8'))
    out=Path(output_folder)
    try:
        import openseespy.opensees as ops
        from components.validation.parameter_studies import CM,MPF
        ops.wipe()
        ops.model('basic','-ndm',3,'-ndf',6)
        panel=data['panel']
        original=panel['original_coordinates']
        origin=original[0]
        for n,xyz in enumerate(original,1):
            ops.node(n,*[x-y for x,y in zip(xyz,origin)])
        # First-storey wall base fixed; upper nodes remain free. These are
        # chosen boundary assumptions for the QUAD only, not ETABS foundations.
        for n in (1,2):ops.fix(n,1,1,1,1,1,1)
        s=data['steel'];c=data['concrete'];f=data['fsam']
        ops.uniaxialMaterial('SteelMPF',11,*[
            s[k]*(1000. if k in ('fyp','fyn','E0') else 1.) for k in MPF])
        ops.uniaxialMaterial('ConcreteCM',12,*[
            c[k]*(1000. if k in ('fpcc','Ec','ft') else 1.) for k in CM])
        for tag in (13,14):
            ops.nDMaterial('FSAM',tag,0.,11,11,12,
                            float(f.get('rho_x',.0074)),float(f.get('rho_y',.0074)),
                            float(f['nu']),float(f['alpha']))
        w=float(panel['width_m']);t=float(panel['thickness_m'])
        ops.element('E_SFI_MVLEM_3D',21,1,2,3,4,2,
                    '-thick',t,t,'-width',w/2,w/2,'-mat',13,14,
                    '-CoR',0.4,'-ThickMod',0.63,'-Poisson',float(f['nu']))
        axis=1 if panel['horizontal_axis']=='X' else 2
        ops.timeSeries('Linear',1);ops.pattern('Plain',1,1)
        # Unit load only; this is a deterministic tangent/implementation check,
        # NOT a source-calibrated load history or design lateral demand.
        ops.load(3,*(1. if i==axis-1 else 0. for i in range(3)),0.,0.,0.)
        ops.load(4,*(1. if i==axis-1 else 0. for i in range(3)),0.,0.,0.)
        ops.constraints('Transformation');ops.numberer('RCM')
        ops.system('UmfPack');ops.test('NormDispIncr',1.e-9,50)
        ops.algorithm('Newton');ops.integrator('LoadControl',0.1)
        ops.analysis('Static')
        response=[]
        for step in range(1,11):
            rc=ops.analyze(1)
            if rc!=0:raise RuntimeError('Static probe nonconverged at increment '+str(step))
            value=float(ops.nodeDisp(3,axis))
            if not math.isfinite(value):
                raise FloatingPointError('Nonfinite wall-panel displacement')
            response.append(dict(step=step,applied_lateral_kN=step*.2,
                                 upper_node_displacement_m=value))
        data.update(status='NUMERICAL_PROBE_COMPLETE_NOT_PROJECT_VALIDATED',
                    response=response,units='kN–m–s',kind='monotonic small-load panel smoke test')
    except Exception as exc:
        data.update(status='FAILED',error_type=type(exc).__name__,error=str(exc))
    finally:
        try:ops.wipe()
        except (NameError,Exception):pass
    result=out/'One_Storey_Wall_Probe_Result.json'
    result.write_text(json.dumps(data,indent=2),encoding='utf-8')
    return result


def main():
    parser=argparse.ArgumentParser(description='Single source first-storey wall QUAD diagnostic; research only')
    parser.add_argument('--source',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--property',default=None)
    args=parser.parse_args()
    result=run(args.source,args.output,property_name=args.property)
    print('[ONE_STOREY_WALL_PROBE]',result,flush=True)
    status=json.loads(result.read_text(encoding='utf-8'))['status']
    print('[PROBE STATUS]',status,flush=True)
    if status=='FAILED':raise SystemExit(1)


if __name__=='__main__':
    main()
