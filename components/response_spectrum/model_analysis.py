"""Model MRSM: mode-by-mode OpenSees RSA, CQC, NBC force scaling and drift."""
from components.nbc105.constants import GRAVITY_M_S2
from pathlib import Path
import csv,json,math,time
import numpy as np


def _runtime_repo_root():
    """Repository/runtime root in both direct-module and exec facade contexts.

    Root-level compatibility facades set _component_source to the actual
    components/<package>/<module>.py. __file__ alone then names the facade
    and its parents[2] would point outside the active project.
    """
    from components.shared.repository_paths import runtime_repo_root
    return runtime_repo_root(__file__, globals().get("_component_source"))
from OpenSees_Timing_V130 import timed_outputs
from NBC105_Spectrum_Scaling_V115 import spectral_shape_ch
from OpenSees_Response_Checks_V132 import write_csv,drift_check

def cqc_matrix(omega,zeta=.05):
    """Compatibility wrapper: Clause 7 owns the CQC correlation equation."""
    from components.nbc105.clause_07_modal_response_spectrum import cqc_correlation_matrix
    return np.asarray(cqc_correlation_matrix(omega,zeta),dtype=float)

def combine(values,rho):
    a=np.asarray(values,float)
    return np.sqrt(np.maximum(0.,np.einsum('i...,ij,j...->...',a,rho,a)))

def design_cd(T,cfg):
    """Use the canonical Clause 7 modal ordinate (Clause 6 shared divisor)."""
    from components.nbc105.clause_07_modal_response_spectrum import modal_design_coefficient
    elastic=spectral_shape_ch(T,cfg['soil'],'dynamic')*float(cfg['Z'])*float(cfg['I'])
    return modal_design_coefficient(elastic if cfg['limit_state']=='ULS' else .2*elastic,
            ductility=float(cfg['rmu']) if cfg['limit_state']=='ULS' else None,
            overstrength=float(cfg['omegau']) if cfg['limit_state']=='ULS' else float(cfg['omegas']),
            limit_state=cfg['limit_state'])

