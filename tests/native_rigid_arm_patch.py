"""Synthetic native rigid-arm Timoshenko component benchmark.

First-order response compared with independent full-span axial/torsional and
clear-span bending/shear compliance. Compression is a separate geometric
nonlinear sensitivity check, not an ETABS P-Delta equivalence test.
Run python -m tests.native_rigid_arm_patch native_rigid_arm_results.
"""
import argparse
import json
import math
from pathlib import Path
import subprocess


def run_case(root, executable, name, L, a, b, action, compression=0.,force_based=False):
    E,G,A,J,Iy,Iz,Ay,Az=30e6,12.5e6,.48,.03,.02,.01,.4,.35
    ell=L-a-b
    # Rigid arms preserve full-length axial and torsional compliance.
    scale=ell/L
    load=list(action)
    load[0]-=compression
    folder=root/name
    folder.mkdir()
    kind="PDelta" if compression else "Linear"
    geom=" -geomNonlinear" if compression else ""
    lines=["wipe","model BasicBuilder -ndm 3 -ndf 6",
           "node 1 0 0 0",f"node 4 {L} 0 0","fix 1 1 1 1 1 1 1"]
    if force_based:
        from components.model.elastic_conversion_settings import elastic_offset_force_beam
        # Tcl expresses the same Lobatto integration inline rather than
        # through the separate Python beamIntegration command.
        class Tcl:
            def section(self,*args):
                lines.append("section "+" ".join(map(str,args)))
            def beamIntegration(self,*args):
                self.integration=args
            def element(self,*args):
                lines.append("element "+" ".join(map(str,(*args[:5],self.integration[0],
                              *self.integration[2:],*args[6:]))))
        lines.append(f"geomTransf PDelta 1 0 0 1 -jntOffset {a} 0 0 {-b} 0 0")
        elastic_offset_force_beam(Tcl(),1,[1,4],E,G,
            dict(A=A*scale,J=J*scale,Iy=Iy,Iz=Iz,As2=Ay,As3=Az),1)
    else:
        lines.extend([f"node 2 {a} 0 0",f"node 3 {L-b} 0 0",
                      "rigidLink beam 1 2","rigidLink beam 4 3",
                      f"geomTransf {kind} 1 0 0 1",
                      f"element ElasticTimoshenkoBeam 1 2 3 {E} {G} {A*scale} {J*scale} {Iy} {Iz} {Ay} {Az} 1{geom}"])
    lines.extend(["timeSeries Linear 1","pattern Plain 1 1 {",
           "load 4 "+" ".join(map(str,load)),"}",
           "constraints Transformation","numberer RCM","system FullGeneral",
           "test NormDispIncr 1e-11 50","algorithm Newton",
           "integrator LoadControl 0.1","analysis Static",
           "if {[analyze 10] != 0} {error {native analysis failed}}",
           "reactions","set f [open response.txt w]",
           "puts $f [nodeDisp 4]","puts $f [nodeReaction 1]",
           "puts $f {0 0 0 0 0 0}" if force_based else "puts $f [nodeReaction 2]",
           "puts $f [eleResponse 1 forces]",
           "close $f","puts [version]","exit 0"])
    script=folder/"case.tcl"
    script.write_text("\n".join(lines)+"\n")
    run=subprocess.run([executable,str(script.resolve())],cwd=folder,
                       text=True,capture_output=True,timeout=90)
    (folder/"solver.log").write_text(run.stdout+"\n"+run.stderr)
    if run.returncode:
        raise RuntimeError(f"Native solver failed: {name}")
    data=[list(map(float,row.split())) for row in
          (folder/"response.txt").read_text().splitlines()]
    if [len(row) for row in data]!=[6,6,6,12] or not all(
            math.isfinite(x) for row in data for x in row):
        raise ValueError("Invalid native response")
    u,reaction,slave,ends=data
    # Both the slave reaction and member-end force are at x=a.
    # M_origin = M_node + r cross F; never add the two representations.
    def to_origin(v):
        fx,fy,fz,mx,my,mz=v
        return [fx,fy,fz,mx,my-a*fz,mz+a*fy]
    recovered=[x+y for x,y in zip(reaction,to_origin(slave))]
    element_cut=ends[:6] if force_based else to_origin(ends[:6])
    if not compression:
        fx,fy,fz,mx,my,mz=action
        # Local x along the member, z axis from the transform.
        cy=(ell**3/3+b*ell**2+b*b*ell)/(E*Iz)+ell/(G*Ay)
        cz=(ell**3/3+b*ell**2+b*b*ell)/(E*Iy)+ell/(G*Az)
        dy=(ell**2/2+b*ell)/(E*Iz)
        dz=(ell**2/2+b*ell)/(E*Iy)
        expected=[fx*L/(E*A),fy*cy+mz*dy,fz*cz-my*dz,
                  mx*L/(G*J),my*ell/(E*Iy)-fz*dz,
                  mz*ell/(E*Iz)+fy*dy]
        expected_r=[-fx,-fy,-fz,-mx,-my+L*fz,-mz-L*fy]
        error=max(abs(v-w) for v,w in zip(u,expected))/max(1e-15,max(map(abs,expected)))
        # The native element cut is independent of nodeReaction recovery.
        # Compare both with equilibrium; retain raw master/slave records.
        reaction_residual=max(abs(v-w) for v,w in zip(reaction,expected_r))
        recovered_residual=max(abs(v-w) for v,w in zip(recovered,expected_r))
        cut_residual=max(abs(v-w) for v,w in zip(element_cut,expected_r))
        if max(recovered_residual,cut_residual)>1e-7:
            raise AssertionError(f"{name}: MPC/cut resultant mismatch: {recovered}, {element_cut}, {expected_r}")
        if error>1e-7:
            raise AssertionError(f"{name}: relative compliance mismatch {error}; actual={u}; expected={expected}")
        return dict(case=name,displacements=u,expected_displacements=expected,
                    max_relative_compliance_residual=error,
                    raw_support_reaction=reaction,raw_slave_reaction=slave,
                    expected_resultant=expected_r,
                    raw_support_reaction_residual=reaction_residual,
                    recovered_support_resultant=recovered,independent_element_cut=element_cut,
                    recovered_support_residual=recovered_residual,element_cut_residual=cut_residual)
    return dict(case=name,displacements=u,raw_support_reaction=reaction,
                raw_slave_reaction=slave,recovered_support_resultant=recovered,
                independent_element_cut=element_cut,
                compression_kN=compression,status="GEOMETRIC_NONLINEAR_SENSITIVITY_ONLY")


