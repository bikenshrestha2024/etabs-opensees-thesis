"""Native-independent completion-contract checks for the ETABS conversion worker."""
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

from tools.etabs_conversion_worker import _report_signature, validate_converter_report


class TestWorkerReport(unittest.TestCase):
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
