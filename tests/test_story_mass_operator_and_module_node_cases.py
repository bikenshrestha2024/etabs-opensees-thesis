"""TDD: source-consistent floor mass condensation and OpenSees GUI case selection.

Synthetic numerical model only; native ETABS/25-storey analysis not executed.
[REF docs/superpowers/plans/2026-11-22-esm-support-and-storey-mass-audit.md]
"""
import unittest
from pathlib import Path
from components.model.story_mass_operator import story_lumped_mass_plan

ROOT=Path(__file__).resolve().parents[1]


class StoryMassOperatorTests(unittest.TestCase):
    def test_two_floors_lump_intermediate_mass_at_correct_master_with_inertia(self):
        # First floor receives an intermediate wall mass; both centers are at x=0.
        model={
            "base_z_m":0.,
            "nodes":{"1":[-1.,0.,3.],"2":[1.,0.,3.],"3":[0.,0.,1.5],
                     "4":[0.,0.,6.],"5":[0.,0.,0.]},
            "nodal_mass":{"1":2.,"2":2.,"3":1.,"4":3.,"5":9.},
            "supports":{"5":[1]*6},
            "diaphragms":[
                {"master_tag":100,"master_xyz":[0.,0.,3.],
                 "slave_node_tags":[1,2],"storey_number":1},
                {"master_tag":200,"master_xyz":[0.,0.,6.],
                 "slave_node_tags":[4],"storey_number":2},
            ]
        }
        plan=story_lumped_mass_plan(model)
        self.assertEqual(plan["horizontal_mass_by_master"][100]["mass"],5.)
        self.assertEqual(plan["horizontal_mass_by_master"][100]["Jz"],4.)
        self.assertEqual(plan["horizontal_mass_by_master"][200]["mass"],3.)
        self.assertEqual(plan["active_source_horizontal_mass"],8.)
        self.assertEqual(plan["intermediate_mass"],1.)
        self.assertEqual(plan["plan_status"],"STORY_LUMPING_NUMERICALLY_RECONCILED_NOT_NATIVE_ACCEPTED")
        self.assertEqual(plan["unassigned_horizontal_mass"],0.)

    def test_mass_centroid_not_matching_master_fails_closed(self):
        model={
            "base_z_m":0.,
            "nodes":{"1":[1.,0.,3.]},
            "nodal_mass":{"1":2.}, "supports":{},
            "diaphragms":[{"master_tag":100,"master_xyz":[0.,0.,3.],
                          "storey_number":1,"slave_node_tags":[1]}]
        }
        with self.assertRaisesRegex(ValueError,"center|centroid"):
            story_lumped_mass_plan(model)

    def test_all_module_gui_sources_expose_physical_case(self):
        for source in (
            "components/equivalent_static/calculation_and_gui.py",
            "components/modal/gui_and_reports.py",
            "components/response_spectrum/model_analysis.py",
            "components/linear_time_history/runner_and_gui.py",
            "components/nonlinear_time_history/runner_and_gui.py",
        ):
            with self.subTest(source=source):
                text=(ROOT/source).read_text(encoding="utf8")
                self.assertIn("PHYSICAL_32",text)
                self.assertIn("SOURCE_76",text)
                self.assertIn("WALL_BASE_97",text)
                self.assertIn("OPENSEES_SUPPORT_CASE",text)
        model=(ROOT/"components/model/assembly.py").read_text(encoding="utf8")
        self.assertIn("OPENSEES_SEISMIC_MASS_POLICY",model)
        self.assertIn("story_lumped_mass_plan",model)


if __name__=="__main__":
    unittest.main()
