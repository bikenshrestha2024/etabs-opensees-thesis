"""Synthetic, independent earthquake response and source-case semantics tests."""
import csv
import tempfile
import unittest
from pathlib import Path
from components.validation.eq_pdelta_case_contract import (
    check_etabs_case_contract,initial_pattern_factors)
from components.validation.eq_pdelta_comparison import compare_saved_case

class EQTests(unittest.TestCase):
    def test_initial_factor_and_dependent_reference(self):
        factor=initial_pattern_factors("X")
        self.assertEqual(factor["Self Weight"],1.2)
        self.assertEqual(factor["Floor Finish"],1.2)
        self.assertEqual(factor["Partition"],1.2)
        self.assertEqual(factor["Wall"],1.2)
        self.assertEqual(factor["Live"],0.5)
        self.assertEqual(factor["EQX"],1.5)
        init=dict(analysis_type="Nonlinear Static",starts_unstressed=True,
                  geometric_nonlinearity="P-Delta",load_pattern_factors=factor)
        self.assertEqual(check_etabs_case_contract(init,axis="X",
                         role="initial_positive"),[])
        dependent=dict(analysis_type="Linear Static",
                       use_nonlinear_case_stiffness=True,
                       initial_case_loads_included=False,
                       stiffness_source_case="EQX+ P Delta Initial",
                       load_pattern_factors={"EQX":1.0})
        self.assertEqual(check_etabs_case_contract(
            dependent,axis="X",role="dependent_positive",
            initial_case="EQX+ P Delta Initial"),[])
        dependent["initial_case_loads_included"]=True
        self.assertIn("DEPENDENT_MUST_EXCLUDE_INITIAL_LOADS",
                      check_etabs_case_contract(
                        dependent,axis="X",role="dependent_positive",
                        initial_case="EQX+ P Delta Initial"))
    def _write(self,path,values):
        with path.open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f)
            w.writerow(["story_name","elevation_m","story_shear_kN",
                        "displacement_m","drift_ratio"])
            w.writerows(values)
    def test_raw_comparison_and_blocked_design_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            self._write(path/"etabs.csv",[
                ["Story1",4,200,0.003,0.00075],
                ["Story2",8,100,0.006,0.00075]])
            self._write(path/"open.csv",[
                ["Story1",4,200,0.003,0.00075],
                ["Story2",8,100,0.006,0.00075]])
            md=dict(source_model_sha256="a"*64,units="kN_m",
                    support_strategy="ETABS_NONZERO_REACTION_DIAGNOSTIC",
                    response_scope="RAW_SIGNED_ANALYSIS",
                    eccentricity_branch="+E5",gravity_preload="source model",
                    pdelta_stiffness_source="EQX+ P Delta Initial",
                    load_pattern_factors={"EQX":1.0},limit_state="ULS",
                    model_equivalence_verified=True,
                    force_case_equivalence_verified=True,
                    preload_equivalence_verified=True,
                    coordinate_system="GLOBAL_XY",
                    etabs_eccentricity_branch="+E5",
                    opensees_eccentricity_branch="+E5",
                    opensees_story_shear_basis="RECOVERED_SECTION_CUT",
                    etabs_drift_basis="MASTER_CENTRE",
                    opensees_drift_basis="MASTER_CENTRE",
                    etabs_response_step="FINAL",
                    opensees_response_step="FINAL",
                    etabs_case_definition_verified=True,
                    opensees_case_definition_verified=True,
                    etabs_base_shear_kN=200.,opensees_base_shear_kN=200.)
            result=compare_saved_case(
                etabs_csv=path/"etabs.csv",opensees_csv=path/"open.csv",
                output_dir=path/"out",axis="X",etabs_case="EQX+ P-Delta",
                opensees_case="X tangent",metadata=md)
            self.assertEqual(result["status"],"COMPATIBLE_NUMERIC_SCREEN_ONLY")
            self.assertEqual(result["checked_rows"],7)
            self.assertEqual(result["scanned_failures"],0)
            md["response_scope"]="CODE_AMPLIFIED_DESIGN"
            other=compare_saved_case(
                etabs_csv=path/"etabs.csv",opensees_csv=path/"open.csv",
                output_dir=path/"out2",axis="X",etabs_case="EQX+ P-Delta",
                opensees_case="X tangent",metadata=md)
            self.assertEqual(other["status"],"BLOCKED_NOT_COMPARABLE")
            self.assertIn("RESPONSE_MUST_BE_RAW_NOT_DESIGN_AMPLIFIED",
                          other["blockers"])
    def test_missing_story_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            self._write(path/"etabs.csv",[["Story1",4,200,.003,.00075]])
            self._write(path/"open.csv",[["Story2",8,200,.003,.00075]])
            result=compare_saved_case(
                etabs_csv=path/"etabs.csv",opensees_csv=path/"open.csv",
                output_dir=path/"out",axis="X",etabs_case="EQX",
                opensees_case="EQX",metadata={})
            self.assertEqual(result["status"],"BLOCKED_NOT_COMPARABLE")
            self.assertIn("STORY_ID_SET_MISMATCH",result["blockers"])

if __name__=="__main__":
    unittest.main()
