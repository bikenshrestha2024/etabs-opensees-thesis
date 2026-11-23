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

    def test_emitted_code_never_renames_physical_esm_response_outputs(self):
        from components.equivalent_static import calculation_and_gui as cg
        import inspect
        src=inspect.getsource(cg.write_outputs)
        self.assertIn("NBC105_ESM_OpenSees_Response_",src)
        self.assertIn("NBC105_ESM_Support_Reactions_",src)
        self.assertIn("BASE_SHEAR_ERROR_PCT",src)


if __name__=='__main__':unittest.main()
