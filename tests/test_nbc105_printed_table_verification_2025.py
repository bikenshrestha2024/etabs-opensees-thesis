"""Independent printed NBC 105:2025 table benchmark and component detailing checks.

Transcribed from the user's 137-page source PDF, printed pages 19, 24, 30,
32, 39 and 49-51. Tests contain independent source values (not imported
constants) so a shared accidental edit cannot make both sides agree.
"""
import math
import unittest

from components.nbc105.clause_03_scope_of_analysis import cracked_flexural_factor
from components.nbc105.clause_04_seismic_hazard import TABLE_4_1
from components.nbc105.clause_05_dynamic_characteristics import table_5_2_system_factors
from components.nbc105.clause_06_equivalent_static import esm_deflection_factor
from components.nbc105 import clause_10_parts_and_components as c10


class SourceTablesAndComponentDetailing(unittest.TestCase):
    def test_table_3_1_all_six_cracked_stiffness_rows(self):
        cases=[("beam",.35,.70),("column",.70,.90),
               ("cracked wall",.50,.70),("uncracked wall",.80,.90),
               ("masonry wall",.45,.60),("flat slab",.25,.50)]
        for name,uls,sls in cases:
            self.assertAlmostEqual(cracked_flexural_factor(name,"ULS"),uls)
            self.assertAlmostEqual(cracked_flexural_factor(name,"SLS"),sls)

    def test_table_4_1_four_soil_categories(self):
        expected={"A":(.1,.5,4.,2.5),"B":(.1,.7,4.,2.5),
                  "C":(.1,1.,4.,2.5),"D":(.5,2.,5.,2.25)}
        for name,values in expected.items():
            row=TABLE_4_1[name]
            self.assertEqual(tuple(row[k] for k in ("Ta","Tc","Td","alpha")),values)

    def test_table_5_2_all_twenty_one_seismic_system_rows(self):
        source=[
            (4,1.5,1.25),(4,1.5,1.25),(4,1.5,1.25),
            (4,1.5,1.25),(4,1.5,1.25),(3,1.3,1.15),
            (3,1.3,1.15),(4,1.5,1.25),(3,1.3,1.15),
            (3,1.3,1.15),(2.5,1.2,1.1),(2.5,1.2,1.1),
            (2,1.2,1.1),(4,1.5,1.25),(4,1.5,1.25),
            (3.5,1.4,1.2),(3.5,1.4,1.2),(4,1.5,1.25),
            (3.5,1.4,1.2),(3.5,1.4,1.2),(2.5,1.2,1.1)]
        for i,expected in enumerate(source,1):
            row=table_5_2_system_factors(i)
            self.assertEqual(tuple(row[k] for k in ("Rmu","Omega_u","Omega_s")),expected)

    def test_table_6_1_all_story_deflection_rows(self):
        self.assertEqual([esm_deflection_factor(i) for i in range(1,8)],
                         [1.,.97,.94,.91,.88,.85,.85])

    def test_table_10_1_resonance_interpolation_and_off_resonance(self):
        for delta,expected in [(0,2.5),(.1,2.2),(.25,1.75),(.5,1),(.6,1)]:
            self.assertAlmostEqual(c10.component_amplification_factor(2,2+delta),expected)

    def test_table_10_2_3_values(self):
        self.assertEqual(c10.component_ductility_factor("low"),1.5)
        self.assertEqual(c10.component_ductility_factor("moderate"),2.5)
        self.assertEqual(c10.component_importance_factor("hazardous"),1.5)
        self.assertEqual(c10.component_importance_factor("other"),1.)

    def test_clause_10_4_d_light_safety_cable_minimum_four_times_weight(self):
        self.assertAlmostEqual(c10.light_safety_cable_design_capacity(2.),8.)
        for bad in (-1.,0.,float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                c10.light_safety_cable_design_capacity(bad)


if __name__=="__main__":
    unittest.main()
