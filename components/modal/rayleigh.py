"""NBC 105:2025 §5.1.1 force/displacement Rayleigh estimate.

Reference: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
The centered reference vector uses the amplified empirical ESM period.
An explicit legacy CLI or API call uses the historical small perturbation.
This is a period-estimation diagnostic, not a ULS ESM eligibility override,
nor evidence that IS 16700 initial combination cases have been completed.
"""

from OpenSees_Timing_V130 import timed_outputs

__release__ = '134'
from pathlib import Path
import csv
import json
import math
import hashlib
import os
from components.nbc105.clause_05_dynamic_characteristics import amplified_period_s, empirical_period_s
from components.nbc105.constants import GRAVITY_M_S2


RAYLEIGH_METHOD_VERSION = 127
RAYLEIGH_DISPLACEMENT_BASIS = 'TORSION_SUPPRESSED_CONSTRAINED_FLOOR_NODES'
RAYLEIGH_PREFIX = 'NBC105_Rayleigh_Preliminary_V127'


def rayleigh_result_prefix(state):
    """Build the ULS/SLS period output prefix.

    [REF docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md]
    """
    return RAYLEIGH_PREFIX + ('' if state == 'ULS' else '_' + state)


def empirical_esm_reference(rows, *, height_m, aw_m2, state, settings):
    """Build the centered floor-load vector at the amplified empirical period.

    [REF NBC105-2025 §§5.1.2–5.1.3 and 6.3]
    """
    from components.equivalent_static.code_basis import calculate_esm

    aw = float(aw_m2)
    if not math.isfinite(aw) or aw <= 0:
        raise ValueError("Directional Aw must be finite and positive.")
    empirical = empirical_period_s(height_m, "concrete shear-wall", aw)
    seed = calculate_esm(rows, period_s=amplified_period_s(empirical), limit_state=state,
                         diagnostic_reference=True, **settings)
    proof = {key: seed[key] for key in (
        "period_s", "period_exponent_k", "base_shear_kN", "design_coefficient_Cd",
        "code_eligible", "site_subsoil_status",
    )}
    return empirical, proof, [row["lateral_force_kN"] for row in seed["stories"]]


def verify_empirical_esm_reference(result, axis, *, source_rows=None):
    """Rebuild the saved empirical ESM seed and match every applied floor force.

    [REF docs/source/components/modal/rayleigh.py.md]
    """
    record = result[axis]
    if source_rows is None:
        rows = [{"height_m": row["height_m"], "dead_load_kN": row["weight_kN"]}
                for row in record["rows"]]
    else:
        rows = sorted(source_rows, key=lambda row: float(row["height_m"]))
        if len(rows) != len(record["rows"]) or not math.isclose(
                result["height_m"], float(rows[-1]["height_m"]), abs_tol=1e-7):
            raise ValueError(f"{axis}: empirical ESM seed has different source story coverage.")
        for source, row in zip(rows, record["rows"]):
            weight = (float(source["dead_load_kN"]) + .6*float(source["storage_live_load_kN"])
                      + .3*float(source["other_live_load_kN"]))
            if (int(source["master_node_tag"]) != row["master_node"]
                    or not math.isclose(float(source["height_m"]), row["height_m"], abs_tol=1e-7)
                    or not math.isclose(weight, row["weight_kN"], rel_tol=1e-9)):
                raise ValueError(f"{axis}: empirical ESM seed differs from the source story ledger.")
    empirical, proof, forces = empirical_esm_reference(
        rows, height_m=result["height_m"], aw_m2=record["Aw_m2"],
        state=result["limit_state"], settings=result["empirical_esm_settings"])
    checks = (
        (record["empirical_period_s"], empirical),
        (record["amplified_empirical_s"], proof["period_s"]),
        (record["reference_force_exponent_k"], proof["period_exponent_k"]),
        (record["reference_force_total_kN"], proof["base_shear_kN"]),
        (record["adopted_period_s"], min(record["period_s"], proof["period_s"])),
        *((row["force_kN"], force) for row, force in zip(record["rows"], forces)),
    )
    if record.get("empirical_esm_reference") != proof or any(
            not math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-8) for a, b in checks):
        raise ValueError(f"{axis}: saved Rayleigh forces do not match the empirical ESM seed.")