def mixed_frame_shell_cut(root, executable):
    """Actual first-order mixed shell/frame solve, all six cut components."""
    from components.gravity.load_path_formulas import recovered_interface_resultants
    folder=root/"mixed_frame_shell_cut";folder.mkdir()
    xyz={1:(0,0,0),2:(2,0,0),3:(2,0,3),4:(0,0,3)}
    elems={100001:[1,4],100002:[2,3],100003:[1,2,3,4]}
    loads={3:[2,3,-10,.1,.2,.3],4:[4,-1,-20,.4,.5,.6]}
    lines=["wipe","model BasicBuilder -ndm 3 -ndf 6"]
    for n,pos in xyz.items():lines.append("node "+ " ".join(map(str,(n,*pos))))
    lines+=["fix 1 1 1 1 1 1 1","fix 2 1 1 1 1 1 1",
            "section ElasticMembranePlateSection 1 30000000 0.2 0.3 0",
            "element ShellMITC4 100003 1 2 3 4 1",
            "geomTransf Linear 1 0 1 0",
            "element elasticBeamColumn 100001 1 4 .25 30000000 12500000 .01 .01 .01 1",
            "element elasticBeamColumn 100002 2 3 .25 30000000 12500000 .01 .01 .01 1",
            "timeSeries Linear 1","pattern Plain 1 1 {"]
    for n,v in loads.items():lines.append("load "+ " ".join(map(str,(n,*v))))
    lines+=["}","constraints Plain","numberer RCM","system FullGeneral",
            "test NormDispIncr 1e-10 20","algorithm Linear","integrator LoadControl 1",
            "analysis Static","if {[analyze 1] != 0} {error {mixed cut solve failed}}",
            "reactions","set f [open response.txt w]"]
    for n in (1,2):lines.append(f"puts $f [nodeReaction {n}]")
    for e in elems:lines.append(f"puts $f [eleResponse {e} forces]")
    lines+=["close $f","set mesh [open mesh.txt w]",
            'foreach n [getNodeTags] {puts $mesh "node $n [nodeCoord $n]"}',
            'foreach e [getEleTags] {puts $mesh "element $e [eleNodes $e]"}',
            "close $mesh","exit 0"]
    script=folder/"case.tcl";script.write_text("\n".join(lines)+"\n")
    run=subprocess.run([executable,str(script.resolve())],cwd=folder,
                       capture_output=True,text=True,timeout=90)
    (folder/"solver.log").write_text(run.stdout+"\n"+run.stderr)
    if run.returncode:raise RuntimeError("Native mixed cut solve failed")
    rows=[list(map(float,l.split())) for l in (folder/"response.txt").read_text().splitlines()]
    if [len(x) for x in rows]!=[6,6,12,12,24]:
        raise ValueError("Unexpected native mixed response shape")
    actual_nodes={}; actual_elements={}
    for row in (folder/"mesh.txt").read_text().splitlines():
        kind,tag,*values=row.split(); tag=int(tag)
        target=actual_nodes if kind=="node" else actual_elements if kind=="element" else None
        if target is None or tag in target:raise ValueError("Invalid native topology record")
        target[tag]=tuple(map(float,values)) if kind=="node" else list(map(int,values))
    if actual_nodes!=xyz or actual_elements!=elems:
        raise ValueError("Native topology differs from the specified test model")
    keys=("rx_kN","ry_kN","rz_kN","mx_kNm","my_kNm","mz_kNm")
    payload=dict(ok=True, support_node_tags=[1,2],
        nodes=[dict(tag=n,x_m=p[0],y_m=p[1],z_m=p[2]) for n,p in actual_nodes.items()],
        elements=[dict(tag=e,nodes=ns) for e,ns in actual_elements.items()],
        reactions=[dict(node_tag=n,**dict(zip(keys,v))) for n,v in zip((1,2),rows[:2])],
        global_end_forces=[dict(tag=e,nodes=ns,forces=v) for (e,ns),v in zip(elems.items(),rows[2:])])
    labels=[dict(tag=e,nodes=ns,category="SHEAR WALL" if e==100003 else "COLUMN",object=str(e))
            for e,ns in elems.items()]
    report=recovered_interface_resultants(payload,[0,3],loads,source_elements=labels)
    cut=report["interfaces"][0]
    error=max(map(abs,cut["lower_free_body_residual"]+cut["upper_free_body_residual"]))
    if error>1e-7:
        raise AssertionError(f"Native mixed cut equilibrium mismatch: {cut}")
    report["maximum_native_mixed_cut_component_residual"]=error
    # The comparison source is a deliberately synthetic reference fixture,
    # NOT a native CSI export. The other side is actual solved OpenSees
    # connectivity queried above, through the production comparison helper.
    from components.validation.etabs_native_quantity_tables import compare_analytical_mesh
    reference=dict(schema="etabs-analytical-mesh-native-v1",units="kN,m,C",
        points=[dict(id=str(n),xyz_m=p) for n,p in xyz.items()],
        elements=[dict(kind="AREA_ELM" if e==100003 else "LINE_ELM",
                       id=str(e),points=list(map(str,ns)),source_object=dict(name=str(e)))
                  for e,ns in elems.items()])
    domain=dict(frames=[dict(object=str(e),nodes=elems[e]) for e in (100001,100002)],
                shells=[dict(object="100003",nodes=elems[100003])])
    exact=compare_analytical_mesh(reference,payload,domain)
    if exact["matched_elements"]!=3 or exact["matched_points"]!=4:
        raise AssertionError("Actual native solved connectivity comparison failed")
    reference["points"] += [dict(id="5",xyz_m=(1,0,0)),dict(id="6",xyz_m=(1,0,3))]
    reference["elements"]=reference["elements"][:2]+[
        dict(kind="AREA_ELM",id="a",points=["1","5","6","4"],source_object=dict(name="100003")),
        dict(kind="AREA_ELM",id="b",points=["5","2","3","6"],source_object=dict(name="100003"))]
    refined=compare_analytical_mesh(reference,payload,domain)
    if (refined["matched_elements"]!=2 or
        refined["geometry_coverage_counts"]!={"GEOMETRIC_COVERAGE_MATCHED_DIAGNOSTIC":3}):
        raise AssertionError("Refined synthetic reference coverage mismatch")
    report["mesh_comparison"]=dict(reference="SYNTHETIC_NOT_CSI_NATIVE",
                                   exact=exact,refined=refined)
    print(json.dumps(dict(native_mesh_exact_elements=exact["matched_elements"],
                          native_mesh_exact_points=exact["matched_points"],
                          refined_reference_exact_elements=refined["matched_elements"],
                          refined_geometry_coverage=refined["geometry_coverage_counts"])),flush=True)
    (folder/"summary.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(native_mixed_cut_residual=error,cut=cut)),flush=True)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output",type=Path)
    p.add_argument("--opensees",default="OpenSees")
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    rows=[]
    for L,a,b in ((6.,.55,.625),(3.8,.0,.8)):
        # Zero-offset end still has a coincident MPC slave; explicit
        # rigidLink tests the same transform, without artificial stiffness.
        for i in range(6):
            load=[0.]*6
            load[i]=10.
            row=run_case(args.output,args.opensees,f"L{L}_dof{i+1}",L,a,b,load)
            rows.append(row)
            print(json.dumps(row),flush=True)
    force_rows=[]
    for L,a,b in ((6.,.55,.625),(3.8,0.,.8)):
        for i in range(6):
            load=[0.]*6;load[i]=10.
            row=run_case(args.output,args.opensees,f"force_L{L}_dof{i+1}",
                         L,a,b,load,force_based=True)
            force_rows.append(row)
            print(json.dumps(row),flush=True)
    force_probe=run_case(args.output,args.opensees,"force_compressed_probe",
                         6.,.55,.625,[0,10,0,0,0,0],1000.,force_based=True)
    force_probe["lateral_displacement_ratio_to_linear"]=force_probe["displacements"][1]/force_rows[1]["displacements"][1]
    print(json.dumps(force_probe),flush=True)
    base=rows[1]["displacements"][1]
    nonlinear=run_case(args.output,args.opensees,"compressed_column_probe",6.,.55,.625,[0,10,0,0,0,0],1000.)
    nonlinear["lateral_displacement_ratio_to_linear"]=nonlinear["displacements"][1]/base
    print(json.dumps(nonlinear),flush=True)
    mixed=mixed_frame_shell_cut(args.output,args.opensees)
    (args.output/"summary.json").write_text(json.dumps(dict(
        status="NATIVE_FIRST_ORDER_COMPLIANCE_PASSED_NOT_ETABS_EQUIVALENCE",
        checks=rows,compression_probe=nonlinear,
        force_based_checks=force_rows,force_based_compression_probe=force_probe,
        mixed_frame_shell_cut=mixed,
        limitation="RigidLink small-displacement kinematics; compression probe is diagnostic, no native ETABS section-cut or P-Delta benchmark."),
        indent=2))


if __name__=="__main__":
    main()