@timed_outputs('Model modal response spectrum analysis','output_dir')
def run_model_spectrum(folder,config,output_dir):
    import openseespy.opensees as ops
    from OpenSees_Complete_Export_V118 import build_complete_model
    from components.model.support_case_contract import (normalize_support_case, require_runtime_support_case, solver_reaction_support_tags)
    from NBC105_Analysis_Settings_V109 import calculate_esm
    from OpenSees_Earthquake_Analysis_NBC105_V111 import read_story_csv
    from OpenSees_Modal_Analysis_NBC105_V111 import run_nbc105_modal_audit
    folder=Path(folder).resolve();out=Path(output_dir)
    from components.inputs.project_workbooks import require_source_state
    require_source_state(folder,config['limit_state'])
    out.mkdir(parents=True,exist_ok=True)
    data=json.loads((folder/'OpenSees_Complete_Model_Data_V118.json').read_text(encoding='utf-8-sig'))
    manifest=json.loads((folder/'OpenSees_Export_Manifest_V118.json').read_text(encoding='utf-8-sig'))
    stories=read_story_csv(folder/manifest['esm_story_weight_csv']);groups=sorted(data['diaphragms'],key=lambda g:g['master_xyz'][2]);state=config['limit_state']
    overrides=folder/'OpenSees_Element_Overrides_V125.json'
    if overrides.is_file() and json.loads(overrides.read_text(encoding='utf-8-sig')).get('active'):raise ValueError('MRSM requires the elastic baseline; nonlinear replacements are unsupported.')
    if not all(math.isfinite(float(config[k])) and float(config[k])>0 for k in ('Z','I','rmu','omegau','omegas','T1_X','T1_Y')):raise ValueError('Spectrum inputs and adopted periods must be positive.')
    if not 0<float(config.get('damping',.05))<=.05:raise ValueError('Damping must be positive and no greater than 5 percent.')
    from components.shared.eigen_solver import validated_mode_count
    requested_modes = validated_mode_count(config.get('nmodes',40), name='nmodes')
    import hashlib
    from OpenSees_Model_Audit_V130 import implementation_digest,modal_numeric_digest
    source_signature=implementation_digest();numeric_signature=modal_numeric_digest()
    model_signature=hashlib.sha256((folder/'OpenSees_Complete_Model_Data_V118.json').read_bytes()).hexdigest()
    print('[STIFFNESS REVIEW] Production elastic wall shells retain source gross in-plane stiffness. Review NBC Table 3-1 effective wall EI and match ETABS before design use.',flush=True)
    results={}
    for axis,dof in [('X',1),('Y',2)]:
        if axis not in config.get('axes',['X','Y']):continue
        __import__('os').environ['OPENSEES_GRAVITY_PROFILE']=config.get('gravity_profile',__import__('os').environ.get('OPENSEES_GRAVITY_PROFILE','AS_CONFIGURED'))
        import os
        selected_support=normalize_support_case(config.get('support_case','PHYSICAL_32'))
        os.environ['OPENSEES_SUPPORT_CASE']=selected_support
        selected_mass=str(config.get('seismic_mass_policy','SOURCE_DISTRIBUTED')).strip().upper()
        if selected_mass not in ('SOURCE_DISTRIBUTED','STORY_LUMPED_NBC'):
            raise ValueError('Unknown selected MRSM mass policy')
        os.environ['OPENSEES_SEISMIC_MASS_POLICY']=selected_mass
        print('[MRSM START]',state,axis,'support_case='+selected_support,'mass='+selected_mass,flush=True)
        built=build_complete_model(folder,mode='elastic',preload=True,limit_state=state)
        support_evidence=require_runtime_support_case(selected_support,built)
        print('[MRSM SELECTED SUPPORT CASE VERIFIED]',support_evidence,flush=True)
        print('[MRSM STAGE]',state,axis,'gravity converged; solving eigenmodes, then CQC response and NBC force scaling. This is one state of the selected batch.',flush=True)
        from components.modal.analysis import modal_response_nodes
        modal=run_nbc105_modal_audit(
            ops, nmodes=requested_modes,
            output_dir=out/('Modal_'+axis),
            story_nodes=modal_response_nodes(data))
        modal.update(limit_state=state,model_sha256=model_signature,implementation_sha256=source_signature,modal_numeric_sha256=numeric_signature)
        # This modal reference belongs to this MRSM model/gravity state.
        # Never populate legacy all-stage results with a hidden cache copy.
        # Keep it with the originating MRSM solver outputs and case provenance.
        from components.inputs.output_contract import safe_component
        gravity_label=safe_component(
            __import__('os').environ.get('OPENSEES_GRAVITY_PROFILE','AS_CONFIGURED'))
        cache=out/'Modal_Reference'/state/gravity_label
        cache.mkdir(parents=True,exist_ok=True)
        from OpenSees_Timing_V130 import StageTimer
        cache_timer=StageTimer(cache,'MRSM modal reference cache export')
        (cache/'NBC105_Modal_V111.json').write_text(json.dumps(modal,indent=2),encoding='utf-8')
        cache_timer.finish('completed')
        rows=modal['rows'];props=ops.modalProperties('-return')
        if float(modal['cumulative_U'+axis+'_percent'] or 0)<90:raise ValueError(axis+' modal mass is below 90 percent; increase modes.')
        if modal['modes_at_or_above_33_Hz']:raise ValueError('Returned modes at/above 33 Hz require a reviewed missing-mass correction, not implemented by this MRSM engine. No design result exported.')
        # Actual assembled supports, never the unfiltered exported 76-point
        # source map, determine MRSM reaction recorder node identities.
        # 32 real foundations remain primary; 76/97 are diagnostic only.
        ns=sorted(map(int,data['nodes']));elements=sorted(ops.getEleTags());support_tags=solver_reaction_support_tags(built,selected_support)
        display_nodes=dict(data['nodes'],**{str(g['master_tag']):g['master_xyz'] for g in groups});display_ns=sorted(map(int,display_nodes))
        for ecc_sign in ((0,1,-1) if config.get('accidental_torsion',True) else (0,)):
            case_axis=axis+('_Eplus' if ecc_sign==1 else '_Eminus' if ecc_sign==-1 else '_E0')
            modal_u=[];modal_f=[];modal_d=[];modal_edge=[];modal_shear=[];modal_V=[];modal_reactions=[];force_checks=[]
            print('[MRSM CASE START]',state,axis+'_'+('E0' if ecc_sign==0 else 'Eplus' if ecc_sign==1 else 'Eminus'),flush=True)
            for row in rows:
                T=row['period_s'];Sa=design_cd(T,config)*GRAVITY_M_S2
                gamma_x=float(props['partiFactorM'+axis][row['mode']-1])
                gm=sum(float(data['nodal_mass'].get(str(n),0.))*sum(float(ops.nodeEigenvector(n,row['mode'],j))**2 for j in (1,2,3)) for n in ns)
                torque_generalized=0.
                if ecc_sign:
                    for g in groups:
                        z=g['master_xyz'][2];lower=max([data['base_z_m']]+[q['master_xyz'][2] for q in groups if q['master_xyz'][2]<z-1e-7])
                        members=[n for n in ns if lower+1e-7<data['nodes'][str(n)][2]<=z+1e-7]
                        floor_nodes=[data['nodes'][str(n)] for n in g['slave_node_tags'] if str(n) in data['nodes']]
                        breadth=max(v[1 if axis=='X' else 0] for v in floor_nodes)-min(v[1 if axis=='X' else 0] for v in floor_nodes)
                        mass=sum(float(data['nodal_mass'].get(str(n),0.)) for n in members)
                        torque_generalized+=ecc_sign*.05*breadth*mass*ops.nodeEigenvector(g['master_tag'],row['mode'],6)
                desired_gamma=gamma_x+(torque_generalized/gm if gm else 0.)
                # Native RSA can generate the same eigenvector displacement using any nonzero participation factor.
                factors=[float(props.get(key,[0.]*len(rows))[row['mode']-1]) for key in ('partiFactorMX','partiFactorMY','partiFactorMZ','partiFactorRMX','partiFactorRMY','partiFactorRMZ')]
                excitation=max(range(6),key=lambda j:abs(factors[j]));input_sa=Sa*desired_gamma/factors[excitation] if abs(factors[excitation])>1e-20 else 0.
                # Exact ordinate at the mode period; the two equal values avoid interpolation error.
                ops.responseSpectrumAnalysis(excitation+1,'-Tn',0.,6.,'-Sa',0.,0.,'-mode',row['mode'])
                baseline=[np.asarray(ops.eleForce(e),float) for e in elements]
                ops.reactions();baseline_reactions=np.asarray([ops.nodeReaction(n) for n in support_tags])
                response_sign=1. if input_sa>=0 else -1.
                ops.responseSpectrumAnalysis(excitation+1,'-Tn',0.,6.,'-Sa',abs(input_sa),abs(input_sa),'-mode',row['mode'])
                ops.reactions();reactions=(np.asarray([ops.nodeReaction(n) for n in support_tags])-baseline_reactions)*response_sign;modal_reactions.append(reactions)
                u=np.asarray([ops.nodeDisp(n) for n in display_ns]);forces=[np.asarray(ops.eleForce(e),float)-b for e,b in zip(elements,baseline)]
                modal_u.append(u*response_sign);modal_f.append(np.concatenate(forces)*response_sign)
                floor=np.asarray([ops.nodeDisp(g['master_tag'],dof) for g in groups]);h=np.diff([0.]+[g['master_xyz'][2]-data['base_z_m'] for g in groups]);modal_d.append(np.diff(np.r_[0.,floor])/h*response_sign)
                edges=[]
                for index,g in enumerate(groups):
                    lower=groups[index-1] if index else None;h=g['master_xyz'][2]-(lower['master_xyz'][2] if lower else data['base_z_m'])
                    pts=[data['nodes'][str(n)] for n in g['slave_node_tags'] if str(n) in data['nodes']];perp=1 if axis=='X' else 0
                    for position in (min(p[perp] for p in pts),max(p[perp] for p in pts)):
                        sign=-1 if axis=='X' else 1
                        upper_u=ops.nodeDisp(g['master_tag'],dof)+sign*ops.nodeDisp(g['master_tag'],6)*(position-g['master_xyz'][perp])
                        lower_u=(ops.nodeDisp(lower['master_tag'],dof)+sign*ops.nodeDisp(lower['master_tag'],6)*(position-lower['master_xyz'][perp])) if lower else 0.
                        edges.append((upper_u-lower_u)/h*response_sign)
                modal_edge.append(edges)
                gamma=desired_gamma;force_by_level=[]
                for g in groups:
                    z=g['master_xyz'][2];lower=max([data['base_z_m']]+[q['master_xyz'][2] for q in groups if q['master_xyz'][2]<z-1e-7]);f=0.
                    for n in ns:
                        p=data['nodes'][str(n)];m=float(data['nodal_mass'].get(str(n),0.))
                        if lower+1e-7<p[2]<=z+1e-7:f+=m*ops.nodeEigenvector(n,row['mode'],dof)*gamma*Sa
                    force_by_level.append(f)
                modal_shear.append(np.cumsum(force_by_level[::-1])[::-1]);modal_V.append(gm*gamma_x*desired_gamma*Sa)
                reaction=float(reactions[:,dof-1].sum());expected=modal_V[-1]
                force_checks.append(dict(mode=row['mode'],modal_inertia_base_shear_kN=expected,modal_support_reaction_kN=reaction,error_kN=reaction+expected,error_percent=100*abs(reaction+expected)/max(1.,abs(expected))))
            rho=cqc_matrix([r['omega_rad_s'] for r in rows],float(config.get('damping',.05)))
            raw_V=float(combine(modal_V,rho));reference=calculate_esm(stories,period_s=float(config['T1_'+axis]),soil_type=config['soil'],zoning_factor_z=float(config['Z']),importance_factor_i=float(config['I']),limit_state=state,r_mu=float(config['rmu']),omega_u=float(config['omegau']),omega_s=float(config['omegas']),irregular=True,diagnostic_reference=True)
            from components.nbc105.clause_07_modal_response_spectrum import force_scale_factor
            scale=force_scale_factor(reference['base_shear_kN'],raw_V);u=combine(modal_u,rho);d=combine(modal_d,rho);shear=combine(modal_shear,rho)*scale;f=combine(modal_f,rho)*scale
            amp=float(config['rmu']) if state=='ULS' else 1.
            edge_d=combine(modal_edge,rho)*amp
            # NBC force scale is deliberately not applied to displacement/drift; ESM kd is not an MRSM factor.
            story_result=[dict(story_number=g['storey_number'],height_m=g['master_xyz'][2]-data['base_z_m'],elastic_displacement_m=float(u[display_ns.index(int(g['master_tag'])),dof-1]),design_displacement_m=float(u[display_ns.index(int(g['master_tag'])),dof-1]*amp),elastic_drift_ratio=float(d[i]),design_drift_ratio=float(max(edge_d[2*i:2*i+2])),master_design_drift_ratio=float(d[i]*amp),scaled_story_shear_kN=float(shear[i])) for i,g in enumerate(groups)]
            write_csv(out/(state+'_'+case_axis+'_Drift_V132.csv'),drift_check(story_result,state))
            write_csv(out/(state+'_'+case_axis+'_Modal_Force_Equilibrium_V132.csv'),force_checks)
            support_envelope=combine(modal_reactions,rho)*scale
            write_csv(out/(state+'_'+case_axis+'_Support_Reactions_V132.csv'),[dict(node_tag=n,**{('F'+str(j+1)+'_kN' if j<3 else 'M'+str(j-2)+'_kNm'):float(v) for j,v in enumerate(support_envelope[i])}) for i,n in enumerate(support_tags)])
            sizes=[len(v) for v in forces];offset=0;force_rows=[]
            for tag,size in zip(elements,sizes):
                for j,value in enumerate(f[offset:offset+size]):force_rows.append(dict(element_tag=tag,global_component_index=j+1,scaled_modal_force=float(value),unit='kN for translational components; kN m for rotational components',note='CQC seismic envelope only; combine gravity separately and preserve action correlations for member design.'))
                offset+=size
            write_csv(out/(state+'_'+case_axis+'_Element_Force_Envelopes_V132.csv'),force_rows)
            profile_path=out/(state+'_'+case_axis+'_CQC_Story_Response_Profile.csv')
            write_csv(profile_path,[
                dict(story_number=r["story_number"],height_m=r["height_m"],
                     elastic_displacement_m=r["elastic_displacement_m"],
                     design_displacement_m=r["design_displacement_m"],
                     elastic_drift_ratio=r["elastic_drift_ratio"],
                     design_drift_ratio=r["design_drift_ratio"],
                     scaled_story_shear_kN=r["scaled_story_shear_kN"])
                for r in story_result
            ])
            deformation=dict(nodes=display_nodes,limit_state=state,response_case=case_axis,dof_names=['Ux','Uy','Uz','Rx','Ry','Rz'],dof_availability=[True]*6,eccentricity_sign=ecc_sign,elements=[e['nodes'] for e in data['frames']+data['shells']],displacements={str(n):(u[j]*amp).tolist() for j,n in enumerate(display_ns)},note=state+' '+axis+' MRSM component-wise positive CQC envelope; not a simultaneous physical shape. Force base-shear scale is not applied.')
            (out/('Deformation_MRSM_'+state+'_'+case_axis+'_V132.json')).write_text(json.dumps(deformation),encoding='utf-8')
            result=dict(model_sha256=model_signature,implementation_sha256=source_signature,modal_numeric_sha256=numeric_signature, support_case=selected_support, seismic_mass_policy=selected_mass, support_case_evidence=support_evidence, gravity_profile=__import__('os').environ.get('OPENSEES_GRAVITY_PROFILE','AS_CONFIGURED'),limit_state=state,axis=axis,accidental_eccentricity_sign=ecc_sign,unscaled_modal_base_shear_kN=raw_V,reference_ESM_base_shear_kN=reference['base_shear_kN'],force_scale=scale,scaled_modal_base_shear_kN=raw_V*scale,displacement_scale_from_7_5=1.,drift_amplification=amp,combination='CQC, equal modal damping',mass_participation_percent=modal['cumulative_U'+axis+'_percent'],stories=story_result,modal_base_shears_kN=modal_V,modal_rows=rows,units='kN m s; dimensionless Cd converted to m/s2 using 9.81',scope='Elastic model with inherent torsion plus signed 5 percent per-floor eccentric inertia torque; lumped floor influence vector on unchanged eigenmodes. Orthogonal member design combinations require review; member design not performed.',status='ANALYSIS COMPLETE / DESIGN COMBINATIONS REQUIRE REVIEW')
            relevant=[r['error_percent'] for r in force_checks if abs(r['modal_inertia_base_shear_kN'])>max(1.,max(abs(v) for v in modal_V)*1e-4)]
            result['stiffness_review']='Gross in-plane elastic wall stiffness: review NBC Table 3-1; no compliance certification.'
            result['modal_force_equilibrium_max_relevant_percent']=max(relevant or [0.])
            result['modal_force_equilibrium_note']='Native elastic RSA force diagnostic about a gravity-preloaded geometric model; inspect residuals. 1 percent is an implementation review threshold, not an NBC-prescribed tolerance.'
            if max(relevant or [0.])>1.:result['status']='FORCE EQUILIBRIUM NEEDS REVIEW - do not use member force envelopes for design'
            from components.shared.response_recorders import write_recorder_index
            write_recorder_index(
                out, "modal_response_spectrum",
                [
                    (profile_path.name, [
                        "story displacement", "story drift", "scaled story shear"]),
                    (state+'_'+case_axis+'_Support_Reactions_V132.csv', [
                        "component-wise CQC support reaction envelope"]),
                    (state+'_'+case_axis+'_Element_Force_Envelopes_V132.csv', [
                        "component-wise CQC element force envelope"]),
                    ('Deformation_MRSM_'+state+'_'+case_axis+'_V132.json', [
                        "component-wise CQC nodal displacement envelope"]),
                    ('Modal_'+axis+'/Modal_Story_Mode_Shapes.csv', [
                        "raw and normalized diaphragm/perimeter mode shapes"]),
                ],
                notes=[
                    "CQC displacement, drift, support-reaction and force envelopes are independently combined components; they are not one simultaneous physical response state and must not be interpreted as a hysteresis path.",
                    "Gravity effects and correlated member design combinations require separate review.",
                ],
                filename="Response_Recorder_Index_"+state+"_"+case_axis+".json",
            )
            results[case_axis]=result;print('[MRSM COMPLETE]',state,case_axis,'| '+('centered e=0' if ecc_sign==0 else ('signed eccentricity +5% breadth' if ecc_sign==1 else 'signed eccentricity -5% breadth')),'| Vraw=',raw_V,'| force S=',scale,flush=True)
    (out/'MRSM_Results_V132.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(1,2,figsize=(11,6),layout='constrained')
    for axis,res in results.items():
        z=[r['height_m'] for r in res['stories']];ax[0].plot([r['scaled_story_shear_kN'] for r in res['stories']],z,label=axis);ax[1].plot([r['design_drift_ratio'] for r in res['stories']],z,label=axis)
    ax[0].set(xlabel='Force-scaled storey shear (kN)',ylabel='Height (m)');ax[1].set(xlabel='Unscaled design drift ratio');ax[1].axvline(.025 if state=='ULS' else .006,color='r',ls='--')
    for a in ax:a.grid(alpha=.2);a.legend()
    fig.savefig(out/'MRSM_Profiles_V132.png',dpi=160);plt.close(fig)
    from OpenSees_MRSM_Reports_V134 import export_reports
    export_reports(out)
    return results


def validate_mrsm_case_output(output, *, state, expected_model_sha256=None,
                              expected_support_case=None, expected_mass_policy=None):
    """[REF docs/source/components/response_spectrum/model_analysis.py.md]
    Verify exact, independently saved six-case MRSM output before solver-only
    completion status. This verifies *file completeness*, not physical validity.
    """
    root=Path(output)
    file=root/"MRSM_Results_V132.json"
    if not file.is_file():
        raise ValueError("MRSM solver returned without MRSM_Results_V132.json")
    import re
    data=json.loads(file.read_text(encoding="utf-8-sig"))
    if not isinstance(data,dict):
        raise ValueError("MRSM saved result must be a case-keyed JSON object")
    expected={axis+suffix for axis in ("X","Y")
              for suffix in ("_E0","_Eplus","_Eminus")}
    if set(data)!=expected:
        raise ValueError("Incomplete or unexpected MRSM cases: "
                         +repr(sorted(expected-set(data)))+" missing, "
                         +repr(sorted(set(data)-expected))+" unexpected")
    hashes=set()
    for key in sorted(expected):
        result=data[key]
        if not isinstance(result,dict):
            raise ValueError("MRSM case result is not a JSON object: "+key)
        if result.get("limit_state")!=state:
            raise ValueError("MRSM state mismatch: "+key)
        if result.get("axis")!=key[0]:
            raise ValueError("MRSM response direction mismatch: "+key)
        # A serialized model SHA does not encode the runtime-selected
        # foundation constraints or mass operator. Require those identities
        # whenever this is a saved current-run numerical-completeness gate.
        if expected_support_case is not None:
            if result.get("support_case")!=expected_support_case:
                raise ValueError("MRSM executed support profile mismatch: "+key)
            evidence=result.get("support_case_evidence")
            if (not isinstance(evidence,dict)
                    or evidence.get("selected_profile")!=expected_support_case):
                raise ValueError("MRSM runtime support evidence mismatch: "+key)
        if (expected_mass_policy is not None
                and result.get("seismic_mass_policy")!=expected_mass_policy):
            raise ValueError("MRSM executed seismic mass operator mismatch: "+key)
        if not isinstance(result.get("stories"),list) or not result["stories"]:
            raise ValueError("MRSM case has no storey results: "+key)
        # A six-case JSON with only drift values is not a complete response.
        # Verify the scalar force/mass outputs before treating saved files as
        # solver-only complete. This is still NOT an ETABS/NBC acceptance gate.
        numeric_scalars = (
            "unscaled_modal_base_shear_kN",
            "reference_ESM_base_shear_kN",
            "force_scale",
            "scaled_modal_base_shear_kN",
            "mass_participation_percent",
        )
        values = {}
        for field in numeric_scalars:
            try:
                raw = result[field]
                if isinstance(raw, bool):
                    raise TypeError("Boolean is not a numeric result")
                values[field] = float(raw)
            except (KeyError, TypeError, ValueError, OverflowError) as exc:
                raise ValueError(
                    f"MRSM {key} missing/invalid required numeric {field}"
                ) from exc
            if not math.isfinite(values[field]):
                raise ValueError(f"MRSM {key} nonfinite {field}")
        if any(values[field] <= 0 for field in (
            "unscaled_modal_base_shear_kN",
            "reference_ESM_base_shear_kN",
            "scaled_modal_base_shear_kN",
        )):
            raise ValueError(f"MRSM {key} base shear must be positive")
        if values["force_scale"] < 1.0:
            raise ValueError(f"MRSM {key} force scale cannot be below one")
        if not 90.0 <= values["mass_participation_percent"] <= 100.0 + 1e-6:
            raise ValueError(f"MRSM {key} insufficient/invalid modal mass")
        expected_scaled = (
            values["unscaled_modal_base_shear_kN"] * values["force_scale"]
        )
        if not math.isclose(
            expected_scaled, values["scaled_modal_base_shear_kN"],
            rel_tol=1e-6, abs_tol=1e-5,
        ):
            raise ValueError(f"MRSM {key} inconsistent force-scaled base shear")
        response_status = result.get("status")
        if not isinstance(response_status, str) or not response_status.strip():
            raise ValueError(f"MRSM {key} missing response-status review flag")

        for position,row in enumerate(result["stories"],start=1):
            if not isinstance(row,dict):
                raise ValueError(f"MRSM {key} story {position} is not a response object")
            for required in ("story_number", "scaled_story_shear_kN",
                             "design_displacement_m", "design_drift_ratio"):
                if required not in row:
                    raise ValueError(
                        f"MRSM {key} story {position} missing {required}"
                    )
            try:
                drift=float(row["design_drift_ratio"])
            except (ValueError,TypeError,OverflowError) as exc:
                raise ValueError(f"MRSM {key} story {position} has invalid drift") from exc
            if not math.isfinite(drift) or drift<0:
                raise ValueError(f"MRSM {key} story {position} has nonfinite/negative drift")
            for numeric_key in ("height_m","scaled_story_shear_kN",
                                "elastic_displacement_m","design_displacement_m",
                                "elastic_drift_ratio"):
                if numeric_key in row and row[numeric_key] is not None:
                    try:
                        number=float(row[numeric_key])
                    except (ValueError,TypeError,OverflowError) as exc:
                        raise ValueError(f"MRSM {key} story {position} invalid {numeric_key}") from exc
                    if not math.isfinite(number):
                        raise ValueError(f"MRSM {key} story {position} nonfinite {numeric_key}")
        digest=result.get("model_sha256")
        if not isinstance(digest,str) or re.fullmatch("[a-fA-F0-9]{64}",digest) is None:
            raise ValueError("MRSM model fingerprint missing/invalid: "+key)
        hashes.add(digest)
    if len(hashes)!=1:
        raise ValueError("MRSM response cases refer to different assembled models")
    if expected_model_sha256 is not None and next(iter(hashes))!=expected_model_sha256:
        raise ValueError("Saved MRSM response is not the requested model SHA")
    return {"status":"COMPLETE_SAVED_CASES_ONLY",
            "case_count":6,"limit_state":state,
            "model_sha256":next(iter(hashes)),
            "file":str(file)}



def mrsm_period_defaults(folder, values, state='ULS'):
    """Return NBC §5.1.3 adopted periods only with current-model Rayleigh+Aw.

    The legacy workbook C14/C15 references are NOT the sole proof of a
    calculated Rayleigh period or the adopted T=min(Tr,1.25*T_emp).
    This is for the thesis concrete shear-wall structural system. The
    associated source/period audit must still be independently reviewed.
    """
    from components.modal.analysis import nbc105_period_estimate
    folder=Path(folder)
    values=dict(values)
    aw_note=''
    if values.get("awx") in (None,"") or values.get("awy") in (None,""):
        # [REF NBC105-2025 §5.1.2; components/inputs/aw_sources.py] same-EDB
        # ETABS-linked Excel method first, then the OpenSees geometry
        # diagnostic; the label is shown with the adopted periods.
        try:
            from components.inputs.aw_sources import resolve_aw
            res=resolve_aw(folder,state)
            for axis in ("X","Y"):
                if values.get("aw"+axis.lower()) in (None,"") and res.get(axis) is not None:
                    values["aw"+axis.lower()]=res[axis]
            aw_note=" Aw source: "+"; ".join(f"{a}={res['labels'].get(a,'n/a')}" for a in ("X","Y"))+"."
        except Exception as exc:
            aw_note=" Aw source lookup failed: "+str(exc)+"."
    required=("awx","awy","rayleigh_tx","rayleigh_ty")
    missing=[key for key in required if values.get(key) in (None,"")]
    if missing:
        # The user's original ETABS-linked calculator already contains
        # attributed adopted design periods; never substitute them as modal
        # or Rayleigh results. Reuse only a source/state-matched audit.
        if (folder/'OpenSees_Complete_Model_Data_V118.json').is_file():
            from components.inputs.aw_sources import latest_linked_reference
            reference,_=latest_linked_reference(folder,state)
            if reference:
                adopted=reference['values']
                return {'T1_X':adopted['workbook_adopted_tx'],
                        'T1_Y':adopted['workbook_adopted_ty']}, (
                    'Original ETABS-linked workbook adopted design-period references; '
                    'fresh Rayleigh evidence unavailable. Research comparison only. '
                    'Source: '+reference['source_workbook'])
        return {"T1_X":"","T1_Y":""}, ("Validated period defaults unavailable; "
                "missing source-model fields: "+", ".join(missing)+
                ". Run the preliminary Rayleigh analysis (ESM window) for this state, "
                "or type reviewed T1_X / T1_Y."+aw_note)
    model=folder/"OpenSees_Complete_Model_Data_V118.json"
    if not model.is_file():
        return {"T1_X":"","T1_Y":""},"Missing assembled current-model geometry for H."
    data=json.loads(model.read_text(encoding="utf-8-sig"))
    groups=data.get("diaphragms",[])
    if not groups:
        return {"T1_X":"","T1_Y":""},"No mapped floor elevations for seismic height."
    height=max(float(g["master_xyz"][2]) for g in groups)-float(data["base_z_m"])
    periods=nbc105_period_estimate(
        height_m=height,system_type="concrete shear-wall building",
        wall_aw_x_m2=values["awx"],wall_aw_y_m2=values["awy"],
        rayleigh_x_s=values["rayleigh_tx"],rayleigh_y_s=values["rayleigh_ty"])
    return {"T1_X":periods["adopted_design_period_X_s"],
            "T1_Y":periods["adopted_design_period_Y_s"]}, (
            "NBC §5.1.3 adopted period=min(reviewed current-state Rayleigh, "
            "1.25×directional empirical wall period). Verify Aw and model hash."+aw_note)



_MRSM_INPUT_FIELDS = (
    "limit_state", "soil", "Z", "I", "rmu", "omegau", "omegas",
    "T1_X", "T1_Y", "nmodes", "damping", "support_case",
    "seismic_mass_policy", "gravity_profile",
)


def mrsm_input_signature(fields):
    """[REF docs/source/components/response_spectrum/model_analysis.py.md]
    Stable fingerprint of the selected MRSM GUI analysis inputs.

    Model JSON, EDB and source workbook keep separate source fingerprints.
    String-preserving comparison is intentionally conservative; changing
    an input's representation triggers a saved-case review, never silent reuse.
    """
    import hashlib
    if not isinstance(fields, dict):
        raise ValueError("MRSM selected inputs must be a mapping")
    values = {}
    for key in _MRSM_INPUT_FIELDS:
        item = fields.get(key)
        if item is None or isinstance(item, bool) or not str(item).strip():
            raise ValueError("Missing selected MRSM input: " + key)
        values[key] = str(item).strip()
    encoded = json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def review_saved_mrsm_batch(output_root, source_folder, selected_fields):
    """[REF docs/source/components/response_spectrum/model_analysis.py.md]
    Read-only saved MRSM GUI status, never a physics or NBC approval.

    A legacy/stale case-status ledger alone cannot prove that the current
    source model, selected ULS/SLS inputs and six numeric results agree.
    Re-open only the exact recorded canonical run; never discover a nearby
    result through a latest-file scan or historic snapshot.
    """
    import hashlib
    from components.inputs.output_contract import inspect_case_manifest
    stage = Path(output_root).expanduser()
    ledger_file = stage / "MRSM_Batch_Status_V151.json"
    base = {"reported_completed": 0, "numerical_cases_verified": 0,
            "engineering_acceptance": "NOT_VERIFIED"}
    def reviewed(status, reason, **values):
        return dict(base, status=status, reason=reason, **values)

    if ledger_file.is_symlink():
        return reviewed("NUMERIC_EVIDENCE_INCOMPLETE", "Linked batch ledger is not trusted")
    if not ledger_file.is_file():
        return reviewed("NOT_RUN", "No MRSM batch ledger recorded")
    try:
        payload = json.loads(ledger_file.read_text(encoding="utf-8-sig"))
        rows = payload.get("cases") if isinstance(payload, dict) else None
        if not isinstance(rows, list) or any(
                not isinstance(row, dict) for row in rows):
            raise ValueError("Invalid MRSM case rows")
        completed = sum(row.get("status") == "COMPLETED" for row in rows)
    except (OSError, ValueError, TypeError) as exc:
        return reviewed("INVALID_LEDGER", str(exc))
    base["reported_completed"] = completed
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict) or not provenance:
        return reviewed("LEGACY_UNVERIFIED",
                        "Saved process rows lack a model and input fingerprint")
    try:
        state = str(selected_fields["limit_state"]).strip().upper()
        # Source-state/config mismatches take precedence over a case-name
        # count: a saved ULS row viewed in SLS is stale, not an incomplete
        # current-state batch.
        if (provenance.get("state") != state
                or provenance.get("input_sha256") !=
                    mrsm_input_signature(selected_fields)):
            return reviewed("SOURCE_OR_INPUT_MISMATCH",
                            "Saved MRSM ledger belongs to another selected state or input configuration")
        required = {state + " " + axis + "_" + ecc
                    for axis in ("X", "Y")
                    for ecc in ("E0", "Eplus", "Eminus")}
        actual = [row.get("case") for row in rows]
        if (len(actual) != len(required) or len(set(actual)) != len(actual)
                or set(actual) != required or completed != len(required)):
            return reviewed("SAVED_PROCESS_INCOMPLETE",
                            "Six distinct X/Y eccentricity process completions required")
        source = Path(source_folder).expanduser()
        model_file = source / "OpenSees_Complete_Model_Data_V118.json"
        if model_file.is_symlink() or not model_file.is_file():
            return reviewed("SOURCE_UNAVAILABLE",
                            "Current serialized model JSON is missing or linked")
        with model_file.open("rb") as stream:
            model_sha = hashlib.file_digest(stream, "sha256").hexdigest()
        selected_input_sha = mrsm_input_signature(selected_fields)
        if (provenance.get("model_sha256") != model_sha
                or provenance.get("state") != state
                or provenance.get("input_sha256") != selected_input_sha):
            return reviewed("SOURCE_OR_INPUT_MISMATCH",
                            "Saved MRSM ledger belongs to another source, state or input selection")
        location = provenance.get("run_dir")
        if not isinstance(location, str) or not location.strip():
            return reviewed("NUMERIC_EVIDENCE_INCOMPLETE",
                            "Saved ledger has no exact created MRSM run directory")
        run_raw = Path(location).expanduser()
        if any(piece.is_symlink() for piece in (run_raw, *run_raw.parents)):
            return reviewed("NUMERIC_EVIDENCE_INCOMPLETE",
                            "Linked MRSM saved run is not accepted")
        run = run_raw.resolve()
        exact_stage = stage.resolve()
        if (len(run.parents) < 4 or run.parents[3] != exact_stage
                or run.parents[2].name != "RUNS"
                or run.parents[1].name != state):
            return reviewed("NUMERIC_EVIDENCE_INCOMPLETE",
                            "Saved MRSM run is outside the selected stage/state")
        checked = inspect_case_manifest(run, expected_stage="MRSM")
        if (not checked["valid"]
                or checked["solver_status"] != "COMPLETED_SOLVER_ONLY"):
            return reviewed("NUMERIC_EVIDENCE_INCOMPLETE",
                            "Canonical saved MRSM case manifest is missing, incomplete or inconsistent")
        case_manifest = json.loads(
            (run / "00_INPUT_SOURCE" / "CASE_MANIFEST.json").read_text(encoding="utf-8-sig"))
        if case_manifest.get("model_sha256") != model_sha:
            return reviewed("SOURCE_OR_INPUT_MISMATCH",
                            "Saved numerical run model SHA differs from selected model")
        gate_file = run / "06_REVIEW" / "SAVED_CASE_COMPLETENESS.json"
        if not gate_file.is_file() or gate_file.is_symlink():
            return reviewed("NUMERIC_EVIDENCE_INCOMPLETE",
                            "Saved-case numeric completeness checkpoint missing")
        gate = json.loads(gate_file.read_text(encoding="utf-8-sig"))
        if (not isinstance(gate, dict)
                or gate.get("status") != "COMPLETE_SAVED_CASES_ONLY"
                or gate.get("model_sha256") != model_sha
                or gate.get("case_count") != len(required)):
            return reviewed("NUMERIC_EVIDENCE_INCOMPLETE",
                            "Saved-case completeness checkpoint inconsistent")
        # Revalidate the six actual numeric responses, not only their log
        # statuses or a copied review ZIP.
        inspected = validate_mrsm_case_output(
            run / "02_RESULTS", state=state,
            expected_model_sha256=model_sha,
            expected_support_case=selected_fields["support_case"],
            expected_mass_policy=selected_fields["seismic_mass_policy"])
        if inspected.get("case_count") != len(required):
            return reviewed("NUMERIC_EVIDENCE_INCOMPLETE",
                            "Saved numeric case count differs from configured six cases")
        return reviewed("SAVED_NUMERICALLY_COMPLETE_SOURCE_MATCHED",
                        "Six exact-source saved cases passed numeric completeness screening; ETABS parity/code approval unverified",
                        numerical_cases_verified=len(required), run_dir=str(run))
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        return reviewed("NUMERIC_EVIDENCE_INCOMPLETE",
                        "Saved MRSM evidence could not be revalidated: " + str(exc))


