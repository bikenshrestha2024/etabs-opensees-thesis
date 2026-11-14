"""Pure-path stage-layout consistency; no ETABS/OpenSees executable required."""
import tempfile
import json
import unittest
from pathlib import Path
from components.inputs.output_layout import export_root_for, review_snapshots_for, STAGE_FOLDERS, write_stage_index


class OutputLayoutTests(unittest.TestCase):
    def test_all_stages_use_one_selected_export(self):
        with tempfile.TemporaryDirectory() as td:
            selected = Path(td) / "ETABS 11-14-2026" / "2"
            legacy = selected / "OpenSees_Analysis_Results" / "ULS_Third_Floor_Model"
            for stage, folder in STAGE_FOLDERS.items():
                self.assertEqual(
                    review_snapshots_for(legacy, stage),
                    selected / folder / "REVIEW_SNAPSHOTS"
                )

    def test_legacy_or_canonical_input_same_target(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "export"
            legacy = root / "OpenSees_Analysis_Results" / "ULS" / "case_1"
            existing = root / "03_ESM" / "REVIEW_SNAPSHOTS" / "old_run"
            self.assertEqual(export_root_for(legacy), root)
            self.assertEqual(export_root_for(existing), root)
            self.assertEqual(review_snapshots_for(existing, "ESM"),
                             root / "03_ESM" / "REVIEW_SNAPSHOTS")
            self.assertEqual(review_snapshots_for(root, "ESM"),
                             root / "03_ESM" / "REVIEW_SNAPSHOTS")
            self.assertFalse(root.exists())

    def test_stage_index_preserves_private_inputs_and_does_not_infer_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "case_2"
            root.mkdir()
            (root / "source.EDB").write_bytes(b"original model")
            (root / "01_ETABS_EXPORT").mkdir()
            (root / "02_GRAVITY" / "REVIEW_SNAPSHOTS" / "run_a").mkdir(parents=True)
            (root / "03_ESM" / "REVIEW_SNAPSHOTS" / "run_b").mkdir(parents=True)
            (root / "OpenSees_Analysis_Results").mkdir()
            index_path = write_stage_index(root)
            idx = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(idx["schema"], "THESIS_STAGE_INDEX_V1")
            self.assertTrue(idx["legacy_analysis_results_present"])
            self.assertEqual({x["stage"] for x in idx["stages"]}, set(STAGE_FOLDERS))
            stages = {x["stage"]: x for x in idx["stages"]}
            self.assertEqual(stages["GRAVITY"]["review_snapshot_count"], 1)
            self.assertEqual(stages["ESM"]["latest_review_folder"],
                             "03_ESM/REVIEW_SNAPSHOTS/run_b")
            self.assertEqual(stages["ESM"]["engineering_status"],
                             "NOT_ASSESSED_BY_FILE_INDEX")
            self.assertFalse(stages["NLTHA"]["present"])
            self.assertEqual((root / "source.EDB").read_bytes(), b"original model")
            self.assertNotIn("original model", index_path.read_text())

    def test_unknown_stage_fails_closed(self):
        with self.assertRaises(ValueError):
            review_snapshots_for("D:/thesis/export", "gravity2")


if __name__ == "__main__":
    unittest.main()
