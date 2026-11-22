"""Cross-stage output-path ownership regression without ETABS/OpenSees runtime."""
import tempfile
import unittest
from pathlib import Path

from components.inputs.output_contract import create_case_run
from tools.audit_uniform_output_structure import audit_export_layout


class UniformOutputStructureTests(unittest.TestCase):
    def test_every_active_stage_uses_same_run_folder_contract(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"export";root.mkdir()
            for stage in ("ETABS_EXPORT","GRAVITY","ESM","MODAL","MRSM","LTHA","NLTHA"):
                run=create_case_run(root,stage,"TEST_CASE",state="ULS",
                                    units="kN-m-s")
                self.assertEqual(run.parent.parent.parent.name,"RUNS")
                self.assertTrue((run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").is_file())
                self.assertTrue((run/"02_RESULTS").is_dir())
            report=audit_export_layout(root)
            self.assertFalse(report["issues"],report["issues"])
            for name in ("ETABS_EXPORT","GRAVITY","ESM","MODAL","MRSM","LTHA","NLTHA"):
                self.assertEqual(report["case_counts"][name],1)

    def test_missing_or_corrupted_manifest_is_flagged_without_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run=create_case_run(root,"GRAVITY","REVIEW",
                                             state="ULS",units="kN-m-s")
            manifest=run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            original=manifest.read_bytes()
            self.assertFalse(audit_export_layout(root)["issues"])
            manifest.unlink()
            report=audit_export_layout(root)
            self.assertTrue(report["issues"])
            self.assertFalse(manifest.exists())
            manifest.write_bytes(original)
            self.assertFalse(audit_export_layout(root)["issues"])

    def test_unclassified_root_artifacts_reported_without_migration(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            artifact=root/"old_scaling_output.xlsx"
            artifact.write_bytes(b"private legacy workbook placeholder")
            report=audit_export_layout(root)
            self.assertEqual(len(report["loose_root_artifacts"]),1)
            self.assertEqual(report["loose_root_artifacts"][0]["relative_path"],
                             artifact.name)
            self.assertIn("ROOT_LEVEL_ARTIFACTS_NEED_OWNER_REVIEW",
                          report["review_flags"])
            self.assertEqual(artifact.read_bytes(),
                             b"private legacy workbook placeholder")
            self.assertFalse(report["issues"])

    def test_flat_stage_artifacts_are_listed_without_relocation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            folder=root/"05_MRSM";folder.mkdir()
            old=folder/"MRSM_legacy_results.json"
            old.write_text('{"legacy":true}',encoding="utf-8")
            report=audit_export_layout(root)
            row=next(x for x in report["stages"] if x["stage"]=="MRSM")
            self.assertEqual(row["loose_stage_artifacts"][0]["filename"],
                             old.name)
            self.assertEqual(old.read_text(encoding="utf-8"),
                             '{"legacy":true}')
            self.assertFalse(report["issues"])

    def test_historical_dirs_are_visible_but_never_relocated(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            legacy=root/"OpenSees_Analysis_Results"
            beam=root/"01_ETABS_EXPORT"/"03_BEAM_FORCES"
            legacy.mkdir();beam.mkdir(parents=True)
            report=audit_export_layout(root)
            by_stage={row["stage"]:row for row in report["stages"]}
            self.assertIn("OpenSees_Analysis_Results",
                          by_stage["GRAVITY"]["historical_locations"])
            self.assertIn("01_ETABS_EXPORT/03_BEAM_FORCES",
                          by_stage["ETABS_EXPORT"]["historical_locations"])
            self.assertTrue(legacy.is_dir())
            self.assertTrue(beam.is_dir())


if __name__=="__main__":
    unittest.main()
