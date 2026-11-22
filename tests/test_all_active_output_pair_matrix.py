"""Fail-safe whole-active-tree output producer/consumer matrix tests.

[REF docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md]
"""
import tempfile
import unittest
from pathlib import Path

from tools.audit_output_writer_reader_pairs import build_matrix


class AllActiveOutputPairMatrixTests(unittest.TestCase):
    def test_every_file_is_included_even_when_no_direct_io(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            model=root/"components"/"gravity"
            model.mkdir(parents=True)
            (model/"export.py").write_text('''from pathlib import Path
def write(p):
    return Path(p).write_text("x")
''',encoding="utf-8")
            (model/"reader.py").write_text('''from pathlib import Path
def read(p):
    return Path(p).read_text()
''',encoding="utf-8")
            (root/"no_io.py").write_text("VALUE=1\n",encoding="utf-8")
            report=build_matrix(root)
            self.assertEqual(report["source_count"],3)
            self.assertEqual(report["owner_counts"]["GRAVITY"],2)
            rows={x["source"]:x for x in report["sources"]}
            self.assertEqual(rows["components/gravity/export.py"]
                             ["possible_write_calls"],1)
            self.assertEqual(rows["components/gravity/reader.py"]
                             ["possible_read_calls"],1)
            self.assertEqual(rows["no_io.py"]["review_status"],
                             "NO_DIRECT_IO_CALL_FOUND_STATIC_ONLY")
            self.assertEqual(report["acceptance"],
                             "OPEN_UNTIL_WRITER_READER_NATIVE_SAVED_CASE_PARITY")
            self.assertFalse(report["historical_results_mutated"])

    def test_syntax_error_is_retained_as_blocker_not_dropped(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"bad.py").write_text("def broken(\n",encoding="utf-8")
            report=build_matrix(root)
            self.assertEqual(report["source_count"],1)
            self.assertTrue(report["parse_errors"])

    def test_current_research_modules_are_inventory_scoped(self):
        report=build_matrix(Path(__file__).resolve().parents[1])
        owners=set(report["owner_counts"])
        self.assertTrue({"GRAVITY","ESM","MODAL","MRSM",
                         "LTHA","NLTHA","UI","MODEL","NBC105"} <= owners)
        self.assertGreater(report["producer_consumer_review_required"],0)
        self.assertEqual(report["source_count"],sum(report["owner_counts"].values()))


if __name__=="__main__":
    unittest.main()