def _diaphragm_translation(ops, master, members, dof):
    """Read shared translation in m from a horizontal, torsion-suppressed floor.

    With RZ=0 the rigid diaphragm equations give the same UX/UY at the
    retained point and every tied node. OpenSees 3.8.0 Transformation can
    accumulate retained-node translation when a retained MP DOF also has an
    SP. The physical tied nodes provide the displacement used in the work sum.
    """
    if not members:
        raise RuntimeError(f'Rayleigh diaphragm {master} has no constrained floor nodes.')
    if any(not abs(ops.nodeDisp(n, 6)) <= 1e-9 for n in members):
        raise RuntimeError(f'Rayleigh diaphragm {master} has unexpected rotation.')
    translations = [ops.nodeDisp(n, dof) for n in members]
    if not all(math.isfinite(value) for value in translations):
        raise RuntimeError(f'Rayleigh diaphragm {master} has nonfinite floor translations.')
    spread = max(translations) - min(translations)
    if spread > 1e-8:
        raise RuntimeError(f'Rayleigh diaphragm {master} has inconsistent floor translations ({spread:g} m).')
    return math.fsum(translations) / len(translations), spread


@timed_outputs('Preliminary Rayleigh X-Y analysis','folder')
def run(folder, awx, awy, reference_fraction=.01, limit_state='ULS',
        output_dir=None, *, empirical_settings=None):
    gravity_profile = os.environ.get('OPENSEES_GRAVITY_PROFILE', 'AS_CONFIGURED')
    if empirical_settings is not None and gravity_profile not in ('AS_CONFIGURED', 'SEISMIC_SOURCE'):
        raise ValueError('Empirical Rayleigh requires the assembled seismic preload. '
                         'Use AS_CONFIGURED or SEISMIC_SOURCE for OPENSEES_GRAVITY_PROFILE.')
    import openseespy.opensees as ops
    from OpenSees_Complete_Export_V118 import build_complete_model
    from OpenSees_Analysis_Stack_V110 import configure_nonlinear_static
    from openpyxl import Workbook
    from matplotlib.figure import Figure
    folder=Path(folder)
    state=str(limit_state).strip().upper()
    if state not in ('ULS','SLS'):raise ValueError('limit_state must be ULS or SLS')
    if output_dir is not None:
        out=Path(output_dir)
    else:
        from components.inputs.project_workbooks import analysis_output_folder
        out=analysis_output_folder(folder,state)
    out.mkdir(parents=True,exist_ok=True)
    reference_fraction=float(reference_fraction)
    if not math.isfinite(reference_fraction) or reference_fraction<=0:raise ValueError('Reference fraction must be finite and positive.')
    model=folder/'OpenSees_Complete_Model_Data_V118.json'
    with (folder/'NBC105_ESM_Story_Weights_Assembled_V118.csv').open(encoding='utf-8-sig') as stream:rows=list(csv.DictReader(stream))
    if not rows:raise ValueError('Reconciled seismic story weights are required.')
    try:
        from components.modal.rayleigh_ledger_audit import verify_storey_coverage, verify_rayleigh_sum, verify_storey_elevations
    except ModuleNotFoundError:
        # Older independently exported OpenSees_Runtime_V118 bundles may not
        # contain newly introduced optional helper files. Keep this historical
        # launcher operational without changing its numerical model.
        def verify_storey_coverage(diaps, ledger):
            expected=[(int(d['storey_number']),int(d['master_tag'])) for d in diaps]
            actual=[(int(r['story_number']),int(r['master_node_tag'])) for r in ledger]
            if (not expected or len(set(expected))!=len(expected) or
                len(set(actual))!=len(actual) or
                len({tag for _,tag in expected})!=len(expected) or
                len({tag for _,tag in actual})!=len(actual) or set(expected)!=set(actual)):
                raise ValueError('Incomplete or duplicated Rayleigh diaphragm master ledger')
            return len(actual)
        def verify_rayleigh_sum(story_rows, *, g=GRAVITY_M_S2):
            vals=[(float(r['weight_kN']),float(r['force_kN']),float(r['displacement_m'])) for r in story_rows]
            if not vals or any(not all(math.isfinite(t) for t in row) or row[0]<=0 or row[1]<=0 for row in vals):
                raise ValueError('Invalid Rayleigh storey terms')
            num=math.fsum(w*d*d for w,f,d in vals)
            den=g*math.fsum(f*d for w,f,d in vals)
            if not math.isfinite(g) or g<=0 or num<=0 or den<=0:
                raise ValueError('Invalid Rayleigh period denominator')
            return {'storey_count':len(vals),'period_s':2*math.pi*math.sqrt(num/den),
                    'status':'NUMERICAL_RECONSTRUCTION_ONLY'}

    config_file=folder/'OpenSees_Complete_Model_Config_V118.json'
    if not config_file.is_file():raise FileNotFoundError('Current Rayleigh model configuration is missing.')
    with model.open(encoding='utf-8-sig') as stream: model_data=json.load(stream)
    covered_storeys=verify_storey_coverage(model_data['diaphragms'],rows)
    # The legacy runtime fallback keeps earlier exported launchers working,
    # but must apply the same model-vs-ledger height check.
    if 'verify_storey_elevations' in locals():
        verify_storey_elevations(model_data['diaphragms'],rows,model_data['base_z_m'])
    else:
        base_z=float(model_data['base_z_m'])
        heights_by_master={int(d['master_tag']):float(d['master_xyz'][2])-base_z
                           for d in model_data['diaphragms']}
        for record in rows:
            master=int(record['master_node_tag'])
            expected=heights_by_master[master]
            actual=float(record['height_m'])
            if not all(math.isfinite(v) and v>0 for v in (expected,actual)) or abs(expected-actual)>1e-6:
                raise ValueError('Rayleigh storey height differs from source diaphragm master geometry')

    rows.sort(key=lambda r:float(r['height_m']))
    heights=[float(r['height_m']) for r in rows]
    weights=[float(r['dead_load_kN'])+.6*float(r['storage_live_load_kN'])+.3*float(r['other_live_load_kN']) for r in rows]
    from components.modal.rayleigh_mass_audit import audit_rayleigh_mass_elevations
    mass_elevation_audit=audit_rayleigh_mass_elevations(model_data,rows)
    if any(not math.isfinite(h) or h<=0 for h in heights) or any(b<=a for a,b in zip(heights,heights[1:])):
        raise ValueError('Story heights must be finite, positive, and strictly increasing from the seismic base.')
    if any(not math.isfinite(w) or w<=0 for w in weights):raise ValueError('Positive finite reconciled seismic story weights are required.')
    H=heights[-1]
    result={'story_weights_sha256':hashlib.sha256((folder/'NBC105_ESM_Story_Weights_Assembled_V118.csv').read_bytes()).hexdigest(),'standard':'NBC 105:2025 §5.1.1-§5.1.3','model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'gravity_state':'assembled sustained gravity','limit_state':state,'height_m':H,'height_basis':'story-ledger elevations from seismic base; confirm qualifying basements are excluded per §5.1.2','gravity_acceleration_m_s2':GRAVITY_M_S2,'rayleigh_equation':'T1 = 2*pi*sqrt(sum(Wi*di^2)/(g*sum(Fi*di)))','torsion':'diaphragm rotations restrained during reference lateral perturbation','diagnostic_only':True}
    result['model_config_sha256']=hashlib.sha256(config_file.read_bytes()).hexdigest()
    result['mass_elevation_audit']=mass_elevation_audit
    result['gravity_profile'] = gravity_profile
    if empirical_settings is None:
        prefix = 'NBC105_Rayleigh_Preliminary_V126_' + state + '_Legacy_Reference'
    else:
        prefix=rayleigh_result_prefix(state)
        result['empirical_esm_settings'] = dict(empirical_settings)
    members_by_master={int(d['master_tag']): d['slave_node_tags'] for d in model_data['diaphragms']}
    supports=tuple(map(int, model_data['supports']))
    if not supports:
        raise ValueError('Source support nodes are required for the Rayleigh reaction balance.')
    wb=Workbook();summary=wb.active;summary.title='Summary';summary.append(['Axis','Aw (m2)','Empirical T (s)','Amplified empirical T (s)','Rayleigh T (s)','Adopted T (s)'])
    fig=Figure(figsize=(11,6),layout='constrained');axes=fig.subplots(1,2)
    for axis,aw in [('X',awx),('Y',awy)]:
        aw=float(aw)
        if not math.isfinite(aw) or aw<=0:raise ValueError('Directional Aw must be finite, positive, and reviewed against first-story walls/openings.')
        empirical=empirical_period_s(H,'concrete shear-wall',aw)  # [REF NBC105-2025 §5.1.2, printed p. 29]
        if empirical_settings is None:
            seed = None
            k=1. if empirical<=.5 else 2. if empirical>=2.5 else 1.+(empirical-.5)/2.
            shape=[w*h**k for w,h in zip(weights,heights)]
            forces=[reference_fraction*sum(weights)*s/sum(shape) for s in shape]
        else:
            empirical, seed, forces = empirical_esm_reference(
                rows, height_m=H, aw_m2=aw, state=state, settings=empirical_settings)
            k = seed['period_exponent_k']
            print(f'[EMPIRICAL ESM SEED] {state} {axis} {json.dumps(seed)}', flush=True)
        build = build_complete_model(folder,mode='elastic',preload=True,limit_state=state)
        dof=1 if axis=='X' else 2
        masters=[int(r['master_node_tag']) for r in rows]
        # Establish the torsion-suppressed gravity equilibrium BEFORE taking
        # the baseline. Adding SP constraints with the lateral loads mixes a
        # gravity redistribution into di and makes the quotient amplitude-dependent.
        ops.timeSeries('Constant',990000);ops.pattern('Plain',990000,990000)
        for n in masters:ops.sp(n,6,0.)
        configure_nonlinear_static(ops,system='UmfPack',tolerance=1e-8,max_iterations=100)
        ops.integrator('LoadControl',0.)
        if ops.analyze(1)!=0:raise RuntimeError('Torsion-suppressed gravity equilibration failed.')
        ops.loadConst('-time',0.)
        baseline=[_diaphragm_translation(ops,n,members_by_master[n],dof)[0] for n in masters]
        retained_baseline=[ops.nodeDisp(n,dof) for n in masters]
        ops.reactions()
        base_before=math.fsum(ops.nodeReaction(n,dof) for n in supports)
        tag=990001;ops.timeSeries('Linear',tag);ops.pattern('Plain',tag,tag)
        for n,f in zip(masters,forces):
            load=[0.]*6;load[dof-1]=f;ops.load(n,*load)
        configure_nonlinear_static(ops,system='UmfPack',tolerance=1e-8,max_iterations=100,nsteps=1)
        status=ops.analyze(1)
        if status!=0:
            raise RuntimeError(f'{axis} preliminary lateral analysis failed (OpenSees {status}).')
        load_factor=ops.getLoadFactor(tag)
        if not math.isclose(load_factor,1.,rel_tol=0.,abs_tol=1e-10):
            raise RuntimeError(f'{axis} Rayleigh load factor {load_factor:g} differs from 1.')
        ops.reactions()
        base_increment=math.fsum(ops.nodeReaction(n,dof) for n in supports)-base_before
        force_total=math.fsum(forces)
        reaction_error=abs(base_increment+force_total)/force_total
        if not reaction_error <= 0.001:
            raise RuntimeError(f'{axis} incremental base reaction imbalance: {reaction_error:.3%}.')
        samples=[_diaphragm_translation(ops,n,members_by_master[n],dof) for n in masters]
        u=[value-b for (value,_),b in zip(samples,baseline)]
        retained=[ops.nodeDisp(n,dof)-b for n,b in zip(masters,retained_baseline)]
        kinematic_audit=dict(
            status='VERIFIED_FLOOR_TRANSLATIONS', steps=1, pattern_factor=load_factor,
            incremental_base_reaction_kN=base_increment, relative_reaction_error=reaction_error,
            max_floor_translation_spread_m=max(spread for _,spread in samples),
            max_retained_translation_difference_m=max(abs(a-b) for a,b in zip(u,retained)))
        denominator=GRAVITY_M_S2*sum(f*d for f,d in zip(forces,u))
        numerator=sum(w*d*d for w,d in zip(weights,u))
        if not math.isfinite(denominator) or denominator<=0:raise ValueError(f'{axis} Rayleigh denominator is nonpositive or non-finite; inspect displacement signs and constraints.')
        if not math.isfinite(numerator) or numerator<=0:raise ValueError(f'{axis} Rayleigh numerator is nonpositive or non-finite; inspect seismic weights and displacements.')
        period=2*math.pi*math.sqrt(numerator/denominator)
        audit=verify_rayleigh_sum([{'weight_kN':w,'force_kN':f,'displacement_m':d} for w,f,d in zip(weights,forces,u)])
        if audit['storey_count'] != covered_storeys or not math.isclose(period,audit['period_s'],rel_tol=1e-10):
            raise RuntimeError(f'{axis}: incomplete or inconsistent all-storey Rayleigh reconstruction')
        if not math.isfinite(period) or period<=0:raise ValueError(f'{axis} Rayleigh period is nonpositive or non-finite.')
        result[axis]=dict(Aw_m2=aw,empirical_period_s=empirical,amplified_empirical_s=amplified_period_s(empirical),period_s=period,adopted_period_s=min(period,amplified_period_s(empirical)),reference_force_exponent_k=k,reference_force_total_kN=sum(forces),rayleigh_numerator_kN_m2=numerator,rayleigh_denominator_gFiDi_kN_m2_s2=denominator,storey_audit=audit,rows=[dict(story=r['story_name'],height_m=float(r['height_m']),master_node=n,weight_kN=w,force_kN=f,displacement_m=d) for r,n,w,f,d in zip(rows,masters,weights,forces,u)])
        result[axis]['kinematic_audit']=kinematic_audit
        result[axis]['stiffness_basis'] = build['stiffness_basis']
        if seed is not None:
            result[axis]['empirical_esm_reference'] = seed
        for record,raw in zip(result[axis]['rows'],retained):
            record['retained_node_displacement_diagnostic_m']=raw
            record['constrained_floor_node_count']=len(members_by_master[record['master_node']])
        sheet=wb.create_sheet(axis+' Rayleigh');sheet.append(['Story','Height (m)','Master node','Wi (kN)','Fi (kN)','di (m)','Wi di2 (kN m2)','Fi di (kN m)'])
        for rr in result[axis]['rows']:
            excel_row=sheet.max_row+1
            sheet.append([rr['story'],rr['height_m'],rr['master_node'],rr['weight_kN'],
                          rr['force_kN'],rr['displacement_m'],
                          f'=D{excel_row}*F{excel_row}^2',
                          f'=E{excel_row}*F{excel_row}'])
        end_row=sheet.max_row
        sum_row=end_row+1
        sheet.append(['SUM OF NBC §5.1.1 TERMS',None,None,None,None,None,
                      f'=SUM(G2:G{end_row})',f'=SUM(H2:H{end_row})'])
        period_row=sum_row+1
        sheet.append(['INDEPENDENT EXCEL T_R (s)',
                      f'=IF(H{sum_row}>0,2*PI()*SQRT(G{sum_row}/({GRAVITY_M_S2!r}*H{sum_row})),"")'])
        sheet.append(['SOLVER/PYTHON T_R (s)',period])
        sheet.append(['EXCEL - PYTHON T_R (s)',
                      f'=IF(B{period_row}="","",B{period_row}-B{period_row+1})'])
        if seed is None:
            sheet.append(['Legacy reference lateral load scale',reference_fraction])
        else:
            sheet.append(['Empirical ESM seed period (s)',seed['period_s']])
            sheet.append(['Empirical ESM seed coefficient',seed['design_coefficient_Cd']])
        sheet.append(['Reference Fi total (kN)',sum(forces)])
        sheet.append(['Reference Fi shape exponent k',k])
        sheet.append(['k basis','amplified empirical period' if seed else 'legacy unamplified empirical period'])
        sheet.append(['Source model SHA256',result['model_sha256']])
        sheet.append(['Source weight ledger SHA256',result['story_weights_sha256']])
        sheet.append(['Limit state',state])
        sheet.append(['Elastic COM displacement','constrained floor translation increment from torsion-suppressed gravity'])
        for key,value in kinematic_audit.items():
            sheet.append([key,value])
        sheet.append(['Independent verification', 'OPEN: native ETABS response and stiffness/restraint matching'])
        for col,width in (('A',38),('B',21),('C',17),('D',20),
                          ('E',20),('F',20),('G',24),('H',20)):
            sheet.column_dimensions[col].width=width
        summary.append([axis,aw,empirical,amplified_period_s(empirical),period,min(period,amplified_period_s(empirical))])
        heights=[float(r['height_m']) for r in rows]
        axes[0].plot([v*1000 for v in u],heights,label=f'{axis}: T_R={period:.3f} s')
        axes[1].plot(forces,heights,label=axis)
    for ax in axes:ax.grid(alpha=.25);ax.legend();ax.set_ylabel('Elevation (m)')
    axes[0].set(title='Reference lateral displacement profiles',xlabel='Incremental translation (mm)')
    axes[1].set(title='Reference lateral floor forces',xlabel='Reference force Fi (kN)')
    fig.suptitle(f'NBC 105:2025 Rayleigh period estimate | {state} preliminary elastic perturbation')
    for ext in ('png','pdf'):fig.savefig(out/(prefix+'.'+ext),dpi=300)
    for sheet in wb:sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
    wb.save(out/(prefix+'.xlsx'))
    result['method_version']=RAYLEIGH_METHOD_VERSION if empirical_settings is not None else 126
    result['displacement_basis']=RAYLEIGH_DISPLACEMENT_BASIS
    result['opensees_version']=ops.version()
    result['reference_fraction']=reference_fraction if empirical_settings is None else None
    result['baseline_method']='Equilibrate torsion-suppressed gravity before applying reference forces; use incremental translation.'
    (out/(prefix+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    import sys
    print(json.dumps(run(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),
                         reference_fraction=float(sys.argv[4]) if len(sys.argv)>4 else .01,
                         limit_state=sys.argv[5] if len(sys.argv)>5 else 'ULS',
                         empirical_settings=json.loads(sys.argv[6]) if len(sys.argv)>6 else None),indent=2))
