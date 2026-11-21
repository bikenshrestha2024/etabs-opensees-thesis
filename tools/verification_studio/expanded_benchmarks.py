"""Standalone, explicit numerical subassemblies for Verification Studio v2.

CAUTION: B05-B12 are independently defined micro-benchmarks, not full CSI examples
or native ETABS comparison. B12 is analytical-only. All stress values use kN/m².
"""
import math

G=9.81  # standalone copy of components.nbc105.constants.GRAVITY_M_S2


def metric(name, actual, expected, tol, unit='', source='ANALYTICAL', note='', abs_tol=1e-8):
    actual=float(actual);expected=float(expected)
    if not all(map(math.isfinite, (actual,expected))):raise ValueError('Nonfinite benchmark quantity: '+name)
    allowed=max(abs_tol,tol*abs(expected));diff=actual-expected
    return dict(metric=name,actual=actual,expected=expected,difference=diff,
                relative_error=abs(diff)/max(abs(expected),abs_tol),tolerance=tol,
                passed=abs(diff)<=allowed,reference_type=source,unit=unit,note=note)


def analysis(ops, *, dynamic=False):
    ops.constraints('Transformation');ops.numberer('RCM');ops.system('BandGeneral')
    ops.test('NormUnbalance',1e-9,50);ops.algorithm('Newton')
    if dynamic:
        ops.integrator('Newmark',0.5,0.25);ops.analysis('Transient')
    else:
        ops.integrator('LoadControl',1.);ops.analysis('Static')
    rc=ops.analyze(1,0.01) if dynamic else ops.analyze(1)
    if rc:raise RuntimeError('OpenSees solve failed, exit status '+str(rc))
    ops.reactions()


def mplate(ops, E=25e6,nu=.20,t=.15):
    ops.section('ElasticMembranePlateSection',1,E,nu,t,0.0)


def plate_square(ops,n=4,q=1.5):
    # Fully modeled beam-shell compatible 6m x 6m slab; four pinned vertically
    # supported beam-column grid corners. No vertical rigidDiaphragm constraint.
    ops.wipe();ops.model('basic','-ndm',3,'-ndf',6)
    L=6.;dx=L/n
    def tag(i,j):return 1+j*(n+1)+i
    for j in range(n+1):
        for i in range(n+1):
            node=tag(i,j);ops.node(node,i*dx,j*dx,0.)
            if i in (0,n) and j in (0,n):ops.fix(node,1,1,1,1,1,1)
    mplate(ops)
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
    analysis(ops)
    supports=[tag(0,0),tag(n,0),tag(0,n),tag(n,n)]
    reactions=[ops.nodeReaction(a,3) for a in supports]
    return dict(supports=reactions,total=sum(reactions),load=applied,
                center_uz_m=ops.nodeDisp(tag(n//2,n//2),3),cells=n*n,
                shared_beam_shell_nodes=4*n,beam_elements=beam_count)


def vertical_wall(ops,n=4,with_opening=False):
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
    mplate(ops,t=.3)
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
    analysis(ops)
    supports=[tag(i,0) for i in range(n+1)] if with_opening else [500,500+n]
    R=[ops.nodeReaction(x,3) for x in supports]
    return dict(reactions=R,total=sum(R),expected=W,net_area=area,
                cells=active,with_opening=with_opening)


def frame_wall_parallel(ops):
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
    analysis(ops)
    rf=ops.nodeReaction(1,2);rw=ops.nodeReaction(2,2)
    return dict(frame_R=rf,wall_R=rw,total=rf+rw,expected_frame=P*Af/(Af+Aw),
                expected_wall=P*Aw/(Af+Aw),vertical_disp_m=ops.nodeDisp(3,2))


def rigid_end_test(ops):
    # Cantilever with a short high-EI rigid-offset element at fixed end.
    # Not an ETABS automatic end-zone implementation or full 6-DOF equality.
    ops.wipe();ops.model('basic','-ndm',2,'-ndf',3)
    L=6.; a=.8; E=30e6; I=.03;P=100.
    ops.node(1,0.,0.);ops.node(2,a,0.);ops.node(3,L,0.)
    ops.fix(1,1,1,1);ops.geomTransf('Linear',1)
    ops.element('elasticBeamColumn',1,1,2,1e3,E,I*1e9,1)
    ops.element('elasticBeamColumn',2,2,3,1e3,E,I,1)
    ops.timeSeries('Linear',1);ops.pattern('Plain',1,1);ops.load(3,0,-P,0)
    analysis(ops)
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


def two_bay_frame(ops):
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
    analysis(ops)
    R=[ops.nodeReaction(i,2) for i in (1,2,3)]
    return dict(reactions=R,total=sum(R),expected_total=2*L*q)


def modal_axial(ops):
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


def run(case,ops,tol):
    metrics=[];details={};scope='INDEPENDENT_COMPONENT_BENCHMARK'
    def check(name,value,expected,unit='',reference='ANALYTICAL',abs_tol=1e-8,note=''):
        metrics.append(metric(name,value,expected,tol,unit,reference,note,abs_tol))
    if case=='B05':
        s=rigid_end_test(ops);details=s
        check('Rigid-zone beam root Fy',s['reaction'],s['expected_reaction'],'kN')
        check('Rigid-zone beam root Mz',s['moment'],s['expected_moment'],'kN-m')
        check('Flexible-length beam tip deflection',s['uy'],s['expected_uy'],'m',note='High EI offset; approximate rigid limit')
    elif case=='B06':
        states={}
        for n in (4,8,16):
            s=plate_square(ops,n);states[str(n)]=s
            check(f'{n}x{n} slab gravity equilibrium',s['total'],54.,'kN')
            for k,r in enumerate(s['supports']):check(f'{n}x{n} corner {k+1} symmetry',r,13.5,'kN',note='Four geometrically symmetric fully fixed corner supports')
        details={'states':states,'scope':'ShellMITC4 slab + edge beam shared-node benchmark, NOT ETABS mesh comparison'}
    elif case=='B07':
        s=vertical_wall(ops,n=4,with_opening=False);details=s
        check('Wall-on-columns base reaction',s['total'],600.,'kN')
        for i,r in enumerate(s['reactions']):check('Column support '+str(i+1),r,300.,'kN')
    elif case=='B08':
        s=vertical_wall(ops,n=4,with_opening=True);details=s
        check('Opening wall net area',s['net_area'],18.,'m2')
        check('Opening wall gravity total',s['total'],600.,'kN')
        check('Opening wall symmetric half load left',sum(s['reactions'][:2])+s['reactions'][2]/2,300.,'kN')
    elif case=='B09':
        s=frame_wall_parallel(ops);details=s
        check('Parallel frame base reaction',s['frame_R'],s['expected_frame'],'kN')
        check('Parallel wall base reaction',s['wall_R'],s['expected_wall'],'kN')
        check('Parallel total reaction',s['total'],1000.,'kN')
    elif case=='B10':
        s=two_bay_frame(ops);details=s
        check('Two-bay complete gravity equilibrium',s['total'],s['expected_total'],'kN')
        check('Two-bay end support symmetry',s['reactions'][0],s['reactions'][2],'kN')
    elif case=='B11':
        s=modal_axial(ops);details=s
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