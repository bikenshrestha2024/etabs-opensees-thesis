"""Regression coverage for 32/76/97 solved reaction display, no solver required."""
import json
import tempfile
import unittest
from pathlib import Path
from components.gravity.reaction_case_registry import (
    SCENARIO_SUPPORTS,checked_reaction_result,register_case,current_case,
    current_case_diagnostic)

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

    def test_distinguishes_missing_case_from_solved_result_and_stale_model(self):
        mode="ETABS_NONZERO_REACTION_DIAGNOSTIC"
        initial=current_case_diagnostic(
            self.output,self.model,scenario=mode,profile="GRAVITY_1.0D_1.0L")
        self.assertEqual(initial["status"],"NO_CASE_INDEX")
        f=self.write(self.payload(mode))
        register_case(self.output,f,self.model,scenario=mode,
                      profile="GRAVITY_1.0D_1.0L")
        solved=current_case_diagnostic(
            self.output,self.model,scenario=mode,profile="GRAVITY_1.0D_1.0L",
            expected_support_tags=range(1,33))
        self.assertEqual(solved["status"],"SOLVED_VERIFIED_INDEX")
        self.assertEqual(solved["result"]["support_count"],32)
        absent=current_case_diagnostic(
            self.output,self.model,scenario="ETABS_SOURCE_SUPPORTS",
            profile="GRAVITY_1.0D_1.0L")
        self.assertEqual(absent["status"],"CASE_NOT_INDEXED")
        self.model.write_text("print('new source')\\n",encoding="utf-8")
        stale=current_case_diagnostic(
            self.output,self.model,scenario=mode,profile="GRAVITY_1.0D_1.0L")
        self.assertEqual(stale["status"],"MODEL_SHA_CHANGED")
        self.assertIsNone(stale["result"])

    def test_digest_and_support_mismatch_are_not_labeled_never_analyzed(self):
        mode="ETABS_NONZERO_REACTION_DIAGNOSTIC"
        f=self.write(self.payload(mode))
        register_case(self.output,f,self.model,scenario=mode,
                      profile="GRAVITY_1.0D_1.0L")
        wrong=current_case_diagnostic(
            self.output,self.model,scenario=mode,profile="GRAVITY_1.0D_1.0L",
            expected_support_tags=range(2,34))
        self.assertEqual(wrong["status"],"SAVED_CASE_VALIDATION_BLOCKED")
        self.assertIn("support tags differ",wrong["reason"])
        self.assertIsNone(wrong["result"])
        data=self.payload(mode)
        data["reactions"][0]["rz_kN"]+=5.0
        data["reactions"][1]["rz_kN"]-=5.0
        f.write_text(json.dumps(data),encoding="utf-8")
        tampered=current_case_diagnostic(
            self.output,self.model,scenario=mode,profile="GRAVITY_1.0D_1.0L")
        self.assertEqual(tampered["status"],"SAVED_RESULT_HASH_CHANGED")

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

    def test_gravity_gui_reports_exact_result_availability_and_32_completion(self):
        from types import SimpleNamespace
        from components.gravity.gui_and_reports import GravityAnalysisGUI
        class Var:
            def __init__(self,value=""):self.value=value
            def get(self):return self.value
            def set(self,value):self.value=value
        mode="ETABS_NONZERO_REACTION_DIAGNOSTIC"
        gui=SimpleNamespace(
            solved_reaction_var=Var(),solved_reaction_status_var=Var(),
            model_var=Var(str(self.model)),output_var=Var(str(self.output)),
            gravity_profile_var=Var("GRAVITY_1.0D_1.0L"),
            reaction_support_var=Var(", ".join(map(str,range(1,33)))),
            reaction_support_verification_var=Var("SCREENING: 32 verified"),
            position_support_var=Var(""),
            _selected_wall_support_strategy=lambda:mode)
        GravityAnalysisGUI._refresh_case_reaction(gui)
        self.assertEqual(gui.solved_reaction_var.get(),"No indexed run")
        self.assertIn("NO_CASE_INDEX",gui.solved_reaction_status_var.get())
        f=self.write(self.payload(mode))
        register_case(self.output,f,self.model,scenario=mode,
                      profile="GRAVITY_1.0D_1.0L")
        GravityAnalysisGUI._refresh_case_reaction(gui)
        self.assertAlmostEqual(float(gui.solved_reaction_var.get()),
                               320047.788933,places=4)
        self.assertIn("32 solved supports",gui.solved_reaction_status_var.get())
        self.model.write_text("print('modified')\\n",encoding="utf-8")
        GravityAnalysisGUI._refresh_case_reaction(gui)
        self.assertEqual(gui.solved_reaction_var.get(),"Saved result unavailable")
        self.assertIn("MODEL_SHA_CHANGED",gui.solved_reaction_status_var.get())

    def test_gui_export_resolves_selected_nested_case_without_parent_result(self):
        from types import SimpleNamespace
        from components.gravity.gui_and_reports import GravityAnalysisGUI
        mode="ETABS_NONZERO_REACTION_DIAGNOSTIC"
        nested=self.output/"Gravity_Reaction_Diagnostic"/"20261109"
        nested.mkdir(parents=True)
        result=nested/"Gravity_Result_V110.json"
        result.write_text(json.dumps(self.payload(mode)),encoding="utf-8")
        register_case(self.output,result,self.model,scenario=mode,
                      profile="GRAVITY_1.0D_1.0L")
        var=lambda value:SimpleNamespace(get=lambda:value)
        gui=SimpleNamespace(output_var=var(str(self.output)),
            model_var=var(str(self.model)),gravity_profile_var=var("GRAVITY_1.0D_1.0L"),
            _selected_wall_support_strategy=lambda:mode)
        self.assertEqual(GravityAnalysisGUI._selected_result_path(gui),result.resolve())
        self.assertFalse((self.output/"Gravity_Result_V110.json").exists())
        gui.gravity_profile_var=var("AS_CONFIGURED")
        with self.assertRaisesRegex(ValueError,"No current completed"):
            GravityAnalysisGUI._selected_result_path(gui)

    def test_common_output_index_preserves_all_three_case_locations(self):
        paths=[]
        for mode in SCENARIO_SUPPORTS:
            folder=self.output/"runs"/mode
            folder.mkdir(parents=True)
            result=folder/"Gravity_Result_V110.json"
            result.write_text(json.dumps(self.payload(mode)),encoding="utf-8")
            register_case(self.output,result,self.model,scenario=mode,
                          profile="GRAVITY_1.0D_1.0L")
            paths.append(result)
        index=json.loads((self.output/"00_INDEXES"/"Gravity_Case_Reaction_Index.json").read_text())
        self.assertEqual(len(index),3)
        text=(self.output/"00_INDEXES"/"Gravity_Output_Index.txt").read_text(encoding="utf-8")
        for mode, result in zip(SCENARIO_SUPPORTS,paths):
            self.assertIn(str(result.resolve()),text)
            self.assertEqual(current_case(self.output,self.model,scenario=mode,
                profile="GRAVITY_1.0D_1.0L")["result_path"],str(result.resolve()))
        self.assertIn("not ETABS validation",text)

    def test_compensating_node_reaction_tamper_invalidates_registered_result(self):
        mode="ETABS_NONZERO_REACTION_DIAGNOSTIC"
        payload=self.payload(mode)
        f=self.write(payload)
        record=register_case(self.output,f,self.model,scenario=mode,
                             profile="GRAVITY_1.0D_1.0L")
        self.assertEqual(len(record["result_sha256"]),64)
        self.assertIsNotNone(current_case(self.output,self.model,scenario=mode,
                                          profile="GRAVITY_1.0D_1.0L"))
        # Equal total and unchanged support count/report must NOT make a
        # changed distribution look like the registered solver result.
        payload["reactions"][0]["rz_kN"]+=400.0
        payload["reactions"][1]["rz_kN"]-=400.0
        f.write_text(json.dumps(payload),encoding="utf-8")
        self.assertIsNone(current_case(self.output,self.model,scenario=mode,
                                       profile="GRAVITY_1.0D_1.0L"))

    def test_legacy_entry_without_result_sha_requires_reregistration(self):
        mode="ETABS_SOURCE_SUPPORTS"
        f=self.write(self.payload(mode))
        register_case(self.output,f,self.model,scenario=mode,
                      profile="GRAVITY_1.0D_1.0L")
        index=self.output/"00_INDEXES"/"Gravity_Case_Reaction_Index.json"
        records=json.loads(index.read_text(encoding="utf-8"))
        records[mode+"|GRAVITY_1.0D_1.0L"].pop("result_sha256")
        index.write_text(json.dumps(records),encoding="utf-8")
        self.assertIsNone(current_case(self.output,self.model,scenario=mode,
                                       profile="GRAVITY_1.0D_1.0L"))
        register_case(self.output,f,self.model,scenario=mode,
                      profile="GRAVITY_1.0D_1.0L")
        self.assertIsNotNone(current_case(self.output,self.model,scenario=mode,
                                          profile="GRAVITY_1.0D_1.0L"))

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
