"""Actual signed elastic stability checks; diagnostic EL profile, kN-m-s.

The reference EL is explicitly not an eligible high-rise ULS ESM design case.
Source hierarchy: NBC 105:2025 supplies the seismic coefficient/EL actions; IS 16700:2023 §7.2(d) supplies the compulsory project initial combination. NBC §§8.1.1.3/9.3.1.3 require P-Delta in time histories. This module solves initial checks only; it does not certify state transfer into a time-history solver. WARNING: current D/IL factor classification uses seismic mass_factors as a proxy: review explicit ETABS load categories before accepting results. [REF REVIEW_MAIN/00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md]
Every sign/direction builds a fresh domain; the caller rebuilds its final state.
"""

__release__ = '134'
from OpenSees_Timing_V130 import timed_outputs
from pathlib import Path
import hashlib
import json
import math
import os
import time


def _initial_pdelta_fingerprint(inputs, sources, *, support_case, mass_policy,
                                limit_state):
    """Source- and profile-bound key; no saved solver state is reused.

    Each input and implementation dependency is hashed independently to
    avoid ambiguous concatenation of distinct byte streams. The key does
    not establish native ETABS parity or certify transitive dependencies.
    """
    from components.model.support_case_contract import normalize_support_case
    case=normalize_support_case(support_case)
    mass_policy=str(mass_policy).strip().upper()
    limit_state=str(limit_state).strip().upper()
    if mass_policy not in ("SOURCE_DISTRIBUTED", "STORY_LUMPED_NBC"):
        raise ValueError("Unknown seismic mass operator policy")
    if limit_state not in ("ULS", "SLS"):
        raise ValueError("Initial P-Delta limit state must be ULS or SLS")
    if len(inputs)!=3 or len(sources)!=3:
        raise ValueError("Initial P-Delta fingerprint requires three inputs and three sources")
    hasher=hashlib.sha256(b"initial-pdelta-evidence-v2\0")
    hasher.update(json.dumps(
        dict(support_case=case, seismic_mass_policy=mass_policy, limit_state=limit_state),
        sort_keys=True, separators=(',', ':')).encode('ascii'))
    for kind,paths in (("input", inputs), ("source", sources)):
        for index,path in enumerate(paths):
            selected=Path(path)
            if not selected.is_file():
                raise FileNotFoundError("Initial P-Delta dependency missing: "+str(selected))
            hasher.update(f"{kind}:{index}:{selected.name}\0".encode('utf-8'))
            with selected.open('rb') as stream:
                hasher.update(hashlib.file_digest(stream, 'sha256').digest())
    return hasher.hexdigest()


