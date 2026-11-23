"""Synthetic ESM runner output policy: skip only optional image/Excel work.

OpenSees solver, gravity, reactions, response JSON/CSV, source provenance,
and saved-evidence gates must never be disabled by fast-IO mode.
"""
import ast
import inspect
import tempfile
import unittest
from pathlib import Path

from components.equivalent_static.calculation_and_gui import write_outputs
from components.equivalent_static.code_basis import calculate_esm


class ESMFastIOTests(unittest.TestCase):
    def test_generated_script_has_opt_in_optional_reports_and_keeps_core(self):
        stories=[
            dict(height_m=4.,story_number=1,story_name="S1",master_node_tag=101,
                 dead_load_kN=1000.,storage_live_load_kN=0.,other_live_load_kN=100.),
            dict(height_m=8.,story_number=2,story_name="S2",master_node_tag=102,
                 dead_load_kN=900.,storage_live_load_kN=0.,other_live_load_kN=100.),
        ]
        result=calculate_esm(
            stories,limit_state='ULS',period_s=1.5,soil_type='C',
            zoning_factor_z=0.35,importance_factor_i=1.,
            r_mu=3.,omega_u=1.3,omega_s=1.15,diagnostic_reference=True)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            generated=write_outputs(root/'story.csv',stories,result,'X',1,True,
                                    (24.,1),root,model_script=str(root/'model.py'))
            script=Path(generated[2]).read_text(encoding='utf-8')
            ast.parse(script)
            self.assertIn('OPENSEES_ESM_OPTIONAL_OUTPUTS',script)
            self.assertIn("NBC105_ESM_OpenSees_Response_",script)
            self.assertIn('BASE_SHEAR_ERROR_PCT',script)
            self.assertIn('export_static_response',script)

    def test_gui_fast_io_mode_is_visible_and_avoids_worker_tk_reads(self):
        from components.equivalent_static.calculation_and_gui import ESMGui
        src=inspect.getsource(ESMGui)
        self.assertIn('self.esm_optional_case_reports',src)
        self.assertIn('OPENSEES_ESM_OPTIONAL_OUTPUTS',src)
        self.assertIn('Detailed PNG/XLSX per case',src)
        self.assertIn('support_case_for_run',src)
        self.assertIn('mass_policy_for_run',src)


if __name__=='__main__':
    unittest.main()
