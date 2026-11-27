"""Native OpenSees Tcl component qualification; no project model data.

Run from repository root:
    python -m tests.native_layered_shell_patch native_layered_shell_results
The same candidate registration helper is used via a Tcl command adapter.
No production shell, supports, gravity or nonlinear material is changed.
"""
import argparse
import json
import math
from pathlib import Path
import subprocess

from components.model.linear_shell_stiffness import (
    layered_elastic_candidate, layered_elastic_candidate_command)


class TclCommands:
    def __init__(self):
        self.lines=[]
    def nDMaterial(self,*args):
        self.lines.append("nDMaterial "+" ".join(map(str,args)))
    def section(self,*args):
        self.lines.append("section "+" ".join(map(str,args)))


def patch(root, executable, candidate, mode, mesh):
    # Prescribed kinematic fields; strains and stresses are read from all
    # Gauss points, not assumed from the input field. Pure modes can contain
    # compatible parasitic shear from interpolation, so check full tangent.
    amplitude=1e-4
    def field(x,y):
        a=amplitude
        return {
            "extension_x":(a*x,0,0,0,0,0),
            "extension_y":(0,a*y,0,0,0,0),
            "membrane_shear":(a*y,0,0,0,0,0),
            "bending_x":(0,0,0,0,a*x,0),
            "bending_y":(0,0,0,a*y,0,0),
            "twisting":(0,0,0,0,a*y,0),
            "shear_x":(0,0,a*x,0,0,0),
            "shear_y":(0,0,a*y,0,0,0),
            "translation":(a,a,a,0,0,0),
            "rotation_z":(-a*y,a*x,0,0,0,a),
        }[mode]
    tag=lambda i,j: 1+i+(mesh+1)*j
    commands=TclCommands()
    layered_elastic_candidate_command(commands,1,range(1,7),candidate)
    lines=["wipe","model BasicBuilder -ndm 3 -ndf 6",*commands.lines]
    for j in range(mesh+1):
        for i in range(mesh+1):
            lines.append(f"node {tag(i,j)} {i/mesh} {j/mesh} 0")
    elements=[]
    for j in range(mesh):
        for i in range(mesh):
            e=len(elements)+1
            elements.append(e)
            lines.append(f"element ShellMITC4 {e} {tag(i,j)} {tag(i+1,j)} {tag(i+1,j+1)} {tag(i,j+1)} 1")
    lines.extend(["timeSeries Linear 1","pattern Plain 1 1 {"])
    for j in range(mesh+1):
        for i in range(mesh+1):
            for dof,value in enumerate(field(i/mesh,j/mesh),1):
                lines.append(f"sp {tag(i,j)} {dof} {value:.17g}")
    lines.extend(["}","constraints Penalty 1e15 1e15","numberer Plain",
                  "system FullGeneral","test NormDispIncr 1e-10 20",
                  "algorithm Linear","integrator LoadControl 1","analysis Static",
                  "if {[analyze 1] != 0} {error {patch failed}}",
                  "set f [open response.txt w]"])
    for e in elements:
        lines.extend([f'puts $f [eleResponse {e} strains]',
                      f'puts $f [eleResponse {e} stresses]'])
    lines.extend(["close $f","puts [version]","exit 0"])
    folder=root/f"{mode}_{mesh}"
    folder.mkdir()
    script=folder/"patch.tcl"
    script.write_text("\n".join(lines)+"\n",encoding="utf8")
    result=subprocess.run([executable,str(script.resolve())],cwd=folder,
                          capture_output=True,text=True,timeout=90)
    (folder/"solver.log").write_text(result.stdout+"\n"+result.stderr,encoding="utf8")
    if result.returncode:
        raise RuntimeError(f"Native patch failed: {folder} ({result.returncode})")
    data=[list(map(float,line.split())) for line in
          (folder/"response.txt").read_text().splitlines()]
    if len(data)!=2*len(elements) or any(len(row)!=32 for row in data):
        raise ValueError("Missing native section response")
    A,D=candidate["A"],candidate["D"]
    K=candidate["transverse_shear_kN_m"]
    scale=[A[i][i] for i in range(3)]+[D[i][i] for i in range(3)]+[K,K]
    errors=[];excited=[0.]*8
    for strains,stresses in zip(data[::2],data[1::2]):
        for offset in range(0,32,8):
            u=strains[offset:offset+8];s=stresses[offset:offset+8]
            if not all(math.isfinite(v) for v in u+s):
                raise ValueError("Nonfinite native response")
            expected=[sum(A[i][j]*u[j] for j in range(3)) for i in range(3)]
            expected.extend(-sum(D[i][j]*u[3+j] for j in range(3)) for i in range(3))
            expected.extend(K*u[i] for i in (6,7))
            errors.extend(abs(x-y)/(k*amplitude) for x,y,k in zip(s,expected,scale))
            excited=[max(x,abs(y)) for x,y in zip(excited,u)]
    maximum=max(errors)
    if maximum>1e-5:
        raise AssertionError(f"Section response mismatch {mode}: {maximum}")
    expected_index={"extension_x":0,"extension_y":1,"membrane_shear":2,
                    "bending_x":3,"bending_y":4,"twisting":5,
                    "shear_x":6,"shear_y":7}.get(mode)
    if expected_index is not None and excited[expected_index]<amplitude*.1:
        raise AssertionError(f"Target section mode not excited: {mode} {excited}")
    if expected_index is None and max(excited)>amplitude*1e-4:
        raise AssertionError(f"Rigid motion generated strain: {mode} {excited}")
    return dict(mode=mode,mesh=mesh,max_normalized_constitutive_residual=maximum,
                max_abs_section_strains=excited,gauss_points=len(elements)*4,
                solver_returncode=result.returncode)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output",type=Path)
    p.add_argument("--opensees",default="OpenSees")
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    mods=dict(f11=.5,f22=.5,f12=.5,m11=.1,m22=.1,m12=.1,
              v13=1.,v23=1.,mass=1.,weight=1.)
    # Generic component values only; no uploaded model exported to CI.
    candidate=layered_elastic_candidate(30e6,.2,.6,mods,
                                      property_name="Synthetic shell",
                                      shear_correction=1.)
    results=[]
    for mesh in (1,2,4):
        for mode in ("extension_x","extension_y","membrane_shear","bending_x",
                     "bending_y","twisting","shear_x","shear_y",
                     "translation","rotation_z"):
            row=patch(args.output,args.opensees,candidate,mode,mesh)
            results.append(row)
            print(json.dumps(row),flush=True)
    report=dict(status="NATIVE_CONSTITUTIVE_PATCH_PASSED_NOT_ETABS_EQUIVALENCE",
                candidate=candidate,checks=results,
                limitation="Prescribed fields across meshes; not a loaded-plate convergence study, P-Delta, nonlinear or native CSI comparison.")
    (args.output/"summary.json").write_text(json.dumps(report,indent=2),encoding="utf8")


if __name__=="__main__":
    main()
