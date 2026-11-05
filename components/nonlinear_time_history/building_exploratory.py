# THESIS NLTHA NOTE: This runner is EXPLORATORY until independently verified.
# 0.005-s diagnostic success is not completion of a paired full earthquake history.
# Ensure separate fresh runs, input hash, accepted-step log, XY/YX and dt refinement.
# Model-physics benchmark: PEER 2015/12; E-SFI formulation DOI:10.1016/j.engstruct.2023.116700.
# Never infer initiation of failure solely from post-failure nonfinite element forces.
"""Own building geometry with explicitly assumed research constitutive models.
This does not approve or modify the calibrated production-model workflow.
"""
from pathlib import Path
import json,math,time,csv,shutil,hashlib,datetime
import traceback
import numpy as np
PROFILE='LITERATURE_FRAME_NL_ELASTIC_WALL_V138'
TRANSIENT_SYSTEMS=('UmfPack','SparseGeneral')
_RUN_CONTEXT={}

def configure_transient_system(ops,system):
    """Select a supported transient matrix solver without silent fallbacks."""
    if system not in TRANSIENT_SYSTEMS:
        raise ValueError('transient_system must be one of: '+', '.join(TRANSIENT_SYSTEMS))
    if system=='SparseGeneral':ops.system('SparseGeneral','-piv')
    else:ops.system('UmfPack')

def profile_for_config(config):
    """Return the research profile selected by the exploratory configuration."""
    return 'LITERATURE_BUILDING_NL_V161' if bool(config.get('nonlinear_walls',False)) else PROFILE


def validate_output_separation(source, output):
    source_path=Path(source).resolve()
    output_path=Path(output).resolve()
    if output_path==source_path:
        raise ValueError('Choose a separate output folder; it may be a subfolder of the model export folder.')
    return source_path,output_path


def diagnostic_record_inputs(records,orientation,excitation):
    """Return records assigned to global X/Y, zeroing only inactive probe axes."""
    if orientation not in ('XY','YX'):
        raise ValueError('orientation must be XY or YX')
    excitation=str(excitation).upper()
    if excitation not in ('XY','X','Y','ZERO'):
        raise ValueError('diagnostic_excitation must be XY, X, Y or ZERO')
    ordered=records if orientation=='XY' else records[::-1]
    result=[]
    for direction,(values,step,units) in enumerate(ordered,1):
        active=excitation=='XY' or excitation=='X' and direction==1 or excitation=='Y' and direction==2
        result.append((values if active else np.zeros_like(values),step,units))
    return result

def _set_run_stage(stage,**details):
    _RUN_CONTEXT['stage']=stage
    _RUN_CONTEXT.update(details)

def _write_failure_report(folder,config,exc,*,filename='INCOMPLETE.json',details=None):
    source=config.get('model_folder')
    output=config.get('output_dir')
    if source and output:
        try:
            validate_output_separation(source,output)
        except ValueError:
            print('[FAILURE REPORT NOT WRITTEN] Output directory must be separate from the source model folder.',flush=True)
            return None
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    report=dict(
        status='INCOMPLETE',
        failed_at=datetime.datetime.now().astimezone().isoformat(),
        profile=profile_for_config(config),
        stage=_RUN_CONTEXT.get('stage','unknown'),
        error_type=type(exc).__name__,
        error=str(exc),
        traceback=traceback.format_exc(),
        config=config,
        context=dict(_RUN_CONTEXT),
    )
    if details:
        report.update(details)
    target=folder/filename
    target.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print('[FAILURE REPORT]',str(target),flush=True)
    return target

def run(config):
    _RUN_CONTEXT.clear()
    _RUN_CONTEXT.update(stage='configuration_validation',output_dir=str(config.get('output_dir','')))
    try:
        if config.get('sensitivity_parameter'):
            return _run_material_sensitivity(config)
        return _run(config)
    except Exception as exc:
        try:
            _write_failure_report(config.get('output_dir') or '.',config,exc)
        except OSError as report_error:
            print('[FAILURE REPORT ERROR]',repr(report_error),flush=True)
        raise


def _run_material_sensitivity(config):
    """Run a serial one-factor sweep, preserving a comparison row per completed case."""
    from components.nonlinear_time_history.research_building_materials import (
        validate_material_overrides,
    )
    from components.shared.response_recorders import write_rows

    parameter = str(config['sensitivity_parameter'])
    base_overrides = validate_material_overrides(config.get('material_overrides', {}))
    values = config.get('sensitivity_values')
    if not isinstance(values, list) or not 2 <= len(values) <= 12:
        raise ValueError('sensitivity_values must contain 2 through 12 numeric candidate values')
    candidates = []
    for raw in values:
        candidate = validate_material_overrides({parameter: raw})[parameter]
        if candidate in candidates:
            raise ValueError('sensitivity_values must not contain duplicates')
        candidates.append(candidate)

    source, output = validate_output_separation(
        config['model_folder'], config['output_dir'])
    output.mkdir(parents=True, exist_ok=True)
    if parameter.startswith(('frame.', 'wall.')) and not config.get('nonlinear_walls'):
        raise ValueError('Frame and wall sensitivity requires the nonlinear E-SFI-MVLEM-3D material profile.')

    rows = []
    completed = []
    for index, value in enumerate(candidates, 1):
        case_name = f"Case_{index:02d}_{parameter.replace('.', '_')}_{value:g}"
        case_config = dict(config)
        case_config.pop('sensitivity_parameter', None)
        case_config.pop('sensitivity_values', None)
        case_config['material_overrides'] = {**base_overrides, parameter: value}
        case_config['output_dir'] = str(output / case_name)
        print(f'[MATERIAL SENSITIVITY] {index}/{len(candidates)} {parameter}={value:g}', flush=True)
        try:
            result = run(case_config)
        except Exception as exc:
            report = dict(
                status='INCOMPLETE',
                parameter=parameter,
                candidate_value=value,
                completed_cases=completed,
                failed_case=case_name,
                error_type=type(exc).__name__,
                error=str(exc),
                output_dir=str(output),
            )
            (output / 'Material_Sensitivity_Summary.json').write_text(
                json.dumps(report, indent=2), encoding='utf-8')
            raise

        states = result.items() if config.get('limit_state') == 'Both' else [
            (config.get('limit_state', 'ULS'), result)
        ]
        for state, state_result in states:
            for case in state_result.get('cases', []):
                row = {
                    'parameter': parameter,
                    'candidate_value': value,
                    'limit_state': state,
                    'orientation': case['orientation'],
                    'status': case['status'],
                    'physical_time_s': case['physical_time_s'],
                    'full_record_duration_s': case['full_record_duration_s'],
                    'peak_roof_UX_m': case['peak_roof_UX_m'],
                    'peak_roof_UY_m': case['peak_roof_UY_m'],
                    'terminal_roof_UX_m': case['terminal_roof_UX_m'],
                    'terminal_roof_UY_m': case['terminal_roof_UY_m'],
                    'residual_roof_UX_m': case['residual_roof_UX_m'],
                    'residual_roof_UY_m': case['residual_roof_UY_m'],
                    'max_story_drift_X': case['max_story_drift_X'],
                    'max_story_drift_Y': case['max_story_drift_Y'],
                    'max_floor_edge_drift_X': case['max_floor_edge_drift_X'],
                    'max_floor_edge_drift_Y': case['max_floor_edge_drift_Y'],
                    'peak_base_shear_X_kN': case['peak_base_shear_X_kN'],
                    'peak_base_shear_Y_kN': case['peak_base_shear_Y_kN'],
                    'peak_floor_relative_accel_X_m_s2': case['peak_floor_relative_accel_X_m_s2'],
                    'peak_floor_relative_accel_Y_m_s2': case['peak_floor_relative_accel_Y_m_s2'],
                    'case_output': str(output / case_name / state / case['orientation'])
                    if config.get('limit_state') == 'Both'
                    else str(output / case_name / case['orientation']),
                }
                rows.append(row)
        completed.append(dict(value=value, output_dir=str(output / case_name)))
        write_rows(output / 'Material_Sensitivity_Comparison.csv', rows)
        (output / 'Material_Sensitivity_Summary.json').write_text(
            json.dumps({
                'status': 'IN_PROGRESS' if index < len(candidates) else 'COMPLETED',
                'parameter': parameter,
                'candidate_values': candidates,
                'completed_cases': completed,
                'comparison_csv': 'Material_Sensitivity_Comparison.csv',
                'interpretation': 'One-factor exploratory comparison only; no candidate is selected as an optimum or design-approved.',
            }, indent=2), encoding='utf-8')

    return {
        'status': 'COMPLETED',
        'parameter': parameter,
        'candidate_values': candidates,
        'completed_cases': completed,
        'comparison_csv': str(output / 'Material_Sensitivity_Comparison.csv'),
    }

