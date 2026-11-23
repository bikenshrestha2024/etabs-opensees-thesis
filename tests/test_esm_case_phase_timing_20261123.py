"""Generated ESM timing contract. Synthetic source, no native OpenSees solve.

[REF docs/source/components/equivalent_static/calculation_and_gui.py.md]
"""
import ast
import json
import tempfile
import unittest
from pathlib import Path

from components.equivalent_static.calculation_and_gui import write_outputs
from components.equivalent_static.code_basis import calculate_esm


class ESMCasePhaseTimingTests(unittest.TestCase):
    def test_generated_solver_writes_source_bound_phase_times_and_preserves_solver(self):
        rows=[]
        for i,h in enumerate([4.,8.],1):
            rows.append(dict(height_m=h,story_number=i,story_name=f"S{i}",
                master_node_tag=100+i,dead_load_kN=1000.,other_live_load_kN=100.,
                storage_live_load_kN=0.,roof_live_load_kN_ignored=0.))
        result=calculate_esm(rows,period_s=1.5,soil_type='C',zoning_factor_z=.35,
            importance_factor_i=1.,limit_state='ULS',r_mu=3.,omega_u=1.3,
            omega_s=1.15,diagnostic_reference=True)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            paths=write_outputs(root/'story.csv',rows,result,'X',1,True,(24.,1),
                root,model_script=str(root/'test_model.py'))
            runner=Path(paths[2]).read_text(encoding='utf-8')
            ast.parse(runner)
            for token in (
                "NBC105_ESM_Case_Timings_",
                "'initial_signed_checks_s'",
                "'model_build_gravity_s'",
                "'lateral_solver_s'",
                "'response_export_s'",
                "'total_elapsed_s'",
                "'model_sha256'",
                "'support_case'",
                "'seismic_mass_policy'",
                "ensure_initial_checks(MODEL_WORKDIR)",
                "runpy.run_path(MODEL_BUILDER_SCRIPT",
                "ops.analyze(1)",
                "export_static_response(ops,",
            ):
                with self.subTest(token=token):
                    self.assertIn(token,runner)
            self.assertIn("schema':'esm-case-timing-v1",runner)

    def test_instrumented_runner_requires_matching_finite_timing_evidence(self):
        import hashlib
        import csv
        from components.equivalent_static.calculation_and_gui import verify_generated_esm_result
        from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            case='ULS_X+_E0'
            script=root/('OpenSees_Direct_NBC105_ESM_Load_And_Static_Analysis_'+case+'_V111.py')
            script.write_text('# NBC105_ESM_Case_Timings_\\n',encoding='utf-8')
            model=root/'OpenSees_Complete_Model_Data_V118.json'
            model.write_text('{}',encoding='utf-8')
            digest=hashlib.sha256(model.read_bytes()).hexdigest()
            (root/('NBC105_ESM_OpenSees_Response_META_'+case+'.json')).write_text(
                json.dumps(dict(model_sha256=digest,limit_state='ULS',axis='X',response_case=case)))
            (root/('NBC105_ESM_OpenSees_Response_'+case+'.json')).write_text(
                json.dumps([dict(response_case=case,height_m=4.,U_elastic_m=.001,U_design_m=.002,design_drift_ratio=.0002)]))
            (root/('NBC105_ESM_Calculation_'+case+'_V111.json')).write_text(
                json.dumps(dict(direction_case=case,limit_state='ULS',support_case='PHYSICAL_32',stories=[{}])))
            (root/('Response_Recorder_Index_'+case+'.json')).write_text(
                json.dumps(dict(analysis='equivalent_static',files=[{'name':'response.csv'}])))
            with (root/('NBC105_ESM_Support_Reactions_'+case+'.csv')).open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=['node_tag'])
                writer.writeheader()
                for tag in sorted(PROJECT_PRIMARY_32):writer.writerow({'node_tag':tag})
            with self.assertRaisesRegex(ValueError,'timing'):
                verify_generated_esm_result(script,root)
            timing_path=root/('NBC105_ESM_Case_Timings_'+case+'.json')
            valid=dict(schema='esm-case-timing-v1',response_case=case,limit_state='ULS',axis='X',
                model_sha256=digest,support_case='PHYSICAL_32',
                seismic_mass_policy='SOURCE_DISTRIBUTED',
                initial_signed_checks_s=1.1,model_build_gravity_s=2.2,
                lateral_solver_s=3.3,response_export_s=.5,total_elapsed_s=8.2)
            timing_path.write_text(json.dumps(valid))
            checked=verify_generated_esm_result(script,root)
            self.assertEqual(checked['timing_status'],'SOURCE_MATCHED_PERFORMANCE_EVIDENCE')
            self.assertEqual(checked['timings']['model_build_gravity_s'],2.2)
            valid['model_sha256']='0'*64
            timing_path.write_text(json.dumps(valid))
            with self.assertRaisesRegex(ValueError,'timing'):
                verify_generated_esm_result(script,root)
            valid['model_sha256']=digest
            valid['lateral_solver_s']=float('nan')
            timing_path.write_text(json.dumps(valid))
            with self.assertRaisesRegex(ValueError,'timing'):
                verify_generated_esm_result(script,root)

    def test_emitted_code_never_renames_physical_esm_response_outputs(self):
        from components.equivalent_static import calculation_and_gui as cg
        import inspect
        src=inspect.getsource(cg.write_outputs)
        self.assertIn("NBC105_ESM_OpenSees_Response_",src)
        self.assertIn("NBC105_ESM_Support_Reactions_",src)
        self.assertIn("BASE_SHEAR_ERROR_PCT",src)


if __name__=='__main__':unittest.main()
