"""V130 timing evidence must be organized, not root-level JSON clutter."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from components.shared.timing import timed_outputs, StageTimer


class TimingMetadataLayoutTests(unittest.TestCase):
    def test_stage_directory_has_no_new_root_sidecar(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            @timed_outputs("elastic export","output")
            def export(output):
                child=Path(output)/"nested"/"run.csv"
                child.parent.mkdir(exist_ok=True)
                child.write_text("n,kN\\n1,2\\n",encoding="utf-8")
            export(root)
            self.assertFalse((root/"nested"/"run.csv.processing.json").exists())
            sidecar=root/"00_PROCESSING_METADATA"/"ARTIFACTS"/"nested"/"run.csv.processing.json"
            self.assertTrue(sidecar.is_file())
            meta=json.loads(sidecar.read_text(encoding="utf-8"))
            self.assertEqual(meta["stage"],"elastic export")
            self.assertEqual(meta["artifact"],"nested/run.csv")
            self.assertEqual(meta["status"],"completed")
            self.assertTrue((root/"00_PROCESSING_METADATA"/"OUTPUT_TIMING_INDEX_V130.json").is_file())
            self.assertEqual(len(list(root.rglob("*.processing.json"))),1)
            export(root)
            self.assertEqual(len(list(root.rglob("*.processing.json"))),1)

    def test_failure_retains_original_file_and_flag(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            @timed_outputs("gravity failed","output")
            def fail(output):
                (Path(output)/"partial.json").write_text("{}")
                raise RuntimeError("synthetic")
            with self.assertRaises(RuntimeError):
                fail(root)
            status=json.loads((root/"00_PROCESSING_METADATA"/"ARTIFACTS"/
                               "partial.json.processing.json").read_text())
            self.assertEqual(status["status"],"failed")
            self.assertEqual((root/"partial.json").read_text(),"{}")

    def test_explicit_stage_timer_uses_same_metadata_subfolder(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"untouched.csv").write_text("previous")
            timer=StageTimer(root,"modal")
            (root/"frequencies.csv").write_text("frequency\\n3.6\\n")
            with patch("components.shared.timing.time.time", return_value=10**10):
                timer.finish("solver-only")
            self.assertFalse((root/"00_PROCESSING_METADATA"/"ARTIFACTS"/
                              "untouched.csv.processing.json").exists())
            self.assertTrue((root/"00_PROCESSING_METADATA"/"ARTIFACTS"/
                             "frequencies.csv.processing.json").is_file())
            self.assertFalse((root/"frequencies.csv.processing.json").exists())


if __name__=="__main__":
    unittest.main()