def _run(config):
    _set_run_stage('configuration_validation',output_dir=str(config.get('output_dir','')))
    if config.get('limit_state')=='Both':
        base=Path(config['output_dir']);base.mkdir(parents=True,exist_ok=True);results={}
        for state in ('ULS','SLS'):
            print('[RESEARCH STATE START]',state,flush=True)
            results[state]=run(dict(config,limit_state=state,output_dir=str(base/state)))
            (base/'Research_Batch_Summary_V161.json').write_text(json.dumps(results,indent=2),encoding='utf8')
        return results
    transient_system=config.get('transient_system','UmfPack')
    if transient_system not in TRANSIENT_SYSTEMS:
        raise ValueError('transient_system must be one of: '+', '.join(TRANSIENT_SYSTEMS))
    gravity_system=config.get('gravity_system','UmfPack')
    if gravity_system not in TRANSIENT_SYSTEMS:
        raise ValueError('gravity_system must be one of: '+', '.join(TRANSIENT_SYSTEMS))
    excitation=str(config.get('diagnostic_excitation','XY')).upper()
    if excitation not in ('XY','X','Y','ZERO'):
        raise ValueError('diagnostic_excitation must be XY, X, Y or ZERO')
    if config.get('diagnostic_zero_damping') and config.get('diagnostic_mass_damping'):
        raise ValueError('Select only one diagnostic damping override')
    max_subdivision_depth=config.get('max_subdivision_depth',5)
    if isinstance(max_subdivision_depth,bool) or not isinstance(max_subdivision_depth,int) or not 0<=max_subdivision_depth<=8:
        raise ValueError('max_subdivision_depth must be an integer from 0 through 8')
    _set_run_stage('loading_analysis_dependencies')
    from OpenSees_Complete_Export_V118 import build_complete_model
    from OpenSees_Input_Records_V130 import _read_peer_text_record
    from OpenSees_Nonlinear_Time_History_NBC105_V116 import _advance_nonlinear_interval,_configure_nonlinear_transient
    from OpenSees_Step13_Analysis_Basis_V115 import rayleigh_coefficients
    from OpenSees_Response_Checks_V132 import export_history_checks
    from components.shared.response_recorders import (
    append_base_shear, frame_solver_tag_catalog, selected_member_response,
    support_resultants, write_base_shear_roof_curve,
        write_recorder_index, write_rows,
    )
    full_wall=bool(config.get('nonlinear_walls',False))
    thesis_intent=config.get('analysis_intent')=='THESIS_NLTHA'
    # Explicit thesis-level job intent must not silently use elastic core walls,
    # nominal reference rebars, zero damping or a short diagnostic excitation.
    # These are necessary input gates only, NOT an approval of the FSAM model.
    if thesis_intent:
        if not config.get('soil_c_primary_nltha',False):
            raise ValueError('THESIS_NLTHA requires soil_c_primary_nltha=true')
        if not full_wall:
            raise ValueError('THESIS_NLTHA requires calibrated nonlinear core-wall elements')
        # Fail closed before constructing a domain: the current research
        # builder still defines PEER-web/M30 sensitivity FSAM and nominal
        # frame materials. A truthful materials banner is NOT calibration.
        from components.nonlinear_time_history.research_building_materials import (
            check_project_material_qualification)
        check_project_material_qualification(config)
        if not config.get('approved_frame_reinforcement_csv'):
            raise ValueError('THESIS_NLTHA requires source-reviewed frame reinforcement CSV')
        # Project has RCC core openings. Requiring an independently reviewed
        # manifest prevents a wall mesh from appearing valid merely because
        # there were no hole declarations to check.
        if not config.get('wall_openings_manifest'):
            raise ValueError('THESIS_NLTHA requires independently reviewed wall_openings_manifest')
        if excitation!='XY' or sorted(config.get('orientations',['XY','YX']))!=['XY','YX']:
            raise ValueError('THESIS_NLTHA requires simultaneous XY and YX in separate domains')
        if config.get('diagnostic_zero_damping') or config.get('diagnostic_mass_damping'):
            raise ValueError('THESIS_NLTHA cannot use a diagnostic damping override')
        if not config.get('nbc105_2025_design_evidence'):
            raise ValueError('THESIS_NLTHA requires independently reviewed modal and SeismoMatch evidence')
        # Independent SeismoMatch logs must prove BOTH component factors and
        # the original common factor. The applied OpenSees scale remains 1.0.
        from components.nonlinear_time_history.soil_c_physics_preflight import (
            evaluate_original_seismomatch_logs)
        evaluate_original_seismomatch_logs(
            config.get('seismomatch_original_pair_scale_evidence'))
        if not config.get('damping_reference_modes'):
            raise ValueError('THESIS_NLTHA requires two explicit damping reference modes')
        if config.get('rayleigh_device_exclusion_reviewed') is not True:
            raise ValueError('THESIS_NLTHA requires element/device Rayleigh damping exclusion audit')
        if config.get('duration_s'):
            raise ValueError('THESIS_NLTHA must use full record duration, not a diagnostic truncation')
    profile=profile_for_config(config)
    _RUN_CONTEXT.update(profile=profile,diagnostic_excitation=excitation,
                        transient_system=transient_system,gravity_system=gravity_system,
                        nonlinear_walls=full_wall,
                        diagnostic_zero_damping=bool(config.get('diagnostic_zero_damping')),
                        diagnostic_mass_damping=bool(config.get('diagnostic_mass_damping')))
    import os
    os.environ['OPENSEES_RESEARCH_MATERIAL_BASIS']=config.get('material_basis','PUBLISHED_REFERENCE')
    os.environ['OPENSEES_STEELMPF_TRANSITION']=config.get('steelmpf_transition','OPENSEES_DOCUMENTED')
    from components.nonlinear_time_history.research_building_materials import (
        brace_steel_parameters, validate_material_overrides,
    )
    material_overrides=validate_material_overrides(config.get('material_overrides',{}))
    if not full_wall and any(key.startswith(('frame.', 'wall.')) for key in material_overrides):
        raise ValueError('Frame and wall material overrides require nonlinear_walls=true.')
    os.environ['OPENSEES_RESEARCH_MATERIAL_OVERRIDES']=json.dumps(material_overrides)
    source,out=validate_output_separation(config['model_folder'],config['output_dir'])
    out.mkdir(parents=True,exist_ok=True)
    model=out/'isolated_model';model.mkdir(exist_ok=True)
    _set_run_stage('reading_records_and_model_inputs')
    for name in ('OpenSees_Complete_Model_Data_V118.json','OpenSees_Complete_Model_Config_V118.json','OpenSees_Complete_Export_Report_V118.json','OpenSees_Load_Conversion_Audit.json','OpenSees_Source_Model_Metadata_V118.json'):shutil.copy2(source/name,model/name)
    if (source/'OpenSees_Complete_Story_Masters_V118.csv').exists():shutil.copy2(source/'OpenSees_Complete_Story_Masters_V118.csv',model/'OpenSees_Complete_Story_Masters_V118.csv')
    # An explicitly selected source register must be copied into the isolated model
    # and its SHA and reviewer kept with each case. Never auto-approve bar schedules.
    register=config.get('approved_frame_reinforcement_csv')
    if register:
        source_register=Path(register).resolve()
        if not source_register.is_file():
            raise FileNotFoundError(source_register)
        target_register=model/'Approved_ETABS_Frame_Reinforcement.csv'
        shutil.copy2(source_register,target_register)
        os.environ['OPENSEES_APPROVED_REINFORCEMENT_REGISTER']=str(target_register)
    else:
        os.environ.pop('OPENSEES_APPROVED_REINFORCEMENT_REGISTER',None)
    for name in ('OpenSees_Element_Overrides_V125.json',
                 'OpenSees_Complete_Element_Map_V118.json'):
        if (source/name).is_file():shutil.copy2(source/name,model/name)
    data=json.loads((model/'OpenSees_Complete_Model_Data_V118.json').read_text(encoding='utf-8-sig'));start=time.perf_counter();unit_factor={'g':9.80665,'m/s2':1.};records=[]
    # Stage 01: audit source wall geometry before expensive gravity and transient solves.
    from components.nonlinear_time_history.wall_diagnostics import write_wall_audit
    write_wall_audit(data, out/'NLTHA_Wall_Geometry_Preflight.json')
    # Stage 03: compare declared ETABS wall openings against actual quad occupancy.
    # No manifest is not approval; the absence is made explicit in the results.
    from components.nonlinear_time_history.wall_topology import write_opening_report
    opening_manifest=config.get('wall_openings_manifest')
    if thesis_intent:
        from components.nonlinear_time_history.wall_topology import (
            verify_project_opening_manifest_required)
        verify_project_opening_manifest_required(config)
    if opening_manifest:
        opening_report=write_opening_report(
            data,opening_manifest,out/'NLTHA_Wall_Opening_Preflight.json')
        if thesis_intent and opening_report['status']!='GEOMETRY_SCREEN_PASSED':
            raise ValueError(
                'THESIS_NLTHA wall openings require nonempty verified opening declarations')
    else:
        (out/'NLTHA_Wall_Opening_Preflight.json').write_text(json.dumps(dict(
            status='UNVERIFIED_NO_MANIFEST',
            warning='No independently checked ETABS opening schedule supplied'),indent=2),
            encoding='utf-8')
    write_rows(out/'Frame_Solver_Tag_Catalog.csv',frame_solver_tag_catalog(data['frames']))
    for key in ('x_path','y_path'):
        values,step,units=_read_peer_text_record(config[key]);records.append((np.asarray(values),step,units))
    # Soil-C research suite is hash-bound to the verified 16 matched exports.
    # Requires opt-in, so unrelated pre-existing exploratory workflows are
    # not silently forced onto the Soil-C thesis record catalogue.
    suite_mode=bool(config.get('soil_c_primary_nltha',False))
    if suite_mode:
        from components.nonlinear_time_history.soil_c_physics_preflight import (
            audit_soil_c_analysis_config)
        source_config_gate=audit_soil_c_analysis_config(config)
        (out/'Soil_C_Thesis_Input_Basis.json').write_text(
            json.dumps(source_config_gate,indent=2,allow_nan=False),encoding='utf-8')
    source_pair_audit=None
    endpoint_policy=dict(status='AS_ORIGINALLY_EXPORTED',added_samples=0)
    if suite_mode:
        from components.nonlinear_time_history.soil_c_nltha_suite import (
            verify_runner_pair, reconcile_loma_runtime_pair)
        if config.get('source_records_already_scaled') is not True:
            raise ValueError('Soil-C thesis matched inputs require source_records_already_scaled=true')
        if float(config.get('scale',1.))!=1.:
            raise ValueError('Already matched Soil-C records must have OpenSees scale=1.0')
        if str(config.get('soil_type','C')).upper()!='C':
            raise ValueError('Soil-C primary suite cannot be relabeled as Soil D')
        source_pair_audit=verify_runner_pair(
            config['x_path'],config['y_path'],
            registered_event=config.get('earthquake_event'),
            gorkha_processing_approved=config.get('gorkha_processing_reviewed') is True,
            reviewer=config.get('engineering_reviewer'),
            loma_end_policy=config.get('loma_end_policy','reject'))
        if source_pair_audit['event']=='Loma Prieta':
            records,endpoint_policy=reconcile_loma_runtime_pair(
                records, policy=config.get('loma_end_policy','reject'),
                reviewer=config.get('engineering_reviewer'))
        # Keep numeric arrays for existing OpenSees time-series use.
        records=[(np.asarray(values),dt,unit) for values,dt,unit in records]
        (out/'Soil_C_Matched_Source_Gate.json').write_text(json.dumps(dict(
            input_source=source_pair_audit,runtime_endpoint=endpoint_policy,
            source_model_requires_independent_material_verification=True),
            indent=2,allow_nan=False),encoding='utf-8')
    from components.nonlinear_time_history.thesis_quality import audit_ground_motion_pair
    input_quality=audit_ground_motion_pair(records,[config['x_path'],config['y_path']])
    if suite_mode:
        input_quality['reviewed_runtime_extension']=endpoint_policy
        input_quality['original_input_source_sha256']=[
            source_pair_audit['source_sha256_A'],source_pair_audit['source_sha256_B']]
    # Read the selected scale BEFORE computing the paired source fingerprint.
    # Previous versions referenced 'scale' before assignment here.
    scale=float(config.get('scale',1.))
    if not math.isfinite(scale) or scale<=0:
        raise ValueError('Scale must be finite and positive')
    # SeismoMatch outputs are ALREADY spectrum-matched. Their encoded
    # accelerations must not be scaled again. The Path factor remains the
    # acceleration UNIT conversion (g -> m/s2), and the applied pair scale is 1.
    # File names/headers establish processing provenance, not proof that
    # NBC 105 §9.3.2.2(c,d) scaling factors were within range/shared.
    from components.nonlinear_time_history.seismomatch_audit import (
        assess_preprocessed_sources)
    matching_preflight=assess_preprocessed_sources(
        config['x_path'],config['y_path'],open_sees_scale=scale,
        declared_already_matched=config.get('source_records_already_scaled'))
    (out/'SeismoMatch_Source_Provenance.json').write_text(json.dumps(
        matching_preflight,indent=2,allow_nan=False),encoding='utf-8')
    matched_source=matching_preflight['both_headers_identify_matched_outputs']


    # Pair fingerprint is constant across XY/YX and binds the input files,
    # sampling, units and selected scale. This is NOT spectrum-match proof.
    record_pair_sha256=hashlib.sha256(json.dumps(dict(
        x=input_quality['records'][0]['sha256'],
        y=input_quality['records'][1]['sha256'],
        dt=input_quality['records'][0]['dt_s'],
        units=[r['source_units'] for r in input_quality['records']],
        scale=scale,source_processing=matching_preflight['status']),sort_keys=True).encode('utf-8')).hexdigest()
    (out/'NLTHA_Input_Quality.json').write_text(json.dumps(input_quality,indent=2,allow_nan=False),encoding='utf-8')
    print('[NLTHA INPUT QUALITY] finite records, matching sampling and file hashes verified',flush=True)
    if abs(records[0][1]-records[1][1])>1e-10 or len(records[0][0])!=len(records[1][0]):raise ValueError('Pair duration/digitization mismatch; reconcile records explicitly')
    record_end=(len(records[0][0])-1)*records[0][1];end=record_end if not config.get('duration_s') else min(float(config['duration_s']),record_end)
    if end<=0:raise ValueError('Duration must be positive')
    dt=float(config.get('dt_s',.005))
    if not math.isfinite(dt) or dt<=0 or dt>min(.01,records[0][1]):raise ValueError('dt must be positive and no larger than record dt or 0.01 s')
    # Optional strict NBC 105:2025 metadata gate. Exploratory trials without
    # actual spectral evidence remain research diagnostics, NOT NBC passes.
    from components.nonlinear_time_history.nbc105_2025_audit import write_preflight
    nbc_evidence=config.get('nbc105_2025_design_evidence')
    if nbc_evidence is not None:
        write_preflight(out/'NBC105_2025_NLTHA_Input_Screen.json',nbc_evidence,
            record_dt_s=records[0][1],integration_dt_s=dt,
            # For pre-matched waveforms, this verifies the claimed ORIGINAL
            # lower factor, not an additional OpenSees Path multiplier.
            selected_scale=(min(float(nbc_evidence['factor_x']),
                                float(nbc_evidence['factor_y']))
                            if matched_source else scale),
            orientations=config.get('orientations',['XY','YX']))
    else:
        (out/'NBC105_2025_NLTHA_Input_Screen.json').write_text(json.dumps(dict(
            status='NOT_EVALUATED_DESIGN_EVIDENCE_NOT_SUPPLIED',
            scope='Research exploratory run only; spectral scaling, Tn90 and source selection unverified'
        ),indent=2),encoding='utf-8')
    brace=brace_steel_parameters(material_overrides)
    brace_fy=brace['fy_mpa']
    brace_b=brace['hardening_ratio']
    brace_e='source-section modulus' if brace['E_mpa'] is None else f'{brace["E_mpa"]:g} MPa'
    assumptions=dict(profile=profile,scope='EXPLORATORY_ASSUMED_MATERIALS_NOT_DESIGN_ACCEPTANCE',source_model_sha256=hashlib.sha256((source/'OpenSees_Complete_Model_Data_V118.json').read_bytes()).hexdigest(),frame_materials='Existing illustrative M35 / Fe550 RC templates; not source M45 project calibration',wall_materials='ELASTIC WALLS: source E/thickness; flexural factor ULS0.5 / SLS0.7 through plate modifier. Frame-nonlinear exploratory model; full FSAM wall trial failed and is not substituted silently.',braces=f'112 hinged SHS objects: corotTruss / Steel01, source area, E={brace_e}, Fy={brace_fy:g} MPa, b={brace_b:g}; ordinary axial brace idealization only, no flexural buckling/fatigue/fracture and not a BRB core qualification',material_overrides=material_overrides,floors='Source geometry, IS16700 ULS0.25/SLS0.35 elastic slab bending and gross membrane stiffness',gravity='Assembled source preload and nodal masses retained',limitation='Exploratory response and runtime only. No NBC design acceptance, reinforcement or collapse assessment.',records=[dict(path=str(config[k]),source_units=r[2],unit_conversion=unit_factor[r[2]],motion_scale=scale,total_Path_factor=unit_factor[r[2]]*scale) for k,r in zip(('x_path','y_path'),records)])
    if full_wall:
        assumptions.update(frame_materials='Literature unconfined Concrete01 + nominal Fe500 Steel02; existing bar-layout templates remain assumptions',wall_materials='Nonlinear E_SFI_MVLEM_3D + ConcreteCM / SteelMPF / FSAM; exact selected parameters exported per property',material_basis=config.get('material_basis','PUBLISHED_REFERENCE'),steelmpf_transition_profile=config.get('steelmpf_transition','OPENSEES_DOCUMENTED'),limitation='Research material transfer and reinforcement templates, not experimental building calibration or NBC design acceptance')
    from Define_Section_V109 import RC_SECTION_CONFIG
    assumptions['RC_template_inputs']=RC_SECTION_CONFIG
    (out/'ASSUMPTIONS_NOT_DESIGN.json').write_text(json.dumps(assumptions,indent=2),encoding='utf-8');(out/'RunConfig.json').write_text(json.dumps(config,indent=2),encoding='utf-8');summary=[]
    for orientation in config.get('orientations',['XY','YX']):
        if orientation not in ('XY','YX'):raise ValueError('Orientation must be XY or YX')
        case=out/orientation;case.mkdir(exist_ok=True);print('[EXPLORATORY START]',orientation,'no calibration or design approval implied',flush=True)
        _set_run_stage('model_build_and_gravity',orientation=orientation,case_output_dir=str(case))
        build_complete_model(
            model, mode='nonlinear', preload=True,
            limit_state=config.get('limit_state','ULS'),
            research_profile=profile, gravity_system=gravity_system)
        import openseespy.opensees as ops
        support_nodes=[
            int(node) for node,flags in data['supports'].items()
            if any(bool(value) for value in flags[:3])
        ]
        if not support_nodes:
            raise ValueError('The assembled model export has no support nodes for base-shear recording.')
        base_reaction_reference=support_resultants(ops,support_nodes)
        if full_wall:
            shutil.copy2(model/'Research_Material_Assignment_V161.json',case/'Research_Material_Assignment_V161.json')
        groups=sorted(data['diaphragms'],key=lambda r:r['master_xyz'][2]);baseline={g['master_tag']:list(ops.nodeDisp(g['master_tag'])) for g in groups}
        print('[EXPLORATORY MODAL] Computing 20 initial nonlinear modes; transient has not started',flush=True)
        _set_run_stage('modal_analysis',orientation=orientation,case_output_dir=str(case))
        from components.shared.eigen_solver import solve_eigen
        eigenvalues=solve_eigen(ops,20);periods=[2*math.pi/math.sqrt(v) for v in eigenvalues if v>0]
        if len(periods)!=20:raise ValueError('Inspected nonlinear modes incomplete')
        # The last of 20 eigenmodes is NOT Tn90; cumulative effective mass
        # must be obtained from independent reviewed X and Y participation.
        bound=min(records[0][1],.01,periods[0]/100.)
        if dt>bound:
            raise ValueError(f'Chosen dt {dt} exceeds preliminary first-mode screen {bound:g}s; reduce dt')
        damping_modes=config.get('damping_reference_modes')
        if damping_modes is not None:
            from components.nonlinear_time_history.soil_c_physics_preflight import (
                assess_modal_damping_and_time_step)
            selected_audit=assess_modal_damping_and_time_step(
                config,periods,records[0][1])
            (case/'Soil_C_Selected_Modal_Damping_and_Time_Step.json').write_text(
                json.dumps(selected_audit,indent=2,allow_nan=False),encoding='utf-8')
            # Same physical modes for both orientations; define two 5% targets
            # instead of arbitrarily damping the first and 20th modes.
            mode_a,mode_b=selected_audit['damping_reference_modes_1_based']
            damping_periods=(periods[mode_a-1],periods[mode_b-1])
        else:
            if thesis_intent:
                raise ValueError('Thesis requires audited damping reference modes')
            damping_periods=(max(periods),min(periods))
            (case/'Soil_C_Selected_Modal_Damping_and_Time_Step.json').write_text(
                json.dumps(dict(status='EXPLORATORY_UNREVIEWED_FIRST_LAST_MODE_DAMPING',
                    damping_reference_periods_s=damping_periods,
                    note='Exploratory only: first/20th damping can distort nonlinear higher modes'),
                    indent=2,allow_nan=False),encoding='utf-8')
        alpha,beta=rayleigh_coefficients(*damping_periods,.05)
        if config.get('diagnostic_mass_damping'):alpha,beta=2*.05*min(math.sqrt(v) for v in eigenvalues),0.
        if config.get('diagnostic_zero_damping'):alpha,beta=0.,0.
        print('[TRANSIENT PROBE]', 'excitation='+excitation, 'zero_damping='+str(bool(config.get('diagnostic_zero_damping'))), 'system='+transient_system, flush=True)
        (case/'Initial_Modal_Damping.json').write_text(json.dumps(dict(eigenvalues=eigenvalues,periods_s=periods,alphaM=alpha,betaKcomm=beta,dt_screen_s=bound),indent=2))
        ops.rayleigh(alpha,0.,0.,beta)
        _set_run_stage('transient_setup',orientation=orientation,case_output_dir=str(case))
        from components.nonlinear_time_history.nbc105_horizontal_input import (
            write_manifest,unit_and_scale)
        input_manifest=write_manifest(
            case/'OpenSees_Bidirectional_Input_Commands.json',
            orientation=orientation,record_a=config['x_path'],record_b=config['y_path'],
            dt_s=records[0][1],units_a=records[0][2],units_b=records[1][2],
            pair_scale=scale,already_scaled=matched_source)
        # Diagnostic X/Y/ZERO runs remain independent failure-isolation probes,
        # NOT complete paired-code analyses. For the real case, X and Y each
        # receive one original source component, and YX interchanges them.
        for mapping,r in zip(input_manifest['commands'],
                             diagnostic_record_inputs(records,orientation,excitation)):
            values,step,units=r
            direction=mapping['dof']
            tag=mapping['path_series_tag']
            factor=unit_and_scale(units,scale,already_scaled=matched_source)
            if not math.isclose(factor,mapping['path_factor_m_s2'],rel_tol=1e-12):
                raise ValueError('Source unit/rotation mapping mismatch')
            ops.timeSeries('Path',tag,'-dt',step,'-values',*values.tolist(),'-factor',factor)
            ops.pattern('UniformExcitation',tag,direction,'-accel',tag)
        _configure_nonlinear_transient(ops)
        configure_transient_system(ops,transient_system)
        suspect_tags=config.get('diagnostic_suspect_tags',[])
        if not isinstance(suspect_tags,list) or len(suspect_tags)>16:
            raise ValueError('diagnostic_suspect_tags must be a list of <=16 element tags')
        suspect_tags=[int(x) for x in suspect_tags]
        if any(x<=0 for x in suspect_tags):
            raise ValueError('diagnostic_suspect_tags must be positive')
        diag={
            'evidence_output_path':str(case/'First_Step_Failure_Evidence.json'),
            'element_map_path':str(model/'OpenSees_Complete_Element_Map_V118.json'),
            'suspect_tags':suspect_tags if suspect_tags else None,
            'efficient_recovery':True,
            'max_subdivision_depth':max_subdivision_depth,
        };rows=[];last=time.perf_counter();case_start=last
        stories=[dict(node=g['master_tag'],story_name='Storey_'+str(g['storey_number']),height=g['master_xyz'][2]-(groups[i-1]['master_xyz'][2] if i else data['base_z_m'])) for i,g in enumerate(groups)]
        wall_tags=[100001+len(data['frames'])+i for i,e in enumerate(data['shells']) if e['category']=='SHEAR WALL']
        tracked_wall=int(config.get('tracked_wall_tag',wall_tags[0])) if wall_tags else None
        tracked=int(config.get('tracked_frame_tag',100001))
        if not 100001<=tracked<100001+len(data['frames']):raise ValueError('Tracked frame solver tag is outside the assembled frame range')
        requested_tags=config.get('tracked_element_tags',[])
        if not isinstance(requested_tags,list) or len(requested_tags)>32:
            raise ValueError('tracked_element_tags must be a list of no more than 32 frame solver tags')
        tracked_tags=sorted({tracked,*[int(tag) for tag in requested_tags]})
        if any(not 100001<=tag<100001+len(data['frames']) for tag in tracked_tags):
            raise ValueError('A selected tracked element tag is outside the assembled frame range')
        tracked_nodes={
            tag: [int(node) for node in data['frames'][tag-100001]['nodes']]
            for tag in tracked_tags
        }
        tracked_baseline={
            node: list(ops.nodeDisp(node))
            for nodes in tracked_nodes.values() for node in nodes
        }
        from components.nonlinear_time_history.ground_acceleration import (
            applied_ground_acceleration,relative_to_absolute_floor_acceleration)
        (case/'Ground_Acceleration_Recording_Method.json').write_text(json.dumps(dict(
            source="https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html",
            input_source_units=[r[2] for r in records],
            conversion_factor_by_unit=unit_factor,
            additional_spectral_scale=scale,
            orientation=orientation,excitation=excitation,
            source_record_end_time_s=record_end,
            note="Relative node acceleration + interpolated support acceleration = horizontal absolute floor acceleration for uniform support excitation only.",
            vertical_ground_motion_recorded=False,
            absolute_acceleration_not_applicable_to_multi_support_excitations=True
        ),indent=2),encoding='utf-8')
        from components.nonlinear_time_history.device_recording import (
            active_device_catalog,baseline_axial_projection,device_sample,summarize_device_demands)
        active_devices=active_device_catalog(model,data['frames'])
        device_initial={d['tag']:baseline_axial_projection(ops,d,data['nodes'])
                        for d in active_devices}
        device_rows=[]
        tracked_element_rows=[]
        from components.nonlinear_time_history.full_record_gate import (
            verify_numeric_accepted_row)
        def capture():
            row={'time_s':ops.getTime()};previous=[0.]*6
            ground_xy=applied_ground_acceleration(
                records,time_s=row['time_s'],orientation=orientation,
                excitation=excitation,additional_spectral_scale=scale)
            row['ground_AccelX_m_s2']=ground_xy[0]
            row['ground_AccelY_m_s2']=ground_xy[1]
            for story,g in zip(stories,groups):
                u=[a-b for a,b in zip(ops.nodeDisp(g['master_tag']),baseline[g['master_tag']])];name=story['story_name']
                acceleration=list(ops.nodeAccel(g['master_tag']))
                for j,axis in enumerate(('X','Y','Z')):row[name+'_U'+axis+'_m']=u[j]
                row[name+'_UX_relative_accel_m_s2']=acceleration[0]
                row[name+'_UY_relative_accel_m_s2']=acceleration[1]
                absolute_xy=relative_to_absolute_floor_acceleration(
                    acceleration,ground_xy)
                row[name+'_UX_absolute_accel_m_s2']=absolute_xy[0]
                row[name+'_UY_absolute_accel_m_s2']=absolute_xy[1]
                for j,axis in enumerate(('X','Y','Z'),3):row[name+'_R'+axis+'_rad']=u[j]
                row[name+'_RZ_rad']=u[5]
                for j,axis in enumerate(('X','Y')):row[name+'_drift_'+axis]=(u[j]-previous[j])/story['height']
                previous=u
            append_base_shear(
                row,ops,support_nodes,base_reaction_reference)
            force=list(ops.eleResponse(tracked,'localForce'))
            section=list(ops.eleResponse(tracked,'section',1,'deformation'))
            if len(force)==12:
                row['selected_frame_N_kN']=force[0];row['selected_frame_My_kNm']=force[4];row['selected_frame_Mz_kNm']=force[5]
            if len(section)>=3:
                row['section_axial_strain']=section[0];row['section_kappa_z_1_per_m']=section[1];row['section_kappa_y_1_per_m']=section[2]
            if full_wall and tracked_wall is not None:
                for response,label in [('panel_strain','wall_panel_strain'),('panel_stress','wall_panel_stress_kN_m2')]:
                    values=list(ops.eleResponse(tracked_wall,'RCPanel',1,response))
                    for j,value in enumerate(values):row[label+'_'+str(j+1)]=value
                for response,label in [('ShearDef','wall_shear_deformation'),('Curvature','wall_curvature')]:
                    values=list(ops.eleResponse(tracked_wall,response))
                    for j,value in enumerate(values):row[label+'_'+str(j+1)]=value
            for element_tag in tracked_tags:
                response=selected_member_response(
                    ops,element_tag,tracked_nodes[element_tag],data['nodes'],
                    tracked_baseline)
                forces=response['local_end_forces_kN_kNm']
                tracked_element_rows.append(dict(
                    time_s=row['time_s'],
                    element_tag=element_tag,
                    source_object=data['frames'][element_tag-100001]['object'],
                    category=data['frames'][element_tag-100001]['category'],
                    axial_extension_m=response['axial_extension_m'],
                    axial_force_kN=forces[0],
                    local_force_vector_json=json.dumps(forces,separators=(',',':')),
                ))
            for device in active_devices:
                device_rows.append(device_sample(ops,device,data['nodes'],device_initial[device['tag']]))
            # Check every accepted step immediately, not only after an entire
            # record has consumed hours of CPU time. A zero solver return
            # code does NOT imply every recorder response is finite.
            verify_numeric_accepted_row(row, row_index=len(rows))
            rows.append(row)
            if suspect_tags and config.get('analysis_intent','RESEARCH_DIAGNOSTIC')!='THESIS_NLTHA':
                from components.nonlinear_time_history.failure_evidence import snapshot_selected_state
                snapshot_selected_state(ops,
                    case/'Last_Accepted_Wall_State.json',
                    suspect_tags=suspect_tags,
                    stage="LAST_ACCEPTED_COMMITTED")
        history=case/'Building_Nonlinear_history.csv'
        _set_run_stage('transient_analysis',orientation=orientation,case_output_dir=str(case),
                       requested_duration_s=end,record_duration_s=record_end,
                       integration_step_s=dt,started_at=datetime.datetime.now().astimezone().isoformat())
        with history.open('w',newline='',encoding='utf-8-sig') as stream:
            capture();writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerow(rows[-1]);stream.flush()
            try:
                while ops.getTime()<end-1e-10:
                    before=len(rows);_advance_nonlinear_interval(ops,min(dt,end-ops.getTime()),max_depth=max_subdivision_depth,on_accept=capture,diagnostics=diag)
                    writer.writerows(rows[before:])
                    if time.perf_counter()-last>5:
                        last=time.perf_counter();stream.flush()
                        minimum_dt=diag.get('minimum_accepted_dt_s')
                        print(
                            f'[EXPLORATORY PROGRESS] {orientation}: t={ops.getTime():.3f}/{end:.3f}s '
                            f'| wall={last-case_start:.1f}s | failed_attempts={diag.get("failed_attempts",0)} '
                            f'| bisections={diag.get("bisections",0)} '
                            f'| min_accepted_dt={minimum_dt if minimum_dt is not None else "n/a"}',
                            flush=True)
            except Exception as exc:
                try:
                    _write_failure_report(
                        case,config,exc,filename='FAILED.json',
                        details=dict(orientation=orientation,time_s=ops.getTime(),
                                     elapsed_s=time.perf_counter()-case_start,
                                     accepted_history_rows=len(rows),
                                     solver_diagnostics=diag,analysis_scope=assumptions['scope']))
                except OSError as report_error:
                    print('[FAILURE REPORT ERROR]',repr(report_error),flush=True)
                raise
        _set_run_stage('response_postprocessing',orientation=orientation,case_output_dir=str(case),
                       accepted_history_rows=len(rows),completed_time_s=ops.getTime())
        (case/'NBC105_Exploratory_Time_History_RunConfig_V138.json').write_text(json.dumps(dict(model_script='../isolated_model/OpenSees_Complete_Model_Data_V118.json',scope=assumptions['scope'])),encoding='utf-8')
        edge_peaks=export_history_checks(rows,stories,case,'EXPLORATORY_'+orientation,config.get('limit_state','ULS'),model_script=str(model/'OpenSees_Complete_Model_Data_V118.json'))
        base_curve_path=write_base_shear_roof_curve(
            case/('BaseShear_RoofDisplacement_'+orientation+'.csv'),
            rows,stories[-1]['story_name'])
        tracked_frame_curve=[]
        for row in rows:
            if 'selected_frame_My_kNm' in row and 'section_kappa_z_1_per_m' in row:
                tracked_frame_curve.append(dict(
                    time_s=row['time_s'],
                    selected_frame_N_kN=row.get('selected_frame_N_kN'),
                    selected_frame_My_kNm=row['selected_frame_My_kNm'],
                    section_axial_strain=row.get('section_axial_strain'),
                    section_kappa_z_1_per_m=row['section_kappa_z_1_per_m'],
                    section_kappa_y_1_per_m=row.get('section_kappa_y_1_per_m')))
        tracked_frame_path=None
        if tracked_frame_curve:
            tracked_frame_path=write_rows(
                case/'Tracked_Frame_Moment_Curvature.csv',
                tracked_frame_curve)
        tracked_wall_curve=[]
        wall_indexes=sorted({
            int(key.rsplit('_',1)[1])
            for key in rows[0]
            if key.startswith('wall_panel_strain_')
        })
        for row in rows:
            for index in wall_indexes:
                strain_key='wall_panel_strain_'+str(index)
                stress_key='wall_panel_stress_kN_m2_'+str(index)
                if strain_key in row and stress_key in row:
                    tracked_wall_curve.append(dict(
                        time_s=row['time_s'],panel_component=index,
                        strain=row[strain_key],
                        stress_kN_m2=row[stress_key]))
        tracked_wall_path=None
        if tracked_wall_curve:
            tracked_wall_path=write_rows(
                case/'Tracked_Wall_Stress_Strain.csv',tracked_wall_curve)
        tracked_element_path=write_rows(
            case/'Tracked_Element_Force_Displacement.csv',
            tracked_element_rows)
        if device_rows:
            write_rows(case/'Device_Accepted_Step_History.csv',device_rows)
            demands=summarize_device_demands(device_rows)
            write_rows(case/'Device_Demand_Summary.csv',demands)
            (case/'Device_Demand_Summary.json').write_text(json.dumps(demands,indent=2,allow_nan=False),encoding='utf-8')
        recorder_files=[
            (history.name,[
                'accepted adaptive substep time','all-story Ux/Uy/Uz/Rx/Ry/Rz',
                'all-story relative UX/UY acceleration',
                'all-story drift X/Y','incremental support reactions',
                'signed base shear X/Y','tracked frame forces/section strains',
                'tracked E-SFI panel response']),
            (base_curve_path.name,[
                'time_s','roof_UX_m','roof_UY_m',
                'base_shear_X_kN','base_shear_Y_kN']),
            ('Concurrent_Final_Frame_Actions.csv',[
                'final-time frame end axial/shear/torsion/moments']),
        ]
        if tracked_frame_path:
            recorder_files.append((tracked_frame_path.name,[
                'selected frame My versus section curvature',
                'selected frame axial force and section axial strain']))
        if tracked_wall_path:
            recorder_files.append((tracked_wall_path.name,[
                'selected E-SFI wall panel stress-strain histories']))
        recorder_files.append((tracked_element_path.name,[
            'selected frame/brace/device tag axial force and gravity-relative projected axial extension',
            'local force vector retained as JSON in native OpenSees local-end ordering']))
        if device_rows:
            recorder_files.append(('Device_Accepted_Step_History.csv',
                ['active FVD/BRB basicForce or axialForce, relative displacement/velocity']))
            recorder_files.append(('Device_Demand_Summary.csv',
                ['peak device demand and signed work; not qualified energy/fatigue']))
        write_recorder_index(
            case,'nonlinear_time_history',
            recorder_files,
            notes=[
                'Support reactions and base shear are incremental relative to the gravity-frozen state.',
                'The base-shear/roof-displacement file preserves synchronized accepted states and can be plotted as a hysteresis history.',
                'Selected member channels are controlled by tracked_frame_tag and tracked_element_tags; confirm each selected device local axis aligns with its member axis.',
                'The final frame-action table is a final-state snapshot, not an all-elements time history.',
            ],
        )
        # Every reported criterion retains the staged-model scope.
        for file in list(case.glob('Drift_Check_*.csv'))+list(case.glob('Floor_Edge_Drift_*.csv')):
            with file.open(encoding='utf-8-sig',newline='') as stream:checks=list(csv.DictReader(stream))
            if checks:
                for check in checks:check['model_scope']=profile
                with file.open('w',encoding='utf-8-sig',newline='') as stream:
                    writer=csv.DictWriter(stream,fieldnames=list(checks[0]));writer.writeheader();writer.writerows(checks)
        action_rows=[]
        for element in range(100001,100001+len(data['frames'])):
            force=list(ops.eleResponse(element,'localForce'))
            if len(force)==12:
                for end_label,values in [('I',force[:6]),('J',force[6:])]:action_rows.append(dict(element_tag=element,end=end_label,time_s=ops.getTime(),N_kN=values[0],Vy_kN=values[1],Vz_kN=values[2],T_kNm=values[3],My_kNm=values[4],Mz_kNm=values[5],scope=assumptions['scope']))
        if action_rows:
            with (case/'Concurrent_Final_Frame_Actions.csv').open('w',newline='',encoding='utf-8-sig') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(action_rows[0]));writer.writeheader();writer.writerows(action_rows)
        deformation={str(n):list(ops.nodeDisp(int(n))) for n in data['nodes']}
        (case/('Deformation_EXPLORATORY_'+orientation+'_V132.json')).write_text(json.dumps(dict(nodes=data['nodes'],elements=[e['nodes'] for e in data['frames']+data['shells']],displacements=deformation,dof_availability=[True]*6,note='EXPLORATORY assumed literature materials; total final response at t='+str(ops.getTime())+' s. Not design acceptance.')),encoding='utf-8')
        roof=stories[-1]['story_name']
        # Stage 05: accept only finite, chronological histories through the
        # requested physical time; no automatic promotion to design approval.
        from components.nonlinear_time_history.full_record_gate import write_accepted_history_gate
        completion_gate=write_accepted_history_gate(case,rows,record_end,end)
        result=dict(
            completion_gate=completion_gate,
            orientation=orientation,
            # Case-matrix evidence fields are explicit, not inferred from folder names.
            pair_id=str(config.get('pair_id','UNSPECIFIED')),
            variant_id=str(config.get('variant_id','UNASSIGNED')),
            limit_state=config.get('limit_state','ULS'),
            record_sha256=record_pair_sha256,
            model_sha256=assumptions['source_model_sha256'],
            wall_model='E_SFI_MVLEM_3D' if full_wall else 'ELASTIC',
            frame_model='LITERATURE_CONCRETE01_NOMINAL_FE500' if full_wall else 'NONLINEAR_ILLUSTRATIVE_RC_FIBERS',
            gravity_system=gravity_system,transient_system=transient_system,
            diagnostic_excitation=excitation,
            diagnostic_zero_damping=bool(config.get('diagnostic_zero_damping')),
            diagnostic_mass_damping=bool(config.get('diagnostic_mass_damping')),
            rayleigh_alphaM=alpha,rayleigh_betaKcomm=beta,
            material_overrides=material_overrides,
            status='COMPLETED_TRUNCATED_TRIAL' if end<record_end else 'COMPLETED_EXPLORATORY_RECORD',
            physical_time_s=end,full_record_duration_s=record_end,
            elapsed_s=time.perf_counter()-case_start,
            peak_roof_UX_m=max(abs(r[roof+'_UX_m']) for r in rows),
            peak_roof_UY_m=max(abs(r[roof+'_UY_m']) for r in rows),
            terminal_roof_UX_m=rows[-1][roof+'_UX_m'],
            terminal_roof_UY_m=rows[-1][roof+'_UY_m'],
            residual_roof_UX_m=rows[-1][roof+'_UX_m'] if end>=record_end-1e-8 else None,
            residual_roof_UY_m=rows[-1][roof+'_UY_m'] if end>=record_end-1e-8 else None,
            max_story_drift_X=max(abs(r[s['story_name']+'_drift_X']) for r in rows for s in stories),
            max_story_drift_Y=max(abs(r[s['story_name']+'_drift_Y']) for r in rows for s in stories),
            max_floor_edge_drift_X=edge_peaks.get('X'),
            max_floor_edge_drift_Y=edge_peaks.get('Y'),
            peak_base_shear_X_kN=max(abs(r['base_shear_X_kN']) for r in rows),
            peak_base_shear_Y_kN=max(abs(r['base_shear_Y_kN']) for r in rows),
            peak_floor_relative_accel_X_m_s2=max(
                abs(r[s['story_name']+'_UX_relative_accel_m_s2']) for r in rows for s in stories),
            peak_floor_relative_accel_Y_m_s2=max(
                abs(r[s['story_name']+'_UY_relative_accel_m_s2']) for r in rows for s in stories),
            peak_roof_torsion_rad=max(abs(r[roof+'_RZ_rad']) for r in rows),
            periods_inspected_s=periods,
            initial_damping_ratios=[alpha/(2*math.sqrt(v))+beta*math.sqrt(v)/2 for v in eigenvalues],
            diagnostics=diag,scope=assumptions['scope'])
        from OpenSees_Building_Response_V144 import plot_response
        plot_response(history,case,tracked)
        (case/'Case_Summary.json').write_text(json.dumps(result,indent=2));summary.append(result);print('[EXPLORATORY COMPLETE]',json.dumps(result),flush=True);ops.wipe()
    from components.nonlinear_time_history.thesis_quality import write_quality_report
    write_quality_report(out,summary)
    result=dict(cases=summary,elapsed_s=time.perf_counter()-start,scope=assumptions['scope']);(out/'Exploratory_Summary.json').write_text(json.dumps(result,indent=2));_set_run_stage('completed',output_dir=str(out));return result

