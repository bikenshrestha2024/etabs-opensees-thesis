#!/usr/bin/env python3
"""Independent ETABS/OpenSeesPy benchmark studio. No network, no repository mutation.

CLI:
  python ETABS_OpenSees_Verification_Studio.py --self-test
  python ETABS_OpenSees_Verification_Studio.py --run-all --output OUTPUT
  python ETABS_OpenSees_Verification_Studio.py --worker case_id --output OUTPUT --tolerance 0.01
GUI: python ETABS_OpenSees_Verification_Studio.py
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import html
import json
import math
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import traceback
import uuid

APP_VERSION = '2.1.0-single-file'
GRAVITY = 9.81  # NBC 105:2025 p. 7; standalone copy of components.nbc105.constants.GRAVITY_M_S2
CASES = [
 ('B01', 'CSI Example 01, Case II — propped beam', 'STATIC FRAME', 'Published CSI reaction and moment (component benchmark)'),
 ('B02', 'Beam subdivision invariance — 1/2/4/8 segments', 'FEM CONNECTIVITY', 'Derived Euler-Bernoulli analytic benchmark'),
 ('B03', 'Axial truss — closed-form solution', 'BRACE / UNITS', 'Derived from axial EA/L element theory, not a CSI example'),
 ('B04', 'ShellMITC4 wall — gravity equilibrium / mesh series', 'WALL / SHELL', 'Independent wall patch; NOT reproduction of CSI Example 15'),
]
# B05-B12 are independent component-level checks, not native CSI ETABS reruns.
CASES += [
 ('B05','Root rigid-end segment under tip force','FRAME END ZONE','Independent high-stiffness rigid-offset idealization'),
 ('B06','6 x 6 m shell slab and four edge beams','SLAB / FRAME','Shared solver nodes and symmetric gravity equilibrium, MESH_04/08/16'),
 ('B07','Wall supported on two columns','WALL / FRAME','Elastic shell-to-column vertical force transfer'),
 ('B08','Wall with geometric opening','WALL / OPENING','Net shell area and gravity equilibrium'),
 ('B09','Parallel wall/frame stiffness sharing','FOUNDATION FORCE SHARING','Independent EA/L-based two-support benchmark'),
 ('B10','Two-bay three-column frame','GRAVITY FRAME','Independent full-frame equilibrium, not full CSI Example 01'),
 ('B11','Single DOF axial oscillator','MODAL / MASS','Analytical eigenvalue and mass-units check'),
 ('B12','FVD power-law constitutive equation','DAMPER / ANALYTICAL','Analytical only, NOT native OpenSees link or CSI Example 11'),
]
REFERENCE_INDEX = [
 ('01','Plane frame — static gravity','component benchmark B01'),
 ('02','Three-storey frame — response spectrum / rigid offsets','REFERENCE ONLY; future native benchmark'),
 ('03','Three-storey historical seismic and wind','REFERENCE ONLY'),
 ('04','3D response spectrum','REFERENCE ONLY'),
 ('05','Three-storey braced frame response spectrum','REFERENCE ONLY'),
 ('06','Nine-storey eigenvalue analysis','REFERENCE ONLY'),
 ('07','Seven-storey frame gravity/static/dynamic','REFERENCE ONLY'),
 ('08','Two-storey 3D response spectrum','REFERENCE ONLY'),
 ('09','Two-storey 3D asymmetric response','REFERENCE ONLY'),
 ('10','ADAS device nonlinear response','REFERENCE ONLY'),
 ('11','Viscous dampers nonlinear time history','REFERENCE ONLY'),
 ('12','Gap/pounding nonlinear time history','REFERENCE ONLY'),
 ('13','Hysteretic base isolator','REFERENCE ONLY'),
 ('14','Friction pendulum isolator','REFERENCE ONLY'),
 ('15','Wall object static lateral response','REFERENCE ONLY; wall patch B04 and B07 are not CSI 15'),
]

def _metric(name, actual, expected, rel_tol, *, abs_tol=1e-7, source='ANALYTICAL', unit='', note=''):
    actual=float(actual); expected=float(expected)
    if not (math.isfinite(actual) and math.isfinite(expected)):
        raise ValueError('Non-finite benchmark result: '+name)
    delta=actual-expected
    scale=max(abs(expected),abs_tol)
    err=abs(delta)/scale
    return {'metric':name,'actual':actual,'expected':expected,'difference':delta,
            'relative_error':err,'tolerance':float(rel_tol),'passed':abs(delta)<=max(abs_tol,rel_tol*abs(expected)),
            'reference_type':source,'unit':unit,'note':note}

def _linear_static(ops):
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral')
    ops.test('NormUnbalance', 1e-10, 25); ops.algorithm('Newton')
    ops.integrator('LoadControl',1.0); ops.analysis('Static')
    rc=ops.analyze(1)
    if rc!=0: raise RuntimeError('OpenSees static analysis failed: '+str(rc))
    ops.reactions()

def _propped(ops,n):
    # CSI Example 01, Case II — B1 isolates a pinned-to-fixed 18-ft beam under 10 kip/ft.
    # Original source is a 2-bay, 3-column frame; we validate the equivalent propped-beam component,
    # not the entire CSI geometry.
    L=216.0; w=10.0/12.0; E=3000.0; I=12.0*30.0**3/12.0
    ops.wipe(); ops.model('basic','-ndm',2,'-ndf',3)
    for j in range(n+1): ops.node(j+1,L*j/n,0.)
    ops.fix(1,1,1,0);ops.fix(n+1,1,1,1)
    ops.geomTransf('Linear',1)
    for j in range(1,n+1):
        ops.element('elasticBeamColumn',j,j,j+1,1e9,E,I,1) # axial stiffness high; immaterial here
    ops.timeSeries('Linear',1);ops.pattern('Plain',1,1)
    for j in range(1,n+1): ops.eleLoad('-ele',j,'-type','-beamUniform',-w)
    _linear_static(ops)
    rx1=ops.nodeReaction(1,2);rx2=ops.nodeReaction(n+1,2)
    moment=ops.nodeReaction(n+1,3)
    mid=ops.nodeDisp(n//2+1,2) if n%2==0 else None
    exact_mid=-w*L**4/(192.0*E*I)
    return {'R_pin':rx1,'R_fixed':rx2,'M_fixed_abs':abs(moment),'R_sum':rx1+rx2,
            'mid':mid,'exact_mid':exact_mid,'n':n,'L':L,'w':w,'EI':E*I}

def _run_legacy_case(ops,case,tol):
    metrics=[];detail={}
    if case=='B01':
        s=_propped(ops,1);detail={'beam':s,'source':'CSI Software Verification Example 01, Table 1-1, Case II, 18-ft B1',
              'scope':'Propped beam component only; no full three-column frame reproduction',
              'reference_units':'kip, inch, second'}
        for name,got,exp,unit in [
            ('Pinned-end vertical reaction',s['R_pin'],67.5,'kip'),
            ('Fixed-end vertical reaction',s['R_fixed'],112.5,'kip'),
            ('Fixed-end moment magnitude',s['M_fixed_abs'],4860.0,'kip-in'),
            ('Total applied versus reactions',s['R_sum'],180.0,'kip')]:
            metrics.append(_metric(name,got,exp,tol,source='CSI_EX01_CASEII',unit=unit))
    elif case=='B02':
        states={str(n):_propped(ops,n) for n in (1,2,4,8)};detail={'segments':states,'source':'Euler-Bernoulli propped beam; direct shared FEM node continuity'}
        for n in (1,2,4,8):
            s=states[str(n)]
            metrics.append(_metric(f'{n} segment(s) pin reaction',s['R_pin'],67.5,tol,unit='kip'))
            metrics.append(_metric(f'{n} segment(s) fixed reaction',s['R_fixed'],112.5,tol,unit='kip'))
        for n in (2,4,8):
            s=states[str(n)]
            metrics.append(_metric(f'{n} segment(s) midpoint UY',s['mid'],s['exact_mid'],tol,unit='in',note='Closed-form Euler-Bernoulli beam deflection'))
    elif case=='B03':
        ops.wipe();ops.model('basic','-ndm',2,'-ndf',2)
        L=6.0; A=0.01; E=200e6; F=120.0
        ops.node(1,0.,0.);ops.node(2,L,0.);ops.fix(1,1,1);ops.fix(2,0,1)
        ops.uniaxialMaterial('Elastic',1,E)
        ops.element('truss',1,1,2,A,1)
        ops.timeSeries('Linear',1);ops.pattern('Plain',1,1);ops.load(2,F,0.)
        _linear_static(ops)
        u=ops.nodeDisp(2,1);r=ops.nodeReaction(1,1)
        detail={'L_m':L,'A_m2':A,'E_kN_m2':E,'F_kN':F,'analytic_u_m':F*L/(E*A), 'scope':'axial stiffness and reaction, not ETABS Example 05 full model'}
        metrics.extend([_metric('Axial displacement',u,F*L/(E*A),tol,unit='m'),_metric('Anchor reaction',r,-F,tol,unit='kN')])
    elif case=='B04':
        states={}
        for n in (1,2,4):
            ops.wipe();ops.model('basic','-ndm',3,'-ndf',6)
            E=25e6; nu=.2; t=.3; width=6.; height=3.; total=1200.
            for j in range(n+1):
                for i in range(n+1):
                    tag=1+j*(n+1)+i
                    ops.node(tag,width*i/n,0.,height*j/n)
                    if j==0:ops.fix(tag,1,1,1,1,1,1)
            ops.section('ElasticMembranePlateSection',1,E,nu,t,0.0)
            k=1
            for j in range(n):
                for i in range(n):
                    a=1+j*(n+1)+i;b=a+1;c=b+(n+1);d=a+(n+1)
                    ops.element('ShellMITC4',k,a,b,c,d,1);k+=1
            ops.timeSeries('Linear',1);ops.pattern('Plain',1,1)
            for i in range(n+1):
                top=1+n*(n+1)+i
                ops.load(top,0,0,-total*(.5 if i in (0,n) else 1.)/n,0,0,0)
            _linear_static(ops)
            R=sum(ops.nodeReaction(1+i,3) for i in range(n+1))
            mid=ops.nodeDisp(1+n*(n+1)+(n//2),3)
            states[str(n)]={'bottom_reaction_kN':R,'top_Uz_m':mid,'mesh_cells':n*n}
            metrics.append(_metric(f'{n}x{n} wall total base reaction',R,total,tol,unit='kN',source='EQUILIBRIUM_ONLY'))
        detail={'states':states,'scope':'2D wall shell in 3D, uniform top gravity; demonstrates equilibrium only. NOT ETABS Example 15 lateral wall verification.'}
    else: raise ValueError('Unknown benchmark '+case)
    return {'case_id':case,'title':next(c[1] for c in CASES if c[0]==case),
            'status':'PASS' if all(m['passed'] for m in metrics) else 'FAIL',
            'metrics':metrics,'details':detail}

# Integrated B05–B12 implementation; no second Python file needed.
"""Standalone, explicit numerical subassemblies for Verification Studio v2.

