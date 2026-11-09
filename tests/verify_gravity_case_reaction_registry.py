"""Regression coverage for 32/76/97 solved reaction display, no solver required."""
import json
import tempfile
import unittest
from pathlib import Path
from components.gravity.reaction_case_registry import (
    SCENARIO_SUPPORTS,checked_reaction_result,register_case,current_case)

class ReactionCaseRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.model=self.root/"model.py"
        self.model.write_text("print('model')\n",encoding="utf-8")
        self.output=self.root/"results"
        self.output.mkdir()

    def payload(self,scenario="ETABS_NONZERO_REACTION_DIAGNOSTIC",
                applied=320047.788933,variation=0.0):
        n=SCENARIO_SUPPORTS[scenario]
        each=(applied+variation)/n
        return {
            "ok":True,"model_script":str(self.model.resolve()),
            "gravity_profile":"GRAVITY_1.0D_1.0L",
            "wall_support_strategy":scenario,
            "support_node_tags":list(range(1,n+1)),
            "reactions":[{"node_tag":i,"rz_kN":each} for i in range(1,n+1)],
            "report":{"support_vertical_reaction_kN":applied+variation,
                      "applied_vertical_load_kN":applied}
        }

    def write(self,payload,filename="Gravity_Result_V110.json"):
        f=self.output/filename
        f.write_text(json.dumps(payload),encoding="utf-8")
        return f

    def test_same_applied_load_for_all_three_cases(self):
        for mode,n in SCENARIO_SUPPORTS.items():
            with self.subTest(mode=mode):
                result=checked_reaction_result(self.payload(mode),self.model,
                    scenario=mode,profile="GRAVITY_1.0D_1.0L")
                self.assertEqual(result["support_count"],n)
                self.assertAlmostEqual(result["summed_reaction_kN"],320047.788933,places=5)
                self.assertAlmostEqual(result["applied_load_kN"],320047.788933,places=5)

    def test_case_switch_fails_closed_and_cannot_show_other_case(self):
        mode="ETABS_NONZERO_REACTION_DIAGNOSTIC"
        result=self.write(self.payload(mode))
        register_case(self.output,result,self.model,scenario=mode,
            profile="GRAVITY_1.0D_1.0L")
        self.assertIsNotNone(current_case(self.output,self.model,scenario=mode,
            profile="GRAVITY_1.0D_1.0L"))
        self.assertIsNone(current_case(self.output,self.model,
            scenario="ETABS_SOURCE_SUPPORTS",profile="GRAVITY_1.0D_1.0L"))
        self.assertIsNone(current_case(self.output,self.model,
            scenario=mode,profile="AS_CONFIGURED"))

    def test_changed_model_code_invalidates_result(self):
        mode="ETABS_NONZERO_REACTION_DIAGNOSTIC"
        f=self.write(self.payload(mode))
        register_case(self.output,f,self.model,scenario=mode,
            profile="GRAVITY_1.0D_1.0L")
        self.model.write_text("print('different')\n",encoding="utf-8")
        self.assertIsNone(current_case(self.output,self.model,scenario=mode,
            profile="GRAVITY_1.0D_1.0L"))

    def test_missing_node_reaction_is_rejected(self):
        mode="ETABS_SOURCE_SUPPORTS"
        p=self.payload(mode);p["reactions"].pop()
        with self.assertRaisesRegex(ValueError,"incomplete"):
            checked_reaction_result(p,self.model,scenario=mode,
                profile="GRAVITY_1.0D_1.0L")

    def test_wrong_scenario_node_count_is_rejected(self):
        p=self.payload()
        with self.assertRaisesRegex(ValueError,"another support case"):
            checked_reaction_result(p,self.model,
                scenario="CONTINUOUS_WALL_BASE_FIXED",profile="GRAVITY_1.0D_1.0L")

    def test_numeric_balance_mismatch_does_not_change_applied(self):
        mode="ETABS_SOURCE_SUPPORTS"
        p=self.payload(mode,variation=9000)
        result=checked_reaction_result(p,self.model,scenario=mode,
            profile="GRAVITY_1.0D_1.0L")
        self.assertFalse(result["balance_pass"])
        self.assertEqual(result["applied_load_kN"],320047.788933)
        self.assertAlmostEqual(result["summed_reaction_kN"],329047.788933,places=5)

if __name__=="__main__":
    unittest.main()
