"""ESM paths must remain under the single source export's 03_ESM owner.

Tests are temporary-file source only. Never copy or read user EDB/Excel.
[REF docs/source/components/equivalent_static/calculation_and_gui.py.md]
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.equivalent_static.organized_exports import (
    esm_batch_status_root, _latest_batch_status)
from components.inputs.project_workbooks import (
    analysis_output_folder, esm_case_output_directory)

RUNNER="OpenSees_Direct_NBC105_ESM_Load_And_Static_Analysis_ULS_X+_E0_V111.py"


class ESMOneOutputOwnerTests(unittest.TestCase):
    def test_case_selection_never_writes_into_another_export_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            export=Path(tmp)/"export"
            export.mkdir()
            expected=analysis_output_folder(export,"ULS",stage="ESM")
            selections=(export, export/"02_MODEL"/"AREA_INTEGRATION",
                        export/"OpenSees_Analysis_Results"/"old",
                        export/"03_ESM", export/"03_ESM"/"RUNS",
                        export/"03_ESM"/"RUNS"/"SLS"/"another",
                        expected)
            for selected in selections:
                with self.subTest(selected=str(selected)):
                    self.assertEqual(esm_case_output_directory(export,"ULS",selected),expected)
            self.assertFalse(expected.exists())

    def test_external_override_is_explicit_and_unmodified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            export=root/"export"
            external=root/"custom"
            export.mkdir()
            self.assertEqual(esm_case_output_directory(export,"ULS",external),external.resolve())
            self.assertEqual(esm_batch_status_root(export,external),external.resolve()/"ESM_Runner_Status")
            self.assertFalse(external.exists())

    def test_batch_status_is_canonical_and_idempotent_for_all_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            export=Path(tmp)/"export"
            export.mkdir()
            expected=export/"03_ESM"/"LOGS_AND_STATUS"/"ESM_Runner_Status"
            for selected in (export, export/"03_ESM",export/"02_MODEL",
                             analysis_output_folder(export,"ULS",stage="ESM"),
                             analysis_output_folder(export,"SLS",stage="ESM")):
                self.assertEqual(esm_batch_status_root(export,selected),expected)
            self.assertFalse(expected.exists())

    def test_export_reader_finds_canonical_status_and_keeps_legacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            selected=analysis_output_folder(root,"ULS",stage="ESM")
            selected.mkdir(parents=True)
            runner=selected/RUNNER
            runner.write_text("# synthetic runner\n",encoding="utf-8")
            status=esm_batch_status_root(root,selected)/"20261123_100000"/"CASE_STATUS.json"
            status.parent.mkdir(parents=True)
            status.write_text(json.dumps([{
                "case":RUNNER,"runner_path":str(runner),
                "runner_sha256":hashlib.sha256(runner.read_bytes()).hexdigest(),
                "status":"SUCCESS","return_code":0
            }]),encoding="utf-8")
            found=_latest_batch_status(selected)
            self.assertEqual(found["status"],"COMPLETE_SOLVER_ONLY")
            self.assertEqual(Path(found["status_file"]),status)
            # A second unexecuted case cannot be covered by the first status.
            (selected/RUNNER.replace("X+","Y+")).write_text("# unsolved\n")
            incomplete=_latest_batch_status(selected)
            self.assertEqual(incomplete["status"],"PARTIAL_OR_FAILED")

    def test_gui_writes_only_resolved_case_and_status_destinations(self):
        import inspect
        from components.equivalent_static.calculation_and_gui import ESMGui
        source=inspect.getsource(ESMGui)
        self.assertIn("esm_case_output_directory(self.export_dir,state,",source)
        self.assertIn("esm_batch_status_root(self.export_dir, output)",source)


if __name__=="__main__":
    unittest.main()