@timed_outputs('Initial signed P-Delta checks','folder')
def ensure_initial_checks(folder):
    folder=Path(folder)
    names=['OpenSees_Complete_Model_Data_V118.json','OpenSees_Complete_Model_Config_V118.json','OpenSees_Initial_PDelta_Input_V124.json']
    import OpenSees_Complete_Export_V118 as assembly
    import OpenSees_Analysis_Stack_V110 as analysis
    from components.model.support_case_contract import normalize_support_case
    from components.inputs.output_contract import atomic_json
    selected_case=normalize_support_case(os.environ.get('OPENSEES_SUPPORT_CASE','PHYSICAL_32'))
    selected_mass_policy=os.environ.get('OPENSEES_SEISMIC_MASS_POLICY','SOURCE_DISTRIBUTED').strip().upper()
    # Initial signed IS16700 preflight is ULS by default, independent of
    # a subsequent SLS modal/ESM stiffness run; never inherit OPENSEES_LIMIT_STATE.
    selected_state=os.environ.get('OPENSEES_INITIAL_PDELTA_LIMIT_STATE','ULS').strip().upper()
    digest=_initial_pdelta_fingerprint(
        [folder/name for name in names],
        [Path(globals().get('_component_source',__file__)),
         Path(getattr(assembly,'_component_source',assembly.__file__)),
         Path(getattr(analysis,'_component_source',analysis.__file__))],
        support_case=selected_case, mass_policy=selected_mass_policy, limit_state=selected_state)
    output=folder/'OpenSees_IS16700_Initial_PDelta_Results.json'
    if output.is_file():
        old=json.loads(output.read_text(encoding='utf-8-sig'))
        if isinstance(old,dict) and all(
                isinstance(old.get(f'PD_INIT_EL_{axis}_{sign}'),dict)
                and old[f'PD_INIT_EL_{axis}_{sign}'].get('input_sha256')==digest
                and old[f'PD_INIT_EL_{axis}_{sign}'].get('converged') is True
                and old[f'PD_INIT_EL_{axis}_{sign}'].get('support_case')==selected_case
                and old[f'PD_INIT_EL_{axis}_{sign}'].get('seismic_mass_policy')==selected_mass_policy
                and old[f'PD_INIT_EL_{axis}_{sign}'].get('limit_state')==selected_state
                for axis in ('X','Y') for sign in ('PLUS','MINUS')):
            print('IS 16700: reusing four converged signed-case reports with matching source, support, mass and state fingerprints; native parity remains unverified.',flush=True)
            return old
    data=json.loads((folder/names[0]).read_text(encoding='utf-8-sig'))
    cfg=json.loads((folder/names[1]).read_text(encoding='utf-8-sig'))
    reference=json.loads((folder/names[2]).read_text(encoding='utf-8-sig'))
    raw=data.get('unfactored_patterns')
    if not raw:raise ValueError('Rebuild the assembled export with V124 to retain unfactored D/IL pattern loads.')
    factors={}
    for pattern in raw:
        mass=cfg['mass_factors'].get(pattern)
        if mass==1:factors[pattern]=1.2
        elif mass in (.3,.6) or 'live' in pattern.lower():factors[pattern]=.5
        else:raise ValueError(f'Classify {pattern!r} explicitly as dead or imposed load before initial P-Delta checks.')
    import openseespy.opensees as ops
    from OpenSees_Complete_Export_V118 import build_complete_model
    from OpenSees_Analysis_Stack_V110 import run_gravity_stage
    from components.model.support_case_contract import solver_reaction_support_tags
    outcomes={}
    for axis in ('X','Y'):
        profile=reference[axis]
        for label,sign in [('PLUS',1),('MINUS',-1)]:
            name=f'PD_INIT_EL_{axis}_{label}'
            print(name+': building 1.2D + 0.5IL '+('+' if sign>0 else '-')+' 1.5EL reference',flush=True)
            started=time.perf_counter()
            built=build_complete_model(folder,preload=False,limit_state=selected_state)
            build_elapsed_s=time.perf_counter()-started
            support_nodes=solver_reaction_support_tags(built, selected_case)
            for tag in range(700001,700001+len(data['gravity'])):ops.remove('loadPattern',tag)
            ops.timeSeries('Linear',970001);ops.pattern('Plain',970001,970001)
            total=0.
            for pattern,values in raw.items():
                factor=factors[pattern]
                for node,vector in values.items():ops.load(int(node),*[factor*v for v in vector]);total-=factor*vector[2]
            gravity_started=time.perf_counter()
            gravity=run_gravity_stage(ops,support_nodes,total,model_nodes=list(map(int,data['nodes'])),nsteps=20,system='UmfPack')
            gravity_elapsed_s=time.perf_counter()-gravity_started
            ops.timeSeries('Linear',970002);ops.pattern('Plain',970002,970002)
            for row in profile['stories']:
                force=sign*1.5*row['lateral_force_kN']
                ops.load(int(row['master_node_tag']),force if axis=='X' else 0.,force if axis=='Y' else 0.,0.,0.,0.,0.)
            ops.wipeAnalysis();ops.constraints('Transformation');ops.numberer('RCM');ops.system('UmfPack')
            ops.test('NormDispIncr',1e-8,40);ops.algorithm('Newton');ops.integrator('LoadControl',.05);ops.analysis('Static')
            lateral_started=time.perf_counter()
            steps=0
            for i in range(20):
                code=ops.analyze(1)
                if code!=0:raise RuntimeError(f'{name} failed at lateral increment {i+1}, code {code}')
                steps+=1
            ops.reactions()
            dof=1 if axis=='X' else 2
            reaction=sum(ops.nodeReaction(n,dof) for n in support_nodes)
            applied=sign*1.5*sum(r['lateral_force_kN'] for r in profile['stories'])
            error=abs(reaction+applied)/abs(applied)*100
            displacements={str(g['master_tag']):ops.nodeDisp(g['master_tag']) for g in data['diaphragms']}
            if not math.isfinite(error) or error>.01:raise RuntimeError(f'{name}: horizontal equilibrium error {error}%')
            outcomes[name]=dict(converged=True,input_sha256=digest,result_file=str(output),combination='1.2D+0.5IL'+('+' if sign>0 else '-')+'1.5EL',
                diagnostic_EL_reference=True,EL_basis=profile['basis'],period_s=profile['period_s'],pattern_factors=factors,
                support_case=selected_case,seismic_mass_policy=selected_mass_policy,limit_state=selected_state,
                actual_solver_support_count=len(support_nodes),
                runtime_support_tags_sha256=hashlib.sha256(json.dumps(support_nodes).encode('ascii')).hexdigest(),
                build_elapsed_s=round(build_elapsed_s,3),gravity_elapsed_s=round(gravity_elapsed_s,3),
                lateral_elapsed_s=round(time.perf_counter()-lateral_started,3),
                gravity=gravity,lateral_steps=steps,applied_horizontal_kN=applied,support_horizontal_kN=reaction,equilibrium_error_percent=error,master_displacements_m_rad=displacements,
                result_note='Actual fresh-domain elastic PDelta analysis at selected solver support tags; native ETABS edge/MPC transfer and high-rise ESM eligibility are NOT_VERIFIED. Wind cases require separate project wind loads.')
            print(f'{name}: PASS | V={applied:.6f} kN | equilibrium error={error:.6g}%',flush=True)
    atomic_json(output, outcomes)
    return outcomes