def launch(parent,folder):
    import tkinter as tk
    from tkinter import ttk,messagebox
    import threading,subprocess,sys
    from OpenSees_Project_Inputs_V123 import import_project_inputs
    from OpenSees_Research_UI_V123 import scrollable_form
    win=tk.Toplevel(parent);win.title('Model MRSM — SLS / ULS, reports and deformation');win.geometry('1100x820');form=scrollable_form(win)
    from components.inputs.project_workbooks import source_limit_state,require_source_state,analysis_output_folder
    model_state,model_state_evidence=source_limit_state(folder)
    initial_state=model_state or 'ULS'
    root=_runtime_repo_root()
    values=import_project_inputs(root,folder,initial_state)['values'];fields={}
    period_defaults,period_note=mrsm_period_defaults(folder,values,initial_state)
    defaults=dict(limit_state=initial_state,soil=values.get('soil',''),Z=values.get('Z',''),I=values.get('I',''),rmu=values.get('rmu',''),omegau=values.get('omegau',''),omegas=values.get('omegas',''),T1_X=period_defaults['T1_X'],T1_Y=period_defaults['T1_Y'],nmodes=40,damping=.05,support_case='PHYSICAL_32',seismic_mass_policy='SOURCE_DISTRIBUTED')
    ttk.Label(form,text='Model response spectrum: mode shapes + site spectrum → CQC actions, force scaling, drift and nodal envelopes',wraplength=1000,font=('Segoe UI',12,'bold')).pack(anchor='w')
    grid=ttk.Frame(form);grid.pack(fill='x')
    for i,(name,value) in enumerate(defaults.items()):
        fields[name]=tk.StringVar(value=str(value));r=i//2;c=(i%2)*2;ttk.Label(grid,text=name,width=20).grid(row=r,column=c,sticky='w',pady=4)
        options=['ULS','SLS'] if name=='limit_state' else ['A','B','C','D'] if name=='soil' else ['PHYSICAL_32','SOURCE_76','WALL_BASE_97'] if name=='support_case' else ['SOURCE_DISTRIBUTED','STORY_LUMPED_NBC'] if name=='seismic_mass_policy' else None
        widget=ttk.Combobox(grid,textvariable=fields[name],values=options,state='readonly',width=25) if options else ttk.Entry(grid,textvariable=fields[name],width=25);widget.grid(row=r,column=c+1,sticky='ew',padx=6)
    grid.columnconfigure(1,weight=1);grid.columnconfigure(3,weight=1)
    def refresh(*unused):
        state=fields['limit_state'].get()
        try:
            require_source_state(folder,state)
        except ValueError as exc:
            fields['limit_state'].set(initial_state)
            messagebox.showwarning('Source state mismatch',str(exc),parent=win)
            return
        v=import_project_inputs(root,folder,state)['values']
        period_values,_=mrsm_period_defaults(folder,v,state)
        for name,key in [('soil','soil'),('Z','Z'),('I','I'),('rmu','rmu'),('omegau','omegau'),('omegas','omegas')]:
            if key in v:fields[name].set(str(v[key]))
        for axis in ('X','Y'):
            fields['T1_'+axis].set(str(period_values['T1_'+axis]) if period_values['T1_'+axis] else '')
    fields['limit_state'].trace_add('write',refresh)
    ttk.Label(form,text=period_note,wraplength=1000).pack(anchor='w',pady=3)
    ttk.Label(form,text='32 physical foundations primary; 76/97 diagnostic restraints only. Optional floor-master mass changes eigenmodes and needs native ETABS verification.',wraplength=1000).pack(anchor='w',pady=3)
    ttk.Label(form,text='Each state runs X and Y, with E0 / Eplus / Eminus cases (6 cases/state). E0 is centered; Eplus/Eminus are signed 5% perpendicular-breadth eccentric inertia cases. Soil selection requires site evidence. Acceleration conversion is internal for the kN-m-s model. Workbook / PNG / PDF are exported automatically.',wraplength=1000).pack(anchor='w',pady=6)
    from components.inputs.output_layout import export_root_for
    from components.inputs.output_contract import create_case_run,record_case_status,atomic_json
    import hashlib
    actions=ttk.Frame(form);actions.pack(fill='x')
    output=export_root_for(folder)/"05_MRSM"
    output.mkdir(parents=True,exist_ok=True)
    latest_result={"folder":None,"run":None}
    operation_status=tk.StringVar(value="READY | No MRSM batch running")
    operation_label=ttk.Label(form,textvariable=operation_status,wraplength=1030,
                              foreground='#165879')
    operation_label.pack(fill='x',pady=3)
    operation_bar=ttk.Progressbar(form,mode='indeterminate')
    operation_bar.pack(fill='x',pady=2)
    def operation(stage,detail):
        # All state and widget updates are applied on Tk's UI thread.
        def render():
            operation_status.set(stage+' | '+detail)
            if stage in ('RUNNING','EXPORTING'):
                operation_bar.start(12)
            else:operation_bar.stop()
        win.after(0,render)
    # Reading a large saved MRSM result must not block Tk startup.
    # Only a same-source, same-state, same-input current numeric run may
    # display as verified; fields changed while checking invalidate it.
    import os
    def current_inputs():
        return dict({key:value.get() for key,value in fields.items()},
                    gravity_profile=os.environ.get('OPENSEES_GRAVITY_PROFILE','AS_CONFIGURED'))

    selected_gui_fields=current_inputs()
    previous_status=output/'MRSM_Batch_Status_V151.json'
    check_label='CHECKING SAVED RUN | validating selected source and six numeric cases'
    def invalidate_saved_review(*unused):
        text=operation_status.get()
        if text.startswith(('CHECKING SAVED RUN','SAVED NUMERIC REVIEW')):
            latest_result.update(folder=None,run=None)
            operation_status.set(
                'REVIEW | MRSM inputs changed; reopen or rerun for current selection')
    for selected in fields.values():
        selected.trace_add('write',invalidate_saved_review)
    if previous_status.is_file() or previous_status.is_symlink():
        operation_status.set(check_label)
        def inspect_previous_saved():
            prior=review_saved_mrsm_batch(output,folder,selected_gui_fields)
            def render_prior():
                if operation_status.get()!=check_label:
                    # The user may have edited inputs or started a new run.
                    return
                current=current_inputs()
                if current!=selected_gui_fields:
                    operation_status.set(
                        'REVIEW | MRSM source inputs changed during saved check')
                elif prior['status']=='SAVED_NUMERICALLY_COMPLETE_SOURCE_MATCHED':
                    latest_result['run']=Path(prior['run_dir'])
                    latest_result['folder']=latest_result['run']/'02_RESULTS'
                    latest_result['input_sha256']=mrsm_input_signature(current)
                    operation_status.set(
                        'SAVED NUMERIC REVIEW | '+
                        str(prior['numerical_cases_verified'])+
                        '/6 cases source-rechecked; ETABS parity still open')
                else:
                    operation_status.set(
                        'REVIEW | '+prior['status']+
                        ' | previously reported '+str(prior['reported_completed'])+
                        ' process completions; current numeric acceptance pending')
            try:
                win.after(0,render_prior)
            except (tk.TclError,RuntimeError):
                pass
        threading.Thread(target=inspect_previous_saved,daemon=True).start()
    log_value=tk.StringVar()
    from OpenSees_Research_UI_V123 import copyable_log
    from components.shared.case_status import panel,CaseLedger
    board=panel(form)
    log=copyable_log(form,log_value,height=12)
    def append(line):
        try:win.after(0,lambda:(log.insert('end',line),log.see('end')))
        except (tk.TclError,RuntimeError):pass
    def run():
        try:
            cfg=current_inputs()
            selected_gui_fields=dict(cfg)
            selected_input_sha=mrsm_input_signature(selected_gui_fields)
            data_file=Path(folder)/'OpenSees_Complete_Model_Data_V118.json'
            if data_file.is_symlink() or not data_file.is_file():
                raise FileNotFoundError('MRSM selected source model JSON missing or linked')
            with data_file.open('rb') as source_stream:
                selected_model_sha=hashlib.file_digest(source_stream,'sha256').hexdigest()
            require_source_state(folder,cfg['limit_state'])
            # [REF NBC105-2025 §5.1.3, §7.5] name blank inputs instead of
            # failing with "could not convert string to float: ''".
            blank=[k for k in ('Z','I','rmu','omegau','omegas','T1_X','T1_Y','damping','nmodes')
                   if not str(cfg.get(k,'')).strip()]
            if blank:
                raise ValueError('Fill these inputs first: '+', '.join(blank)+
                    '. T1_X/T1_Y are the NBC §5.1.3 adopted periods = min(Rayleigh, 1.25×empirical); '
                    'run the preliminary Rayleigh analysis in the ESM window or enter reviewed values.')
            cfg['nmodes']=int(cfg['nmodes'])
            for k in ['Z','I','rmu','omegau','omegas','T1_X','T1_Y','damping']:cfg[k]=float(cfg[k])
            states=[cfg['limit_state']];button.configure(state='disabled')
            operation('RUNNING','Gravity → eigenmodes → CQC responses for '+', '.join(states))
            ledger=CaseLedger(
                output/"MRSM_Batch_Status_V151.json",
                [state+" "+axis+"_"+ecc for state in states for axis in ("X","Y")
                 for ecc in ("E0","Eplus","Eminus")],
                provenance=dict(model_sha256=selected_model_sha,
                                state=cfg['limit_state'],
                                input_sha256=selected_input_sha))
            board["ledger"]=ledger;board["cancelled"]=False
            def worker():
                current_run=None
                try:
                    append('[BATCH PLAN] '+', '.join(states)+'; each state runs X and Y, centered and +/-5% eccentricity.\n')
                    from components.inputs.project_workbooks import analysis_output_folder
                    for state in states:
                        if board.get("cancelled"):break
                        append('[STATE START] '+state+' | gravity/preload, eigenanalysis, modal RSA, CQC, force scaling, drift and export.\n')
                        operation('RUNNING',state+' | gravity and modal CQC stages underway')
                        current=dict(cfg,limit_state=state,
                                     gravity_profile=cfg['gravity_profile'])
                        data_file=Path(folder)/'OpenSees_Complete_Model_Data_V118.json'
                        if not data_file.is_file() or data_file.is_symlink():
                            raise FileNotFoundError('MRSM source model data missing or linked: '+str(data_file))
                        model_hash=hashlib.sha256(data_file.read_bytes()).hexdigest()
                        if model_hash!=selected_model_sha:
                            raise ValueError('MRSM source model changed after batch selection; select current source again')
                        run_root=create_case_run(folder,'MRSM','MRSM_'+current['gravity_profile'],
                                                 state=state,model_sha256=model_hash)
                        current_run=run_root
                        ledger.set_provenance(run_dir=str(run_root))
                        latest_result['run']=run_root
                        out=run_root/'02_RESULTS'
                        latest_result['folder']=out
                        latest_result['input_sha256']=selected_input_sha
                        record_case_status(run_root,'RUNNING')
                        path=run_root/'00_INPUT_SOURCE'/'MRSM_Config_V132.json'
                        atomic_json(path,current)
                        script="import sys,json;sys.path.insert(0,"+repr(str(root))+");from OpenSees_Model_Response_Spectrum_V132 import run_model_spectrum;run_model_spectrum("+repr(str(Path(folder).resolve()))+",json.load(open("+repr(str(path.resolve()))+",encoding='utf-8')),"+repr(str(out.resolve()))+")"
                        log_path=run_root/'01_LOGS'/'MRSM_Run_V132.log'
                        with log_path.open('w',encoding='utf-8') as stream:
                            proc=subprocess.Popen([sys.executable,'-u','-c',script],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',env={**dict(__import__('os').environ),'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'})
                            board["process"]=proc
                            for line in proc.stdout:
                                stream.write(line);stream.flush();append(line)
                                if '[MRSM START]' in line:
                                    axis=line.split('[MRSM START]',1)[1].split()[1]
                                    for ecc in ('E0','Eplus','Eminus'):ledger.set(state+' '+axis+'_'+ecc,'PREPARING','Shared model/gravity/eigenanalysis; case RSA queued')
                                if '[MRSM STAGE]' in line:
                                    axis=line.split('[MRSM STAGE]',1)[1].split()[1]
                                    for ecc in ('E0','Eplus','Eminus'):ledger.set(state+' '+axis+'_'+ecc,'PREPARING','Shared sparse eigenanalysis; individual RSA queued')
                                if '[MRSM CASE START]' in line:
                                    parts=line.split('[MRSM CASE START]',1)[1].split();ledger.set(parts[0]+' '+parts[1],'RUNNING','Modal RSA / CQC and response export')
                                if '[MRSM COMPLETE]' in line:
                                    parts=line.split('[MRSM COMPLETE]',1)[1].split();key=parts[0]+' '+parts[1]
                                    if key in ledger.rows:ledger.set(key,'COMPLETED',line.strip())
                            rc=proc.wait();append(state+' EXIT '+str(rc)+'\n')
                            if rc:
                                record_case_status(run_root,'FAILED',
                                    message='MRSM child process exit '+str(rc)+'; inspect '+str(log_path))
                                for key,row in ledger.rows.items():
                                    if key.startswith(state+' ') and row['status']!='COMPLETED':ledger.set(key,'FAILED','State child exit '+str(rc)+'; inspect log. Next state will run independently.')
                            else:
                                try:
                                    if hashlib.sha256(data_file.read_bytes()).hexdigest()!=model_hash:
                                        raise ValueError('MRSM source model changed during solver execution; native output source invalid')
                                    gate=validate_mrsm_case_output(
                                        out,state=state,
                                        expected_model_sha256=model_hash,
                                        expected_support_case=current["support_case"],
                                        expected_mass_policy=current["seismic_mass_policy"])
                                    atomic_json(run_root/'06_REVIEW'/'SAVED_CASE_COMPLETENESS.json',gate)
                                    record_case_status(run_root,'COMPLETED_SOLVER_ONLY',
                                        message='Six saved MRSM cases found; physical equivalence unverified')
                                    # Only copy small derived display exports; numerical
                                    # native solver files stay exactly where they were written.
                                    import shutil
                                    for suffix,section in (('.xlsx','03_EXCEL'),('.png','04_FIGURES'),
                                                           ('.pdf','04_FIGURES')):
                                        for artifact in out.glob('*'+suffix):
                                            if artifact.stat().st_size<=25*1024*1024:
                                                shutil.copy2(artifact,run_root/section/artifact.name)
                                except (OSError,ValueError,KeyError) as exc:
                                    record_case_status(run_root,'INCOMPLETE',message=str(exc))
                                    append('[MRSM_SAVED_CASE_GATE_FAILED] '+str(exc)+'\n')
                                    for key,row in ledger.rows.items():
                                        if key.startswith(state+' '):
                                            ledger.set(key,'FAILED',
                                                'Saved case validation failed after child exit: '+str(exc))
                except Exception as e:
                    if current_run is not None:
                        try:record_case_status(current_run,'FAILED',message=str(e))
                        except (OSError,ValueError):pass
                    append('[FAILED] '+str(e)+'\n')
                finally:
                    ledger.finish_pending("Batch interrupted or case completion was not reported; inspect state log")
                    # Keep the exact process ledger with its immutable run
                    # alongside the stage-level latest-run pointer.
                    if current_run is not None:
                        try:
                            import shutil
                            shutil.copy2(ledger.path,
                                current_run/'06_REVIEW'/'MRSM_Batch_Status_V151.json')
                        except (OSError,ValueError) as snapshot_error:
                            append('[MRSM_LEDGER_SNAPSHOT_FAILED] '+str(snapshot_error)+'\n')
                    # Automatically consolidate real MRSM output in a single
                    # upload folder/ZIP, clearly separated from ETABS native
                    # responses. No missing native case is inferred.
                    operation('EXPORTING','Case execution ended; collecting auditable MRSM evidence ZIP')
                    try:
                        from components.validation.seismic_review_bundle import bundle_seismic_review
                        if current_run is None:
                            raise ValueError('No MRSM output created')
                        package=bundle_seismic_review(folder,current_run/'02_RESULTS',method="MRSM")
                        append("[MRSM_AUTO_REVIEW_ZIP] "+package["zip"]+"\n")
                    except Exception as pack_exc:
                        append("[MRSM_REVIEW_PACKAGING_FAILED] "+str(pack_exc)+"\\n")
                    reopened=review_saved_mrsm_batch(
                        output,folder,selected_gui_fields)
                    stage=('COMPLETED' if
                        reopened['status']=='SAVED_NUMERICALLY_COMPLETE_SOURCE_MATCHED'
                        else 'REVIEW REQUIRED')
                    operation(stage,str(reopened['numerical_cases_verified'])+
                        '/6 saved numeric cases source-rechecked; '+
                        reopened['status']+'; ETABS equivalence unverified')
                    try:win.after(0,lambda:button.configure(state='normal'))
                    except (tk.TclError,RuntimeError):pass
            threading.Thread(target=worker,daemon=True).start()
        except Exception as e:messagebox.showerror('MRSM inputs',str(e),parent=win)
    button=ttk.Button(actions,text='Run selected state(s)',command=run);button.pack(side='left')
    def selected_evidence_folder():
        selected=latest_result.get('folder')
        from components.inputs.output_contract import inspect_case_manifest
        if (selected is None or latest_result.get('input_sha256')!=mrsm_input_signature(current_inputs())
                or not (selected/'MRSM_Results_V132.json').is_file()):
            raise ValueError('Open a saved MRSM case matching the current inputs, or run the selected state first.')
        case=inspect_case_manifest(selected.parent,expected_stage='MRSM')
        if not case['valid'] or case['solver_status']!='COMPLETED_SOLVER_ONLY':
            raise ValueError('The selected MRSM case has no valid completion manifest.')
        manifest=json.loads((selected.parent/'00_INPUT_SOURCE'/'CASE_MANIFEST.json')
                            .read_text(encoding='utf-8-sig'))
        model=Path(folder)/'OpenSees_Complete_Model_Data_V118.json'
        if (model.is_symlink() or not model.is_file()
                or hashlib.sha256(model.read_bytes()).hexdigest()!=manifest.get('model_sha256')):
            raise ValueError('The current model export differs from the saved MRSM case.')
        return selected

    def export_zip():
        try:
            selected=selected_evidence_folder()
        except (OSError,ValueError) as exc:
            messagebox.showerror('MRSM review ZIP',str(exc),parent=win)
            return
        operation('EXPORTING','Creating MRSM review ZIP from existing saved results')
        def worker():
            try:
                from components.validation.seismic_review_bundle import bundle_seismic_review
                package=bundle_seismic_review(folder,selected,method='MRSM')
                append('[MRSM_REVIEW_ZIP] '+package['zip']+'\n')
                operation('EXPORTED','MRSM review ZIP: '+package['zip'])
            except Exception as exc:
                append('[MRSM_REVIEW_PACKAGING_FAILED] '+str(exc)+'\n')
                operation('FAILED','MRSM review ZIP creation: '+str(exc))
        threading.Thread(target=worker,daemon=True).start()
    ttk.Button(actions,text='Export full evidence ZIP',command=export_zip).pack(side='left')
    def export_organized_zip():
        """[REF docs/source/components/ui/organized_results.py.md] Keep legacy MRSM paths."""
        try:
            selected=selected_evidence_folder()
        except (OSError,ValueError) as exc:
            messagebox.showerror('Organized MRSM review ZIP',str(exc),parent=win)
            return
        def worker():
            try:
                from components.ui.organized_results import publish_mrsm_review
                result=publish_mrsm_review(selected)
                append('[ORGANIZED_MRSM_RUN_ZIP] '+
                       result['zip_files']['MRSM_RUN']+'\n')
                append('[ORGANIZED_MANIFEST] '+result['manifest']+'\n')
            except Exception as exc:
                append('[ORGANIZED_EXPORT_FAILED] '+str(exc)+'\n')
        threading.Thread(target=worker,daemon=True).start()
    ttk.Button(actions,text='Export organized run ZIP',
               command=export_organized_zip).pack(side='left',padx=4)

    # [REF components/ui/output_folder.py] shared output-folder action.
    from components.ui.output_folder import add_open_output_button
    add_open_output_button(actions,lambda:str(latest_result.get('run') or output),window=win)
    ttk.Button(actions,text='Saved SLS / ULS charts + Excel',command=lambda:__import__('OpenSees_MRSM_Reports_V134').launch(win,latest_result.get('folder') or output)).pack(side='left',padx=4)
    ttk.Button(actions,text='Deformation / node DOFs',command=lambda:__import__('OpenSees_Response_Checks_V132').launch_response_viewer(win,latest_result.get('folder') or output)).pack(side='left')
    ttk.Button(actions,text='Compare true ETABS modal/MRSM results',
        command=lambda:__import__('components.validation.etabs_comparison',
            fromlist=['launch']).launch(
            win,folder,results_root=latest_result.get('folder') or output)).pack(side='left',padx=4)
    win._mrsm_fields=fields;win._mrsm_log=log;return win
