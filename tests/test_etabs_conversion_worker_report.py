"""Native-independent completion-contract checks for the ETABS conversion worker."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import ModuleType
import unittest
from unittest import mock

from tools.etabs_conversion_worker import _report_signature, run, validate_converter_report


class TestWorkerReport(unittest.TestCase):
    def test_categorizing_keeps_the_active_log_and_reports_mirror_conflicts(self):
        def fake_conversion(_edb, output, _log, _live):
            folder = Path(output)
            (folder / "OpenSees_Complete_Export_Report_V118.json").write_text(
                '{"assembly_errors": []}', encoding="utf-8")
            (folder / "ETABS_OpenSees_Conversion_Log.txt").write_text("active", encoding="utf-8")

        application = ModuleType("components.ui.application")
        application.convert_model = fake_conversion
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.dict(sys.modules, {application.__name__: application}),
            mock.patch("components.inputs.project_output_layout.create_project_layout",
                       return_value={"source_edb_sha256": "synthetic", "output_root": tmp}),
            mock.patch("components.inputs.lfs_workbook_recovery.audit_optional_gui_workbooks",
                       return_value={}),
            mock.patch("components.inputs.output_layout.write_stage_index"),
        ):
            result = run(Path(tmp) / "source.EDB", Path(tmp), False, True)
            mirror = result["categorized_mirror"]
            self.assertEqual(mirror["status"], "completed")
            manifest = json.loads(Path(mirror["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["excluded_live_logs"]), 1)
            self.assertEqual(len(manifest["files"]), 1)

            with (
                mock.patch("components.inputs.export_mirror.export_mirror",
                           side_effect=ValueError("existing categorized copy differs")),
                mock.patch("tools.etabs_conversion_worker._report_signature",
                           side_effect=[(1, 1), (2, 1)]),
            ):
                result = run(Path(tmp) / "source.EDB", Path(tmp), False, True)
            self.assertEqual(result["categorized_mirror"]["status"], "needs_review")
            self.assertEqual(result["model_equivalence"], "NOT_VERIFIED")

    def test_missing_report_never_counts_as_complete(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(RuntimeError, "fresh"):
                validate_converter_report(Path(td) / "report.json")

    def test_existing_unchanged_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"report.json"
            p.write_text(json.dumps({"assembly_errors":[]}))
            before=_report_signature(p)
            with self.assertRaisesRegex(RuntimeError, "old report"):
                validate_converter_report(p, old_signature=before)

    def test_failed_assembly_is_rejected_even_with_new_report(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"report.json"
            p.write_text(json.dumps({"assembly_errors":["No source shell material"]}))
            with self.assertRaisesRegex(RuntimeError, "assembly error count: 1"):
                validate_converter_report(p)

    def test_missing_or_malformed_error_status_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"report.json"
            for data in ({"warnings":[]}, {"assembly_errors":"none"},
                         {"assembly_errors":None}):
                p.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, "assembly_errors list"):
                    validate_converter_report(p)

    def test_fresh_completed_assembly_is_reported_but_not_engineering_approved(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"report.json"
            p.write_text(json.dumps({
                "assembly_errors":[],
                "analysis_ready":False,
                "nonlinear_ready":False
            }))
            data=validate_converter_report(p)
            self.assertEqual(data["assembly_errors"],[])
            self.assertFalse(data["analysis_ready"])

    def test_new_report_overwrites_old_with_fresh_signature(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"report.json"
            p.write_text(json.dumps({"assembly_errors":["old"]}))
            previous=_report_signature(p)
            p.write_text(json.dumps({"assembly_errors":[],"revision":"new"}))
            # Explicitly make mtime unique, independent of host timestamp granularity.
            stat=p.stat()
            os.utime(p,ns=(stat.st_atime_ns,stat.st_mtime_ns+1_000_000))
            self.assertEqual(validate_converter_report(p,old_signature=previous)["revision"],"new")


if __name__=="__main__":
    unittest.main(verbosity=2)
