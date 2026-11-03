"""PEER Appendix B.3 input cards should never be treated as project inputs."""
import unittest
from pathlib import Path
from components.nonlinear_time_history.paper_specimen_sources import appendix_b3_material_inputs
FILE=Path(__file__).resolve().parents[1]/"Research_Components/paper_specimens/PEER_2015_12_RW_A15_B3_SFI_INPUTS.json"
class Tests(unittest.TestCase):
    def test_source_properties(self):
        out=appendix_b3_material_inputs(FILE)
        self.assertEqual(out["specimen"],"RW-A15-P10-S78")
        self.assertEqual(out["fsam"]["boundary"]["rho_y"],0.0587)
        self.assertAlmostEqual(out["boundary_vs_web_concrete"]["confined_boundary"]["fpcc_kN_m2"],
                               -10.479723*6.894757293168361*1000)
        self.assertFalse(out["apply_to_building_allowed"])
    def test_paper_transition_not_software_default(self):
        self.assertEqual(appendix_b3_material_inputs(FILE)["steel_mpf"]["transition"]["cR1"],18.5)
if __name__=="__main__":
    unittest.main()
