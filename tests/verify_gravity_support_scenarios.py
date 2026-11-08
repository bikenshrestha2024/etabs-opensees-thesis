"""Synthetic two-gravity-case support strategy audit tests."""
import tempfile
import unittest
from pathlib import Path
from components.gravity.support_scenarios import (
    SOURCE, CONTINUOUS, compare_wall_support_gravity, export_wall_support_comparison
)


class DualWallGravityTests(unittest.TestCase):
    def setUp(self):
        self.first=self.make(SOURCE,[1,2],[100,200],-0.02,[])
        self.second=self.make(CONTINUOUS,[1,2,101],[90,180,30],-0.016,[101])
    @staticmethod
    def make(mode,tags,reactions,uz,added):
        return dict(ok=True,wall_support_strategy=mode,
            gravity_profile='GRAVITY_1.0D_1.0L',added_wall_support_tags=added,
            nodes=[dict(tag=n,x_m=float(i),y_m=0.,z_m=0.) for i,n in enumerate(tags)],
            reactions=[dict(node_tag=n,rz_kN=v) for n,v in zip(tags,reactions)],
            report=dict(applied_vertical_load_kN=300.,
                support_vertical_reaction_kN=float(sum(reactions)),
                equilibrium_error_percent=0.,
                max_downward_vertical_displacement_m=uz))
    def test_both_cases_keep_full_gravity_and_report_support_deltas(self):
        audit=compare_wall_support_gravity(self.first,self.second)
        self.assertEqual(audit['same_full_gravity_applied_kN'],300)
        self.assertEqual(audit['summary'][0]['support_count'],2)
        self.assertEqual(audit['summary'][1]['support_count'],3)
        self.assertEqual(audit['reaction_total_difference_kN'],0)
        self.assertEqual(audit['max_Uz_difference_m'],0.004)
        self.assertEqual(
            [r for r in audit['per_node'] if r['status']=='CONTINUOUS_ONLY'][0]['node_tag'],'101')
        with tempfile.TemporaryDirectory() as d:
            dest=export_wall_support_comparison(audit,d)
            self.assertTrue((dest/'Gravity_Wall_Base_Strategy_Comparison.xlsx').exists())
            self.assertTrue((dest/'Gravity_Wall_Base_Nodal_Reaction_Differences.csv').exists())
    def test_mixed_gravity_factors_are_rejected(self):
        self.second['gravity_profile']='AS_CONFIGURED'
        with self.assertRaisesRegex(ValueError,'not full'):
            compare_wall_support_gravity(self.first,self.second)
    def test_failed_analysis_rejected(self):
        self.first['ok']=False
        with self.assertRaisesRegex(ValueError,'did not complete'):
            compare_wall_support_gravity(self.first,self.second)
    def test_differing_applied_gravity_rejected(self):
        self.second['report']['applied_vertical_load_kN']=287.
        with self.assertRaisesRegex(ValueError,'different applied'):
            compare_wall_support_gravity(self.first,self.second)
    def test_gui_uses_isolated_output_directories(self):
        src=(Path(__file__).resolve().parents[1]/
             'components/gravity/gui_and_reports.py').read_text(encoding='utf8')
        self.assertIn('Run BOTH wall-base gravity strategies',src)
        self.assertIn('OPENSEES_GRAVITY_WALL_SUPPORT_STRATEGY',src)
        self.assertIn('root/mode',src)


if __name__=='__main__':
    unittest.main()