def recover_saved_report(folder,output_dir):
    """Recover postprocessing from accepted CSV rows; never rerun/approve a solver."""
    source=Path(folder).resolve();out=Path(output_dir).resolve()
    if out==source or source in out.parents:raise ValueError('Recovery output must be outside the original run folder')
    out.mkdir(parents=True,exist_ok=True)
    config=json.loads((source/'RunConfig.json').read_text(encoding='utf-8-sig'))
    assumptions=json.loads((source/'ASSUMPTIONS_NOT_DESIGN.json').read_text(encoding='utf-8-sig'))
    data=json.loads((source/'isolated_model/OpenSees_Complete_Model_Data_V118.json').read_text(encoding='utf-8-sig'))
    groups=sorted(data['diaphragms'],key=lambda g:g['master_xyz'][2])
    cases=[]
    for orientation in config.get('orientations',['XY','YX']):
        history=source/orientation/'Building_Nonlinear_history.csv'
        if not history.is_file():continue
        with history.open(encoding='utf-8-sig',newline='') as stream:rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(stream)]
        if not rows or any(not math.isfinite(r['time_s']) for r in rows):raise ValueError('Invalid saved history')
        if any(b['time_s']<=a['time_s'] for a,b in zip(rows,rows[1:])):raise ValueError('History times must strictly increase')
        case=out/orientation;case.mkdir(exist_ok=True);shutil.copy2(history,case/history.name)
        roof='Storey_'+str(groups[-1]['storey_number']);t=rows[-1]['time_s'];requested=float(config.get('duration_s') or 0)
        result=dict(orientation=orientation,status='RECOVERED_SAVED_HISTORY_REPORT',recorded_time_s=t,requested_trial_duration_s=requested,requested_trial_reached=bool(requested and t>=requested-1e-8),accepted_rows=len(rows),peak_roof_UX_m=max(abs(r[roof+'_UX_m']) for r in rows),peak_roof_UY_m=max(abs(r[roof+'_UY_m']) for r in rows),scope=assumptions['scope'],note='Postprocessing recovery only. Original run ended with reporting exception. No missing solver diagnostics, full-record completion, calibration or design acceptance inferred.')
        from OpenSees_Building_Response_V144 import plot_response
        plot_response(history,case,int(config.get('tracked_frame_tag',100001)))
        (case/'Case_Summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');cases.append(result)
        from matplotlib.figure import Figure
        fig=Figure(figsize=(11,6),layout='constrained');axes=fig.subplots(2,1)
        for axis,ax in zip(('X','Y'),axes):ax.plot([r['time_s'] for r in rows],[r[roof+'_U'+axis+'_m']*1000 for r in rows]);ax.set(xlabel='Time (s)',ylabel='Roof U'+axis+' (mm)',title='Recovered '+orientation+' saved trial / nonlinear frames, elastic walls');ax.grid(alpha=.25)
        fig.savefig(case/'Recovered_Roof_History.png',dpi=150)
    report=dict(cases=cases,source_run=str(source),scope=assumptions['scope'],recovered_at=datetime.datetime.now().astimezone().isoformat())
    (out/'Recovered_Summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();config=json.loads(Path(a.config).read_text(encoding='utf-8-sig'))
    run(config)
