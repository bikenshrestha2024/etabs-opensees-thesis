"""Centralized gravity evidence packaging and exact path regression tests."""
from __future__ import annotations
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from components.gravity.evidence_workflow import (
    latest_dual_run, package_gravity_review, path_log_entries)


class GravityEvidenceWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source=self.root/"source";self.source.mkdir()
        self.script=self.source/"OpenSees_Complete_Gravity_Model.py"
        self.script.write_text("pass\n",encoding="utf8")
        self.gravity=self.root/"gravity";self.gravity.mkdir()
        self.sample={
            "ok":True,
            "model_script":str(self.script.resolve()),
            "nodes":[{"tag":1,"x_m":0.0,"y_m":0.0,"z_m":0.0,
                      "ux_m":0.0,"uy_m":0.0,"uz_m":0.0,
                      "rx_rad":0.0,"ry_rad":0.0,"rz_rad":0.0}],
            "reactions":[{"node_tag":1,"rx_kN":0.0,"ry_kN":0.0,"rz_kN":50.0}],
            "local_forces":[{"tag":101,"N_i_kN":0.0}],
            "report":{"applied_vertical_load_kN":50.0}}
        (self.gravity/"Gravity_Result_V110.json").write_text(
            json.dumps(self.sample),encoding="utf8")
        (self.gravity/"Gravity_Run_V110.log").write_text(
            "PASS: gravity equilibrium",encoding="utf8")
        (self.gravity/"Gravity_GUI_Actions.log").write_text(
            "GRAVITY_START",encoding="utf8")
        (self.gravity/"Gravity_Results_V110.xlsx").write_bytes(b"example")
        (self.gravity/"Gravity_Load_Plots.pdf").write_bytes(b"example PDF")
        (self.source/"OpenSees_Complete_Model_Config_V118.json").write_text("{}")
        (self.source/"OpenSees_Element_Connectivity.json").write_text("{}")
    def test_primary_workbook_screen_rechecks_native_rows(self):
        from hashlib import sha256
        from components.gravity.etabs_reaction_support_filter import (
            MODE, PROFILE, PROJECT_PRIMARY_32, matched_primary_32_workbook_comparison,
        )
        workbook = self.root/'original.csv'
        workbook.write_text('Story,Label,Unique Name,Output Case,FZ\n'+''.join(
            f'Base,J{tag},{tag},{PROFILE},10\n' for tag in PROJECT_PRIMARY_32), encoding='utf-8')
        fingerprint = sha256(workbook.read_bytes()).hexdigest()
        audit = dict(case=PROFILE, user_confirmed_32_exact_match=True,
                     source_table=str(workbook), source_sha256=fingerprint,
                     mapping=[dict(opensees_node=tag, etabs_unique=str(tag), selected=True,
                                   etabs_FZ_kN=10.) for tag in PROJECT_PRIMARY_32])
        evidence = dict(original_ETABS_case=PROFILE, original_etabs_table_sha256=fingerprint,
                        node_reactions=[dict(opensees_node=tag, etabs_unique_name=str(tag),
                                         etabs_FZ_kN=10., opensees_FZ_kN=20.) for tag in PROJECT_PRIMARY_32])
        result = dict(wall_support_strategy=MODE, gravity_profile='GRAVITY_1.0D_1.0L',
                      support_node_tags=PROJECT_PRIMARY_32,
                      reactions=[dict(node_tag=tag, rz_kN=20.) for tag in PROJECT_PRIMARY_32])
        audit_path=self.gravity/'ETABS_Nonzero_Reaction_Support_Audit.json'
        evidence_path=self.gravity/'Primary_32_ETABS_OpenSees_Reactions.json'
        audit_path.write_text(json.dumps(audit),encoding='utf-8')
        evidence_path.write_text(json.dumps(evidence),encoding='utf-8')
        matched = matched_primary_32_workbook_comparison(self.gravity,result)
        self.assertEqual(matched['etabs_base_FZ_kN'], 320.)
        audit['mapping'][0]['etabs_FZ_kN']=5.
        evidence['node_reactions'][0]['etabs_FZ_kN']=5.
        audit_path.write_text(json.dumps(audit),encoding='utf-8')
        evidence_path.write_text(json.dumps(evidence),encoding='utf-8')
        self.assertIsNone(matched_primary_32_workbook_comparison(self.gravity,result))

    def _dual(self):
        base=self.gravity/"Gravity_Wall_Base_Comparison"/"20261108_111122"
        for mode in ("ETABS_SOURCE_SUPPORTS","CONTINUOUS_WALL_BASE_FIXED"):
            case=base/mode
            case.mkdir(parents=True)
            (case/"Gravity_Result_V110.json").write_text(json.dumps({
                **self.sample,"wall_support_strategy":mode,
                "gravity_profile":"GRAVITY_1.0D_1.0L"}))
            (case/"Gravity_Run_V110.log").write_text(mode)
            (case/"Gravity_Results_V110.xlsx").write_bytes(b"workbook")
        (base/"Gravity_Wall_Base_Strategy_Comparison.json").write_text("{}")
        (base/"Gravity_Wall_Base_Strategy_Comparison.xlsx").write_bytes(b"xlsx")
        (base/"Gravity_Wall_Base_Nodal_Reaction_Differences.csv").write_text("node_tag\n1\n")
        offline=base/"ETABS_Full_Table_Offline_Comparison"
        offline.mkdir()
        (offline/"comparison.csv").write_text("node_tag,difference_kN\n1,0\n")
        return base
    def test_single_run_creates_upload_zip_and_full_paths_manifest(self):
        report,paths=package_gravity_review(self.script,self.gravity,
                                            single_run=self.gravity)
        self.assertTrue(Path(paths["upload_zip"]).is_file())
        self.assertEqual(Path(paths["upload_zip"]).parent,
                         self.gravity/"07_EXPORT_ZIP"/"Gravity_Evidence_Upload")
        manifest=Path(paths["evidence_manifest"])
        self.assertTrue(manifest.is_relative_to(self.gravity/"06_REVIEW"/"Gravity_Evidence"))
        self.assertEqual(json.loads(manifest.read_text())['output_zip'], paths['upload_zip'])
        index=Path(paths["exact_file_paths"])
        pointer=Path(paths["latest_upload_pointer"])
        self.assertTrue(pointer.is_file())
        self.assertIn(paths["upload_zip"],pointer.read_text())
        self.assertIn(paths["exact_file_paths"],pointer.read_text())
        self.assertTrue(manifest.is_file())
        self.assertTrue(index.is_file())
        self.assertIn(str(self.gravity.resolve()),index.read_text())
        self.assertIn(str(self.source.resolve()),index.read_text())
        with zipfile.ZipFile(paths["upload_zip"]) as f:
            names=f.namelist()
            self.assertTrue(any(x.endswith("Gravity_GUI_Actions.log") for x in names))
            self.assertTrue(any(x.endswith("Gravity_Results_V110.xlsx") for x in names))
            self.assertTrue(any(x.endswith("Gravity_Load_Plots.pdf") for x in names))
            self.assertTrue(any(x.endswith("EVIDENCE_FILE_PATHS.txt") for x in names))
        labels=[stage for stage,msg in path_log_entries(paths,report)]
        self.assertIn("EVIDENCE_UPLOAD_ZIP",labels)
        self.assertIn("EVIDENCE_EVIDENCE_MANIFEST",labels)

    def test_dual_run_and_offline_results_are_in_same_zip(self):
        dual=self._dual()
        report,paths=package_gravity_review(self.script,self.gravity,
              dual_run=dual,single_run=dual/"ETABS_SOURCE_SUPPORTS")
        self.assertEqual(latest_dual_run(self.gravity),dual)
        self.assertEqual(Path(report["dual_run_dir"]),dual)
        with zipfile.ZipFile(paths["upload_zip"]) as f:
            names=f.namelist()
            for tail in (
                "wall_base_comparison/ETABS_SOURCE_SUPPORTS/Gravity_Result_V110.json",
                "wall_base_comparison/CONTINUOUS_WALL_BASE_FIXED/Gravity_Result_V110.json",
                "wall_base_comparison/Gravity_Wall_Base_Strategy_Comparison.xlsx",
                "offline_etabs/comparison.csv",
                "gravity_workflow/Gravity_GUI_Actions.log",
                "single_run_root/Gravity_Result_V110.json",
            ):
                self.assertTrue(any(x.endswith(tail) for x in names),tail)

    def test_explicit_dual_wrong_support_or_other_model_fails_closed(self):
        dual=self._dual()
        first=dual/"ETABS_SOURCE_SUPPORTS"/"Gravity_Result_V110.json"
        doc=json.loads(first.read_text())
        doc["wall_support_strategy"]="CONTINUOUS_WALL_BASE_FIXED"
        first.write_text(json.dumps(doc),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"support strategy"):
            package_gravity_review(self.script,self.gravity,dual_run=dual,
                single_run=self.gravity)
        doc["wall_support_strategy"]="ETABS_SOURCE_SUPPORTS"
        doc["model_script"]=str(self.root/"wrong_builder.py")
        first.write_text(json.dumps(doc),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"different or unknown"):
            package_gravity_review(self.script,self.gravity,dual_run=dual,
                single_run=self.gravity)

    def test_different_model_run_is_not_automatically_packaged(self):
        alien=self.gravity/"02_RESULTS"/"ETABS_SOURCE_SUPPORTS"/"GRAVITY_1.0D_1.0L"/"alien"
        alien.mkdir(parents=True)
        wrong={**self.sample,"model_script":str(self.root/"another_model.py")}
        (alien/"Gravity_Result_V110.json").write_text(
            json.dumps(wrong),encoding="utf-8")
        single=__import__("components.gravity.evidence_workflow",
            fromlist=["latest_single_run"]).latest_single_run(
                self.gravity,model_script=self.script)
        self.assertEqual(single,self.gravity)

    def test_canonical_support_cases_and_upload_owner(self):
        from components.gravity.output_ownership import case_directory,dual_runs_parent
        timestamp = 1_700_000_000
        os.utime(self.gravity/"Gravity_Result_V110.json", (timestamp,timestamp))
        for scenario in ("ETABS_NONZERO_REACTION_DIAGNOSTIC",
                         "ETABS_SOURCE_SUPPORTS",
                         "CONTINUOUS_WALL_BASE_FIXED"):
            case=case_directory(self.gravity,scenario,"GRAVITY_1.0D_1.0L",
                                "20261121T000000_123456",create=True)
            (case/"Gravity_Result_V110.json").write_text(
                json.dumps({**self.sample,
                            "wall_support_strategy":scenario,
                            "gravity_profile":"GRAVITY_1.0D_1.0L",
                            "model_script":str(self.script),
                            "ok":True}),encoding="utf-8")
            os.utime(case/"Gravity_Result_V110.json", (timestamp,timestamp))
            (case/"Gravity_Run_V110.log").write_text("ok",encoding="utf-8")
        latest=__import__(
            "components.gravity.evidence_workflow",
            fromlist=["latest_single_run"]).latest_single_run(
                self.gravity,model_script=self.script)
        self.assertTrue(latest.is_relative_to(self.gravity/"02_RESULTS"))
        report,paths=package_gravity_review(self.script,self.gravity,single_run=latest)
        self.assertTrue(Path(paths["upload_zip"]).is_relative_to(
            self.gravity/"07_EXPORT_ZIP"/"Gravity_Evidence_Upload"))
        self.assertTrue(Path(paths["latest_upload_pointer"]).is_relative_to(
            self.gravity/"00_INDEXES"))
        self.assertTrue(dual_runs_parent(self.gravity).is_relative_to(
            self.gravity/"05_COMPARISONS"))

    def test_timestamped_32_node_run_is_discovered_and_packaged(self):
        import os
        diagnostic=self.gravity/"Gravity_Reaction_Diagnostic"/"20261109_094206_701648"
        diagnostic.mkdir(parents=True)
        (diagnostic/"Gravity_Result_V110.json").write_text(
            json.dumps(self.sample),encoding="utf8")
        (diagnostic/"Gravity_Run_V110.log").write_text("solver PASS",encoding="utf8")
        # Ensure newer timestamped run wins over a legacy root result.
        os.utime(self.gravity/"Gravity_Result_V110.json",(946684800,946684800))  # 2000-01-01; ZIP-safe
        report,paths=package_gravity_review(self.script,self.gravity)
        self.assertEqual(Path(paths["selected_gravity_run"]),diagnostic)
        with zipfile.ZipFile(paths["upload_zip"]) as z:
            self.assertTrue(any(x.endswith("single_run_root/Gravity_Result_V110.json")
                                for x in z.namelist()))

    def test_missing_root_result_does_not_hide_saved_diagnostic(self):
        (self.gravity/"Gravity_Result_V110.json").unlink()
        diagnostic=self.gravity/"Gravity_Reaction_Diagnostic"/"20261109_094206_701648"
        diagnostic.mkdir(parents=True)
        (diagnostic/"Gravity_Result_V110.json").write_text(
            json.dumps(self.sample),encoding="utf8")
        _,paths=package_gravity_review(self.script,self.gravity)
        self.assertEqual(Path(paths["selected_gravity_run"]),diagnostic)

    def test_failed_diagnostic_is_not_relabelled_success(self):
        (self.gravity/"Gravity_Result_V110.json").unlink()
        diagnostic=self.gravity/"Gravity_Reaction_Diagnostic"/"failed"
        diagnostic.mkdir(parents=True)
        (diagnostic/"Gravity_Result_V110.json").write_text(
            json.dumps({"ok":False}),encoding="utf8")
        with self.assertRaisesRegex(FileNotFoundError,"No completed gravity"):
            package_gravity_review(self.script,self.gravity)

    def test_explicit_missing_run_does_not_fallback_to_other_case(self):
        with self.assertRaisesRegex(FileNotFoundError,"Required OpenSees"):
            package_gravity_review(self.script,self.gravity,
                single_run=self.gravity/"different_case")


    def test_run_versions_are_immutable_and_failed_inputs_not_fabricated(self):
        _,a=package_gravity_review(self.script,self.gravity,
                                   single_run=self.gravity)
        _,b=package_gravity_review(self.script,self.gravity,
                                   single_run=self.gravity)
        self.assertNotEqual(a["upload_zip"],b["upload_zip"])
        self.assertTrue(Path(a["upload_zip"]).exists())
        self.assertTrue(Path(b["upload_zip"]).exists())
        with self.assertRaisesRegex(FileNotFoundError,"Required OpenSees"):
            package_gravity_review(self.script,self.gravity,
                single_run=self.root/"unavailable")


if __name__=="__main__":
    unittest.main()