CAUTION: B05-B12 are independently defined micro-benchmarks, not full CSI examples
or native ETABS comparison. B12 is analytical-only. All stress values use kN/m².
"""
import math

G=9.81  # standalone copy of components.nbc105.constants.GRAVITY_M_S2


def _exp_metric(name, actual, expected, tol, unit='', source='ANALYTICAL', note='', abs_tol=1e-8):
    actual=float(actual);expected=float(expected)
    if not all(map(math.isfinite, (actual,expected))):raise ValueError('Nonfinite benchmark quantity: '+name)
    allowed=max(abs_tol,tol*abs(expected));diff=actual-expected
    return dict(metric=name,actual=actual,expected=expected,difference=diff,
                relative_error=abs(diff)/max(abs(expected),abs_tol),tolerance=tol,
                passed=abs(diff)<=allowed,reference_type=source,unit=unit,note=note)


def _exp_analysis(ops, *, dynamic=False):
    ops.constraints('Transformation');ops.numberer('RCM');ops.system('BandGeneral')
    ops.test('NormUnbalance',1e-9,50);ops.algorithm('Newton')
    if dynamic:
        ops.integrator('Newmark',0.5,0.25);ops.analysis('Transient')
    else:
        ops.integrator('LoadControl',1.);ops.analysis('Static')
    rc=ops.analyze(1,0.01) if dynamic else ops.analyze(1)
    if rc:raise RuntimeError('OpenSees solve failed, exit status '+str(rc))
    ops.reactions()


def _exp_mplate(ops, E=25e6,nu=.20,t=.15):
    ops.section('ElasticMembranePlateSection',1,E,nu,t,0.0)


def _exp_plate_square(ops,n=4,q=1.5):
    # Fully modeled beam-shell compatible 6m x 6m slab; four pinned vertically
    # supported beam-column grid corners. No vertical rigidDiaphragm constraint.
    ops.wipe();ops.model('basic','-ndm',3,'-ndf',6)
    L=6.;dx=L/n
    def tag(i,j):return 1+j*(n+1)+i
    for j in range(n+1):
        for i in range(n+1):
            node=tag(i,j);ops.node(node,i*dx,j*dx,0.)
            if i in (0,n) and j in (0,n):ops.fix(node,1,1,1,1,1,1)
    _exp_mplate(ops)
    k=1
    for j in range(n):
        for i in range(n):
            ops.element('ShellMITC4',k,tag(i,j),tag(i+1,j),tag(i+1,j+1),tag(i,j+1),1);k+=1
    ops.geomTransf('Linear',1,0,0,1)
    # Beam elements are split at all shell-edge nodes, i.e. true shared tags.
    beam_count=0
    for i in range(n):
        for a,b in ((tag(i,0),tag(i+1,0)),(tag(i,n),tag(i+1,n)),
                    (tag(0,i),tag(0,i+1)),(tag(n,i),tag(n,i+1))):
            ops.element('elasticBeamColumn',10000+beam_count,a,b,.48,30e6,12e6,.02,.03,.03,1)
            beam_count+=1
    ops.timeSeries('Linear',1);ops.pattern('Plain',1,1)
    applied=0.
    for j in range(n):
        for i in range(n):
            f=-q*dx*dx/4
            for node in (tag(i,j),tag(i+1,j),tag(i+1,j+1),tag(i,j+1)):
                ops.load(node,0,0,f,0,0,0);applied-=f
    _exp_analysis(ops)
    supports=[tag(0,0),tag(n,0),tag(0,n),tag(n,n)]
    reactions=[ops.nodeReaction(a,3) for a in supports]
    return dict(supports=reactions,total=sum(reactions),load=applied,
                center_uz_m=ops.nodeDisp(tag(n//2,n//2),3),cells=n*n,
                shared_beam_shell_nodes=4*n,beam_elements=beam_count)


def _exp_vertical_wall(ops,n=4,with_opening=False):
    # 6m wide, 4m tall shell; four-sided opening at the central 2x2 grid cells.
    # Bottom edge is fixed for the opening case; the column-supported case adds
    # independent frame columns and supports only the two column feet.
    ops.wipe();ops.model('basic','-ndm',3,'-ndf',6)
    width=6.;height=4.;dx=width/n;dz=height/n
    def tag(i,j):return 1+j*(n+1)+i
    for j in range(n+1):
        for i in range(n+1):
            node=tag(i,j)
            if with_opening and n==4 and i==2 and j==2:
                # Interior void node belongs to no shell and must not create
                # an unconstrained, zero-stiffness degree of freedom.
                continue
            ops.node(node,i*dx,0.,dz*j+(0 if with_opening else 3.))
            if with_opening and j==0:ops.fix(node,1,1,1,1,1,1)
    _exp_mplate(ops,t=.3)
    active=0; area=0
    for j in range(n):
        for i in range(n):
            if with_opening and n==4 and i in (1,2) and j in (1,2):continue
            a=tag(i,j);b=tag(i+1,j);c=tag(i+1,j+1);d=tag(i,j+1)
            active+=1;area+=dx*dz
            ops.element('ShellMITC4',active,a,b,c,d,1)
    if not with_opening:
        ops.geomTransf('Linear',1,0,1,0)
        for i in (0,n):
            base=500+i;ops.node(base,i*dx,0.,0);ops.fix(base,1,1,1,1,1,1)
            ops.element('elasticBeamColumn',5000+i,base,tag(i,0),.5,30e6,12e6,.03,.03,.03,1)
    W=600.
    ops.timeSeries('Linear',1);ops.pattern('Plain',1,1)
    for i in range(n+1):
        load=-W/n*(0.5 if i in (0,n) else 1.)
        ops.load(tag(i,n),0,0,load,0,0,0)
    _exp_analysis(ops)
    supports=[tag(i,0) for i in range(n+1)] if with_opening else [500,500+n]
    R=[ops.nodeReaction(x,3) for x in supports]
    return dict(reactions=R,total=sum(R),expected=W,net_area=area,
                cells=active,with_opening=with_opening)


def _exp_frame_wall_parallel(ops):
    # Elastic parallel axial members, two distinct physical supports and one
    # compatible superstructure node. This isolates gravity sharing by EA/L.
    ops.wipe();ops.model('basic','-ndm',2,'-ndf',2)
    L=4.;Ec=30e6;Af=.40;Aw=1.20;P=1000.
    ops.node(1,0,0);ops.node(2,2,0);ops.node(3,1,L)
    ops.fix(1,1,1);ops.fix(2,1,1);ops.fix(3,1,0)
    ops.uniaxialMaterial('Elastic',1,Ec)
    # Equal sloping physical element length, so the axial vertical stiffness
    # ratio remains Af:Aw; geometry is symmetric about x=1.
    ops.element('truss',1,1,3,Af,1);ops.element('truss',2,2,3,Aw,1)
    ops.timeSeries('Linear',1);ops.pattern('Plain',1,1);ops.load(3,0,-P)
    _exp_analysis(ops)
    rf=ops.nodeReaction(1,2);rw=ops.nodeReaction(2,2)
    return dict(frame_R=rf,wall_R=rw,total=rf+rw,expected_frame=P*Af/(Af+Aw),
                expected_wall=P*Aw/(Af+Aw),vertical_disp_m=ops.nodeDisp(3,2))


def _exp_rigid_end_test(ops):
    # Cantilever with a short high-EI rigid-offset element at fixed end.
    # Not an ETABS automatic end-zone implementation or full 6-DOF equality.
    ops.wipe();ops.model('basic','-ndm',2,'-ndf',3)
    L=6.; a=.8; E=30e6; I=.03;P=100.
    ops.node(1,0.,0.);ops.node(2,a,0.);ops.node(3,L,0.)
    ops.fix(1,1,1,1);ops.geomTransf('Linear',1)
    ops.element('elasticBeamColumn',1,1,2,1e3,E,I*1e9,1)
    ops.element('elasticBeamColumn',2,2,3,1e3,E,I,1)
    ops.timeSeries('Linear',1);ops.pattern('Plain',1,1);ops.load(3,0,-P,0)
    _exp_analysis(ops)
    # A rigid root offset rotates and translates as a stiff segment. Tip
    # deflection under a tip load depends on flexible L-a and rigid shift a.
    lf=L-a
    u=-P*lf**2*(lf/3+a)/(E*I)
    # Exact expression from flexible-tip slope and tip deflection:
    # u_tip = P [lf^3/3 + a*lf^2/2] /EI since the rigid root is fixed,
    # offset is at the clamped end -> no rotation contribution. Hence only
    # flexural length lf responds.
    u=-P*lf**3/(3*E*I)
    return dict(uy=ops.nodeDisp(3,2),reaction=ops.nodeReaction(1,2),
                moment=ops.nodeReaction(1,3),expected_uy=u,expected_reaction=P,
                expected_moment=P*L,offset=a,full_length=L)


def _exp_two_bay_frame(ops):
    # 3-column / 2-bay elastic frame. Reference from exact external
    # gravity equilibrium and symmetry, NOT published full CSI Example 01.
    ops.wipe();ops.model('basic','-ndm',2,'-ndf',3)
    L=6.;H=3.; q=20.
    for i,x in enumerate((0.,L,2*L),1):
        ops.node(i,x,0);ops.node(i+3,x,H);ops.fix(i,1,1,1)
    ops.geomTransf('Linear',1)
    for i in range(1,4):ops.element('elasticBeamColumn',i,i,i+3,.5,30e6,.03,1)
    for i in range(1,3):ops.element('elasticBeamColumn',10+i,i+3,i+4,.48,30e6,.025,1)
    ops.timeSeries('Linear',1);ops.pattern('Plain',1,1)
    for i in (11,12):ops.eleLoad('-ele',i,'-type','-beamUniform',-q)
    _exp_analysis(ops)
    R=[ops.nodeReaction(i,2) for i in (1,2,3)]
    return dict(reactions=R,total=sum(R),expected_total=2*L*q)


def _exp_modal_axial(ops):
    # Exact single DOF vertical axial oscillator: lambda = EA/(L*m).
    ops.wipe();ops.model('basic','-ndm',2,'-ndf',2)
    L=6.;E=2e8;A=.01;m=5.
    ops.node(1,0,0);ops.node(2,0,L);ops.fix(1,1,1);ops.fix(2,1,0)
    ops.uniaxialMaterial('Elastic',1,E)
    ops.element('truss',1,1,2,A,1);ops.mass(2,0.,m)
    eigen=ops.eigen('-fullGenLapack',1)
    lam=float(eigen[0] if isinstance(eigen,(list,tuple)) else eigen)
    return dict(lambda_calc=lam,lambda_expected=E*A/L/m,
                period_calc=2*math.pi/math.sqrt(lam),period_expected=2*math.pi*math.sqrt(L*m/(E*A)))


def _exp_run(case,ops,tol):
    metrics=[];details={};scope='INDEPENDENT_COMPONENT_BENCHMARK'
    def check(name,value,expected,unit='',reference='ANALYTICAL',abs_tol=1e-8,note=''):
        metrics.append(_exp_metric(name,value,expected,tol,unit,reference,note,abs_tol))
    if case=='B05':
        s=_exp_rigid_end_test(ops);details=s
        check('Rigid-zone beam root Fy',s['reaction'],s['expected_reaction'],'kN')
        check('Rigid-zone beam root Mz',s['moment'],s['expected_moment'],'kN-m')
        check('Flexible-length beam tip deflection',s['uy'],s['expected_uy'],'m',note='High EI offset; approximate rigid limit')
    elif case=='B06':
        states={}
        for n in (4,8,16):
            s=_exp_plate_square(ops,n);states[str(n)]=s
            check(f'{n}x{n} slab gravity equilibrium',s['total'],54.,'kN')
            for k,r in enumerate(s['supports']):check(f'{n}x{n} corner {k+1} symmetry',r,13.5,'kN',note='Four geometrically symmetric fully fixed corner supports')
        details={'states':states,'scope':'ShellMITC4 slab + edge beam shared-node benchmark, NOT ETABS mesh comparison'}
    elif case=='B07':
        s=_exp_vertical_wall(ops,n=4,with_opening=False);details=s
        check('Wall-on-columns base reaction',s['total'],600.,'kN')
        for i,r in enumerate(s['reactions']):check('Column support '+str(i+1),r,300.,'kN')
    elif case=='B08':
        s=_exp_vertical_wall(ops,n=4,with_opening=True);details=s
        check('Opening wall net area',s['net_area'],18.,'m2')
        check('Opening wall gravity total',s['total'],600.,'kN')
        check('Opening wall symmetric half load left',sum(s['reactions'][:2])+s['reactions'][2]/2,300.,'kN')
    elif case=='B09':
        s=_exp_frame_wall_parallel(ops);details=s
        check('Parallel frame base reaction',s['frame_R'],s['expected_frame'],'kN')
        check('Parallel wall base reaction',s['wall_R'],s['expected_wall'],'kN')
        check('Parallel total reaction',s['total'],1000.,'kN')
    elif case=='B10':
        s=_exp_two_bay_frame(ops);details=s
        check('Two-bay complete gravity equilibrium',s['total'],s['expected_total'],'kN')
        check('Two-bay end support symmetry',s['reactions'][0],s['reactions'][2],'kN')
    elif case=='B11':
        s=_exp_modal_axial(ops);details=s
        check('Axial oscillator eigenvalue',s['lambda_calc'],s['lambda_expected'],'1/s2')
        check('Axial oscillator period',s['period_calc'],s['period_expected'],'s')
    elif case=='B12':
        # Analytical material law verification, NOT a native viscous link run.
        # Explicit distinct status avoids claiming NLTHA of a damper.
        scope='ANALYTICAL_ONLY_NOT_NATIVE_OPENSEES'
        C=700.;alpha=.3
        velocities=(-2.,-1.,-.1,0.,.1,1.,2.)
        forces=[math.copysign(C*abs(v)**alpha,v) if v else 0. for v in velocities]
        for v,f in zip(velocities,forces):
            check(f'Viscous force symmetry v={v}',f,-(math.copysign(C*abs(-v)**alpha,-v) if v else 0.),'kN',reference='CONSTITUTIVE_ANALYTICAL_ONLY')
        details={'coefficient_C':C,'alpha':alpha,'velocities_m_per_s':velocities,'forces_kN':forces,
                 'C_units':'kN*(s/m)^alpha for velocities expressed in m/s',
                 'warning':'This is NOT a solver test of the exponential damper or matched ETABS link; C is a numerical example, not approval of the thesis parameter.'}
    else:raise ValueError('Unknown expanded benchmark '+case)
    passed=all(m['passed'] for m in metrics)
    status=('ANALYTICAL_PASS' if passed else 'ANALYTICAL_FAIL') if case=='B12' else ('PASS' if passed else 'FAIL')
    titles={'B05':'Beam root rigid offset component','B06':'6 m x 6 m slab/beam shared nodes','B07':'Wall supported by two columns','B08':'Wall with central opening','B09':'Parallel frame/wall support force sharing','B10':'Three-column two-bay frame equilibrium','B11':'Axial oscillator eigenvalue and period','B12':'Exponential viscous damper force-velocity law (analytical)'}
    return dict(case_id=case,title=titles[case],status=status,metrics=metrics,details=details,
                verification_scope=scope,etabs_native_equivalence='NOT_VERIFIED')

# Preserve the user-tested v1 B01-B04 implementation unchanged.
# B01-B04 use the explicitly named legacy benchmark implementation.

def _run_case(ops,case,tol):
    if case in ('B01','B02','B03','B04'):
        result=_run_legacy_case(ops,case,tol)
        result['verification_scope']='INDEPENDENT_COMPONENT_BENCHMARK'
        result['etabs_native_equivalence']='NOT_VERIFIED'
        return result
    return _exp_run(case,ops,tol)

def run_worker(case, tolerance, destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    try:
        if case=='B12':
            # B12 intentionally tests only analytical constitutive signs/units.
            result=_run_case(None,case,tolerance)
            result['solver']='NONE_ANALYTICAL_ONLY'
            result['solver_version']='NOT_APPLICABLE'
        else:
            import openseespy.opensees as ops
            result=_run_case(ops,case,tolerance)
            result['solver']='OpenSeesPy';result['solver_version']=str(ops.version()) if hasattr(ops,'version') else 'unavailable'
    except FileNotFoundError as exc:
        result={'case_id':case,'title':next(c[1] for c in CASES if c[0]==case),'status':'BLOCKED',
                'reason':str(exc),'missing_dependency':'expanded_benchmarks.py','metrics':[]}
    except (ImportError, ModuleNotFoundError) as exc:
        missing = str(getattr(exc,'name', '') or '')
        if missing.startswith('openseespy'):
            reason = 'OpenSeesPy is not installed in the selected Python environment: ' + str(exc)
        else:
            reason = ('Benchmark module or its dependency could not be imported: ' + str(exc) +
                      '. Check that expanded_benchmarks.py is beside the Studio script.')
        result={'case_id':case,'title':next(c[1] for c in CASES if c[0]==case),'status':'BLOCKED',
                'reason':reason,'missing_dependency':missing,'metrics':[]}
    except Exception as exc:
        result={'case_id':case,'title':next(c[1] for c in CASES if c[0]==case),'status':'ERROR',
                'reason':str(exc),'traceback':traceback.format_exc(), 'metrics':[]}
    import hashlib
    result['source_sha256']={name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
                             for name in ('ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py',)
                             if (Path(__file__).parent/name).is_file()}
    result['timestamp']=dt.datetime.now(dt.timezone.utc).isoformat()
    result['tolerance_relative']=tolerance
    result['software_version']=APP_VERSION
    (destination/(case+'.json')).write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
    print(json.dumps({'case_id':case,'status':result['status'],'metrics':len(result['metrics']),'reason':result.get('reason','')}),flush=True)
    return result

def _write_reports(folder, results, provenance):
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    (folder/'manifest.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    (folder/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    cols=['case_id','case_status','metric','actual','expected','difference','relative_error','tolerance','passed','unit','reference_type','note']
    with (folder/'metrics.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for r in results:
            for m in r.get('metrics',[]):w.writerow({'case_id':r['case_id'],'case_status':r['status'],**{k:m.get(k,'') for k in cols if k not in ('case_id','case_status')}})
    rows=[]
    for r in results:
        rows.append(f'<tr><td>{html.escape(r["case_id"])}</td><td>{html.escape(r["title"])}</td><td>{html.escape(r["status"])}</td><td>{len(r.get("metrics",[]))}</td><td>{html.escape(r.get("reason", ""))}</td></tr>')
    page='''<!DOCTYPE html><html lang="en"><meta charset="utf-8"><title>OpenSeesPy Verification Report</title><style>
body{font:15px system-ui,Arial;max-width:1100px;margin:44px auto;padding:0 16px;color:#162839}h1{font-size:26px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid #ddd}th{background:#f2f5f8}
.warning{background:#fff1d8;padding:16px;border-radius:6px}code{font-size:12px}</style>
<h1>ETABS–OpenSeesPy Independent Verification</h1><p class="warning">PASS means only the listed native component benchmark passed; ANALYTICAL_PASS is not a solver run. It does not verify the full CSI ETABS example, the ETABS native solver, or the thesis model. BLOCKED/ERROR are not PASS.</p>
<p>Run provenance: <code>'''+html.escape(json.dumps(provenance))+'''</code></p><table><tr><th>Case</th><th>Benchmark</th><th>Status</th><th>Metrics</th><th>Diagnostic</th></tr>'''+''.join(rows)+'</table><p>See metrics.csv, results.json and individual per-case JSON for full numerical details.</p></html>'
    (folder/'report.html').write_text(page,encoding='utf-8')

def compare_support_csv(source,output_dir):
    # User provided explicitly mapped source and target IDs. Never match by equal integer name.
    source=Path(source);output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    with source.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    required={'opensees_node','etabs_unique_name','source_primary32','original_ETABS_FZ_kN','opensees_32_Rz_kN'}
    if not rows or not required.issubset(rows[0]):raise ValueError('Input CSV must have exact verified source/target ID and reaction columns')
    selected=[r for r in rows if str(r['source_primary32']).strip().lower() in ('true','1','yes')]
    if len(selected)!=32:raise ValueError(f'Expected exactly 32 mapped foundation reaction records, got {len(selected)}')
    def unique(vals,name):
        if len(set(vals))!=32:raise ValueError('Nonunique '+name+' mapping')
    unique([r['opensees_node'] for r in selected],'OpenSees nodes');unique([r['etabs_unique_name'] for r in selected],'ETABS source points')
    data=[]
    for r in selected:
        e=float(r['original_ETABS_FZ_kN']);o=float(r['opensees_32_Rz_kN'])
        if not all(map(math.isfinite,(e,o))):raise ValueError('Nonfinite reaction data')
        data.append({'etabs_point':r['etabs_unique_name'],'opensees_node':r['opensees_node'],'etabs_kN':e,'opensees_kN':o,'delta_kN':o-e,'abs_delta_kN':abs(o-e),'relative_percent':100*(o-e)/abs(e) if abs(e)>1e-9 else None})
    data.sort(key=lambda r:-r['abs_delta_kN'])
    with (output_dir/'support32_mapped_comparison.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    summary={'source_file':str(source),'count':32,'etabs_sum_kN':sum(r['etabs_kN'] for r in data),
             'opensees_sum_kN':sum(r['opensees_kN'] for r in data),'absolute_difference_sum_kN':sum(r['abs_delta_kN'] for r in data),
             'max_absolute_difference_kN':max(r['abs_delta_kN'] for r in data),
             'status':'DATA_COMPARISON_ONLY_NOT_EQUIVALENCE_PASSED'}
    (output_dir/'support32_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    root=tk.Tk();root.title('ETABS ↔ OpenSeesPy | Independent Verification Studio');root.geometry('1120x740');root.minsize(890,600)
    style=ttk.Style(root)
    if 'clam' in style.theme_names():style.theme_use('clam')
    container=ttk.Frame(root,padding=14);container.pack(fill='both',expand=True)
    ttk.Label(container,text='ETABS ↔ OpenSeesPy Verification Studio',font=('Segoe UI',19,'bold')).pack(anchor='w')
    ttk.Label(container,text='Standalone benchmark runner  •  never edits the source ETABS model or thesis solver  •  outputs isolated per run').pack(anchor='w',pady=(2,12))
    controls=ttk.Frame(container);controls.pack(fill='x')
    python_var=tk.StringVar(value=sys.executable);output_var=tk.StringVar(value=str(Path.cwd()/'VERIFICATION_RUNS'))
    tolerance_var=tk.StringVar(value='0.01');selection=tk.StringVar(value='')
    ttk.Label(controls,text='Solver Python:').grid(row=0,column=0,sticky='w',pady=3)
    ttk.Entry(controls,textvariable=python_var).grid(row=0,column=1,sticky='ew',padx=7)
    ttk.Button(controls,text='Browse',command=lambda: python_var.set(filedialog.askopenfilename(filetypes=[('Python executable','python.exe'),('All files','*')]) or python_var.get())).grid(row=0,column=2)
    ttk.Label(controls,text='Output root:').grid(row=1,column=0,sticky='w',pady=3)
    ttk.Entry(controls,textvariable=output_var).grid(row=1,column=1,sticky='ew',padx=7)
    ttk.Button(controls,text='Browse',command=lambda: output_var.set(filedialog.askdirectory() or output_var.get())).grid(row=1,column=2)
    ttk.Label(controls,text='Relative tolerance:').grid(row=2,column=0,sticky='w',pady=3)
    ttk.Entry(controls,textvariable=tolerance_var,width=13).grid(row=2,column=1,sticky='w',padx=7)
    controls.columnconfigure(1,weight=1)
    hint='0.01 = 1%; component benchmark default for this diagnostic. Tighten when solver equivalence is established.'
    ttk.Label(container,text=hint,foreground='#485b70').pack(anchor='w',pady=(4,10))
    notebook=ttk.Notebook(container);notebook.pack(fill='both',expand=True)
    tab=ttk.Frame(notebook,padding=8);notebook.add(tab,text='Executable Benchmarks')
    ref=ttk.Frame(notebook,padding=8);notebook.add(ref,text='CSI Verification Catalog (15)')
    logtab=ttk.Frame(notebook,padding=8);notebook.add(logtab,text='Progress / Results')
    tree=ttk.Treeview(tab,columns=('category','source'),show='tree headings',selectmode='extended',height=9)
    tree.heading('#0',text='Benchmark');tree.column('#0',width=340)
    tree.heading('category',text='Verification category');tree.column('category',width=180)
    tree.heading('source',text='Scope / reference');tree.column('source',width=450)
    for cid,name,category,source in CASES:tree.insert('', 'end',iid=cid,text=cid+' — '+name,values=(category,source))
    tree.pack(fill='both',expand=True)
    ttk.Label(tab,text='Select one or more benchmarks (Ctrl/Shift). Only implemented tests can receive PASS. The 15 published CSI cases are not implicitly reproduced.').pack(anchor='w',pady=10)
    cat=ttk.Treeview(ref,columns=('topic','scope'),show='tree headings',height=16)
    for k,v,width in [('#0','CSI example',105),('topic','Published subject',360),('scope','Implementation status',470)]:
        cat.heading(k,text=v);cat.column(k,width=width)
    for n,title,scope in REFERENCE_INDEX:cat.insert('', 'end',text='Example '+n,values=(title,scope))
    cat.pack(fill='both',expand=True)
    ttk.Label(ref,text='Sources: uploaded CSI Example 01–15 PDFs. These reference-only entries have not been executed.').pack(anchor='w',pady=6)
    log=tk.Text(logtab,height=12,wrap='word',state='disabled',font=('Consolas',10));log.pack(fill='both',expand=True)
    state={'working':False,'thread':None,'last_output':None};events=queue.Queue()
    def append(msg):
        log.configure(state='normal');log.insert('end',msg+'\n');log.see('end');log.configure(state='disabled')
    def poll():
        try:
            while True:
                kind,data=events.get_nowait()
                if kind=='log':append(data)
                elif kind=='done':state['working']=False;state['last_output']=data;append('Report: '+str(Path(data)/'report.html'));set_controls('normal')
        except queue.Empty:pass
        root.after(125,poll)
    def set_controls(v):
        for b in (runselected,runall,compbtn):b.configure(state=v)
    def do_run(cids):
        if state['working']:return
        try:
            tol=float(tolerance_var.get());assert math.isfinite(tol) and 0<tol<1
            py=Path(python_var.get()).expanduser();assert py.is_file()
            root_out=Path(output_var.get()).expanduser();root_out.mkdir(parents=True,exist_ok=True)
        except (ValueError,AssertionError,OSError):
            messagebox.showerror('Invalid inputs','Specify an existing Python interpreter, writable output directory, and tolerance between 0 and 1.');return
        folder=root_out/(dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]);folder.mkdir()
        state['working']=True;set_controls('disabled');notebook.select(logtab)
        def worker():
            results=[]
            for cid in cids:
                events.put(('log','RUN '+cid))
                cmd=[str(py),str(Path(__file__).resolve()),'--worker',cid,'--output',str(folder/'cases'),'--tolerance',str(tol)]
                try:
                    result=subprocess.run(cmd,capture_output=True,text=True,timeout=180,check=False)
                    if result.stdout:events.put(('log',result.stdout.strip()))
                    if result.stderr:events.put(('log','Solver diagnostic: '+result.stderr.strip()[-1200:]))
                    path=folder/'cases'/(cid+'.json')
                    data=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'case_id':cid,'title':cid,'status':'ERROR','metrics':[],'reason':'No worker result; '+result.stderr[-1200:]}
                except Exception as exc:
                    data={'case_id':cid,'title':cid,'status':'ERROR','metrics':[],'reason':str(exc)}
                results.append(data);events.put(('log','STATUS '+cid+' = '+data['status']))
            prov={'tool_version':APP_VERSION,'timestamp':dt.datetime.now(dt.timezone.utc).isoformat(), 'python':str(py),
                  'tolerance':tol,'requested_cases':cids,'scope':'Benchmark verification only; source model untouched'}
            _write_reports(folder,results,prov);events.put(('done',str(folder)))
        state['thread']=threading.Thread(target=worker,daemon=True);state['thread'].start()
    buttons=ttk.Frame(container);buttons.pack(fill='x',pady=(10,0))
    runselected=ttk.Button(buttons,text='Run selected',command=lambda:do_run(list(tree.selection())) if tree.selection() else messagebox.showinfo('Choose benchmarks','Select at least one benchmark'))
    runselected.pack(side='left',padx=(0,7))
    runall=ttk.Button(buttons,text='Run all 12 benchmarks',command=lambda:do_run([c[0] for c in CASES]));runall.pack(side='left',padx=(0,7))
    def compare():
        file=filedialog.askopenfilename(title='Choose verified 32/76/97 mapped reaction CSV',filetypes=[('CSV','*.csv')]);
        if not file:return
        try:
            folder=Path(output_var.get()).expanduser()/(dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_support32_compare')
            summary=compare_support_csv(file,folder)
            notebook.select(logtab);append('32-support comparison: '+json.dumps(summary,indent=2))
            append('Comparison file: '+str(folder/'support32_mapped_comparison.csv'))
        except Exception as e:messagebox.showerror('Reaction CSV error',str(e))
    compbtn=ttk.Button(buttons,text='Audit mapped 32-support CSV…',command=compare);compbtn.pack(side='left')
    ttk.Button(buttons,text='Open last report',command=lambda:os.startfile(str(Path(state['last_output'])/'report.html')) if state['last_output'] and hasattr(os,'startfile') else messagebox.showinfo('Report location',str(state['last_output'] or 'No report generated'))).pack(side='right')
    ttk.Label(container,text='PASS = native numerical benchmark  | ANALYTICAL_PASS = equation only | BLOCKED = missing solver | ERROR = failure',foreground='#485b70').pack(anchor='w',pady=(8,0))
    root.after(125,poll);root.mainloop()

def self_test():
    s=_metric('test',10.,10.,1e-3);assert s['passed']
    s=_metric('test',9.,10.,1e-3);assert not s['passed']
    # Analytic consistency for Example 01 loads and geometry and beam midspan formula
    L=216.;w=10./12.;E=3000.;I=27000.
    assert abs(3*w*L/8-67.5)<1e-10
    assert abs(5*w*L/8-112.5)<1e-10
    assert abs(w*L*L/8-4860.)<1e-10
    assert -w*L**4/(192*E*I)<0
    assert len(REFERENCE_INDEX)==15 and len(CASES)==12
    print('SELF-TEST PASS: single-file 12-case registry, v1 formulas, source catalog and status logic. Expanded OpenSeesPy runs NOT tested here.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--worker',choices=[x[0] for x in CASES]);p.add_argument('--run-all',action='store_true')
    p.add_argument('--cases',nargs='+',choices=[x[0] for x in CASES],help='Run selected benchmark IDs in headless mode')
    p.add_argument('--list-cases',action='store_true',help='Print all executable benchmark IDs and scopes')
    p.add_argument('--self-test',action='store_true');p.add_argument('--output',default='VERIFICATION_RUNS')
    p.add_argument('--tolerance',type=float,default=.01);p.add_argument('--compare-32',metavar='CSV')
    args=p.parse_args()
    if not math.isfinite(args.tolerance) or not 0<args.tolerance<1:
        p.error('--tolerance must be a finite number greater than 0 and less than 1')
    if args.list_cases:
        for c in CASES:print(f'{c[0]} | {c[1]} | {c[3]}')
        return 0
    if args.self_test:self_test();return 0
    if args.compare_32:
        print(json.dumps(compare_support_csv(args.compare_32,args.output),indent=2));return 0
    if args.worker:
        result=run_worker(args.worker,args.tolerance,args.output)
        return 0 if result['status'] in ('PASS','FAIL','BLOCKED','ANALYTICAL_PASS','ANALYTICAL_FAIL') else 1
    if args.run_all or args.cases:
        selected=[c for c in CASES if args.run_all or c[0] in args.cases]
        root=Path(args.output)/(dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]);root.mkdir(parents=True)
        results=[run_worker(c[0],args.tolerance,root/'cases') for c in selected]
        _write_reports(root,results,{'tool_version':APP_VERSION,'python':sys.executable,'tolerance':args.tolerance,'status':'native solver execution' if any(r['status']=='PASS' for r in results) else 'unverified'})
        print('Reports: '+str(root))
        return 0 if all(x['status'] in ('PASS','ANALYTICAL_PASS') for x in results) else 2
    run_gui();return 0

if __name__=='__main__':sys.exit(main())