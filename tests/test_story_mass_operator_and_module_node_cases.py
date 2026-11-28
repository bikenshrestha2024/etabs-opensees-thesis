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

    def test_etabs_floor_mass_comparison_preserves_direction_and_inertia(self):
        from components.model.story_mass_operator import compare_etabs_story_mass
        model={"base_z_m":0., "nodes":{"1":[-1.,0.,3.],"2":[1.,0.,3.]},
               "nodal_mass":{"1":2.,"2":2.}, "supports":{},
               "diaphragms":[{"master_tag":100,"master_xyz":[0.,0.,3.],
                              "storey_number":1,"slave_node_tags":[1,2]}]}
        rows=[{"Story":"Story1","UX":3900.,"UY":3800.,"RZ":3.,"X":0.,"Y":0.,"Z":3.}]
        report=compare_etabs_story_mass(model,rows)
        self.assertEqual(report["native_mass_matrix_equivalence"],"NOT_VERIFIED")
        self.assertAlmostEqual(report["floors"][0]["UX_difference_t"],.1)
        self.assertAlmostEqual(report["floors"][0]["UY_difference_t"],.2)
        self.assertAlmostEqual(report["floors"][0]["RZ_difference_t_m2"],1.)
        self.assertEqual(model["nodal_mass"],{"1":2.,"2":2.})
        for bad in ([dict(rows[0],Z=3.01)], rows+rows, [dict(rows[0],RZ=-1.)], []):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                compare_etabs_story_mass(model,bad)

    def test_original_object_mass_reference_includes_base_and_polar_inertia(self):
        from components.model.story_mass_operator import compare_etabs_object_lumped_mass
        from components.nbc105.constants import GRAVITY_M_S2 as g
        model={"base_z_m":0.,"nodes":{"1":[-1.,0.,0.],"2":[-1.,0.,3.],"3":[1.,0.,3.],"4":[0.,0.,3.]},
               "nodal_mass":{"1":1.,"2":0.,"3":0.,"4":4.},"supports":{"1":[1]*6},
               "diaphragms":[{"master_tag":100,"master_xyz":[0.,0.,3.],"storey_number":1}],
               "load_provenance":[{"source":"FRAME:b","pattern":"Dead","node":4,"downward_kN":4*g},
                                  {"source":"FRAME:c","pattern":"Dead","node":1,"downward_kN":g}]}
        conn={"node_map":[{"etabs_point_name":str(n),"opensees_node_tag":n,"coordinates_m":model["nodes"][str(n)]} for n in (1,2,3)],
              "elements":[{"dimension":"line_2_node","etabs_object":"b","node_names":["2","3"],"node_tags":[2,3]},
                          {"dimension":"line_2_node","etabs_object":"c","node_names":["1","2"],"node_tags":[1,2]}]}
        ref=[{"Story":"Base","UX":500.,"UY":500.,"RZ":0.,"X":-1.,"Y":0.,"Z":0.},
             {"Story":"Story1","UX":4500.,"UY":4500.,"RZ":4.5,"X":0.,"Y":0.,"Z":3.}]
        import copy
        original=copy.deepcopy(model)
        out=compare_etabs_object_lumped_mass(model,conn,{"Dead":1.},ref,reference_g_m_s2=g)
        self.assertAlmostEqual(out["base_mass_t"],.5)
        self.assertAlmostEqual(out["floors"][0]["mass_residual_X_t"],0.)
        self.assertAlmostEqual(out["floors"][0]["RZ_residual_t_m2"],0.)
        self.assertAlmostEqual(out["floors"][0]["horizontal_reference_matrix"][1][2],-.5)
        self.assertEqual(out["native_mass_matrix_equivalence"],"NOT_VERIFIED")
        self.assertEqual(model,original)
        bad=copy.deepcopy(model);bad["nodal_mass"]["4"]=5.
        with self.assertRaisesRegex(ValueError,"ledger"):
            compare_etabs_object_lumped_mass(bad,conn,{"Dead":1.},ref,reference_g_m_s2=g)
        bad=copy.deepcopy(conn);bad["elements"][0]["node_names"][0]="1"
        with self.assertRaisesRegex(ValueError,"identity"):
            compare_etabs_object_lumped_mass(model,bad,{"Dead":1.},ref,reference_g_m_s2=g)

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
