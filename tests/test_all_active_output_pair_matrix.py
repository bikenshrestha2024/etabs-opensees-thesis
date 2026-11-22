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

    def test_every_legacy_line_and_reader_writer_is_exported_without_loss(self):
        import csv
        from tools.audit_output_writer_reader_pairs import main
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/"components"/"gravity"/"source.py"
            p.parent.mkdir(parents=True)
            p.write_text(
                '"""Legacy OpenSees_Analysis_Results documented only."""\n'
                'from pathlib import Path\n'
                'LEGACY = "OpenSees_Analysis_Results"\n'
                'def save(source):\n'
                '    Path(source).write_text("ok")\n'
                '    return Path(source).read_text()\n',encoding="utf-8")
            report=build_matrix(root)
            self.assertEqual(len(report["legacy_reference_lines"]),2)
            self.assertEqual(len(report["reader_writer_candidate_lines"]),2)
            self.assertEqual(
                {x["literal_context"] for x in report["legacy_reference_lines"]},
                {"DOCSTRING_REFERENCE","CODE_LITERAL_REVIEW"})
            out=root/"review"
            self.assertEqual(main(["--repo",str(root),"--report-dir",str(out)]),0)
            for name,expected in (
                ("legacy_reference_line_register.csv",2),
                ("reader_writer_line_register.csv",2)):
                with (out/name).open(encoding="utf-8-sig",newline="") as f:
                    self.assertEqual(len(list(csv.DictReader(f))),expected)
            self.assertFalse((p.parent/"02_RESULTS").exists())

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
