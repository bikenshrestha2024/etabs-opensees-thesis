"""NBC 105:2025 §5.1.1 force/displacement Rayleigh estimate.

Reference: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
The small reference lateral forces determine a displacement shape. Their
amplitude cancels in the Rayleigh quotient for a fixed linear stiffness.
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


@timed_outputs('Preliminary Rayleigh X-Y analysis','folder')
def run(folder, awx, awy, reference_fraction=.01, limit_state='ULS',
        output_dir=None):
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
        from components.modal.rayleigh_ledger_audit import verify_storey_coverage, verify_rayleigh_sum
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
        def verify_rayleigh_sum(story_rows, *, g=9.81):
            vals=[(float(r['weight_kN']),float(r['force_kN']),float(r['displacement_m'])) for r in story_rows]
            if not vals or any(not all(math.isfinite(t) for t in row) or row[0]<=0 or row[1]<=0 for row in vals):
                raise ValueError('Invalid Rayleigh storey terms')
            num=math.fsum(w*d*d for w,f,d in vals)
            den=g*math.fsum(f*d for w,f,d in vals)
            if not math.isfinite(g) or g<=0 or num<=0 or den<=0:
                raise ValueError('Invalid Rayleigh period denominator')
            return {'storey_count':len(vals),'period_s':2*math.pi*math.sqrt(num/den),
                    'status':'NUMERICAL_RECONSTRUCTION_ONLY'}

    with model.open(encoding='utf-8-sig') as stream: model_data=json.load(stream)
    covered_storeys=verify_storey_coverage(model_data['diaphragms'],rows)
    rows.sort(key=lambda r:float(r['height_m']))
    heights=[float(r['height_m']) for r in rows]
    weights=[float(r['dead_load_kN'])+.6*float(r['storage_live_load_kN'])+.3*float(r['other_live_load_kN']) for r in rows]
    if any(not math.isfinite(h) or h<=0 for h in heights) or any(b<=a for a,b in zip(heights,heights[1:])):
        raise ValueError('Story heights must be finite, positive, and strictly increasing from the seismic base.')
    if any(not math.isfinite(w) or w<=0 for w in weights):raise ValueError('Positive finite reconciled seismic story weights are required.')
    H=heights[-1]
    result={'story_weights_sha256':hashlib.sha256((folder/'NBC105_ESM_Story_Weights_Assembled_V118.csv').read_bytes()).hexdigest(),'standard':'NBC 105:2025 §5.1.1-§5.1.3','model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'gravity_state':'assembled sustained gravity','limit_state':state,'height_m':H,'height_basis':'story-ledger elevations from seismic base; confirm qualifying basements are excluded per §5.1.2','gravity_acceleration_m_s2':9.81,'rayleigh_equation':'T1 = 2*pi*sqrt(sum(Wi*di^2)/(g*sum(Fi*di)))','torsion':'diaphragm rotations restrained during reference lateral perturbation','diagnostic_only':True}
    prefix='NBC105_Rayleigh_Preliminary_V123'+('' if state=='ULS' else '_'+state)
    wb=Workbook();summary=wb.active;summary.title='Summary';summary.append(['Axis','Aw (m2)','Empirical T (s)','Amplified empirical T (s)','Rayleigh T (s)','Adopted T (s)'])
    fig=Figure(figsize=(11,6),layout='constrained');axes=fig.subplots(1,2)
    for axis,aw in [('X',awx),('Y',awy)]:
        aw=float(aw)
        if not math.isfinite(aw) or aw<=0:raise ValueError('Directional Aw must be finite, positive, and reviewed against first-story walls/openings.')
        empirical=.075/math.sqrt(aw)*H**.75
        k=1. if empirical<=.5 else 2. if empirical>=2.5 else 1.+(empirical-.5)/2.
        shape=[w*float(r['height_m'])**k for w,r in zip(weights,rows)]
        forces=[reference_fraction*sum(weights)*s/sum(shape) for s in shape]
        build_complete_model(folder,mode='elastic',preload=True,limit_state=state)
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
        baseline=[ops.nodeDisp(n,dof) for n in masters]
        tag=990001;ops.timeSeries('Linear',tag);ops.pattern('Plain',tag,tag)
        for n,f in zip(masters,forces):
            load=[0.]*6;load[dof-1]=f;ops.load(n,*load)
        ops.wipeAnalysis();configure_nonlinear_static(ops,system='UmfPack',tolerance=1e-8,max_iterations=100)
        ops.integrator('LoadControl',.1)
        if ops.analyze(10)!=0:raise RuntimeError(f'{axis} preliminary lateral analysis did not converge; no Rayleigh value was accepted.')
        u=[ops.nodeDisp(n,dof)-b for n,b in zip(masters,baseline)]
        denominator=9.81*sum(f*d for f,d in zip(forces,u))
        numerator=sum(w*d*d for w,d in zip(weights,u))
        if not math.isfinite(denominator) or denominator<=0:raise ValueError(f'{axis} Rayleigh denominator is nonpositive or non-finite; inspect displacement signs and constraints.')
        if not math.isfinite(numerator) or numerator<=0:raise ValueError(f'{axis} Rayleigh numerator is nonpositive or non-finite; inspect seismic weights and displacements.')
        period=2*math.pi*math.sqrt(numerator/denominator)
        audit=verify_rayleigh_sum([{'weight_kN':w,'force_kN':f,'displacement_m':d} for w,f,d in zip(weights,forces,u)])
        if audit['storey_count'] != covered_storeys or not math.isclose(period,audit['period_s'],rel_tol=1e-10):
            raise RuntimeError(f'{axis}: incomplete or inconsistent all-storey Rayleigh reconstruction')
        if not math.isfinite(period) or period<=0:raise ValueError(f'{axis} Rayleigh period is nonpositive or non-finite.')
        result[axis]=dict(Aw_m2=aw,empirical_period_s=empirical,amplified_empirical_s=1.25*empirical,period_s=period,adopted_period_s=min(period,1.25*empirical),reference_force_exponent_k=k,reference_force_total_kN=sum(forces),rayleigh_numerator_kN_m2=numerator,rayleigh_denominator_gFiDi_kN_m2_s2=denominator,storey_audit=audit,rows=[dict(story=r['story_name'],height_m=float(r['height_m']),master_node=n,weight_kN=w,force_kN=f,displacement_m=d) for r,n,w,f,d in zip(rows,masters,weights,forces,u)])
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
                      f'=IF(H{sum_row}>0,2*PI()*SQRT(G{sum_row}/(9.81*H{sum_row})),"")'])
        sheet.append(['SOLVER/PYTHON T_R (s)',period])
        sheet.append(['EXCEL - PYTHON T_R (s)',
                      f'=IF(B{period_row}="","",B{period_row}-B{period_row+1})'])
        sheet.append(['Reference lateral load scale',reference_fraction])
        sheet.append(['Reference Fi total (kN)',sum(forces)])
        sheet.append(['Reference Fi shape exponent k',k])
        sheet.append(['k basis','preliminary EMPIRICAL period; not iterative adopted k'])
        sheet.append(['Source model SHA256',result['model_sha256']])
        sheet.append(['Source weight ledger SHA256',result['story_weights_sha256']])
        sheet.append(['Limit state',state])
        sheet.append(['Elastic COM displacement','incremental from torsion-suppressed gravity baseline'])
        sheet.append(['Independent verification', 'OPEN: native ETABS response and stiffness/restraint matching'])
        for col,width in (('A',38),('B',21),('C',17),('D',20),
                          ('E',20),('F',20),('G',24),('H',20)):
            sheet.column_dimensions[col].width=width
        summary.append([axis,aw,empirical,1.25*empirical,period,min(period,1.25*empirical)])
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
    result['method_version']=125
    result['reference_fraction']=reference_fraction
    result['baseline_method']='Equilibrate torsion-suppressed gravity before applying reference forces; use incremental translation.'
    (out/(prefix+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    import sys
    print(json.dumps(run(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),
                         reference_fraction=float(sys.argv[4]) if len(sys.argv)>4 else .01,
                         limit_state=sys.argv[5] if len(sys.argv)>5 else 'ULS'),indent=2))
