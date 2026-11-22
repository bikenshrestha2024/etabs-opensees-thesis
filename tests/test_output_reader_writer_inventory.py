"""Every active output reader must be inventoried alongside the writer.

Static evidence only. Native ETABS/OpenSees and actual saved-case reopen
remain separate, mandatory engineering gates. [REF docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md]
"""
import tempfile
import unittest
from pathlib import Path

from tools.audit_live_output_writers import scan_source


class OutputReaderWriterInventoryTests(unittest.TestCase):
    def test_reader_and_writer_are_both_recorded_in_same_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            p=root/"components"/"gravity"/"sample.py"
            p.parent.mkdir(parents=True)
            p.write_text('''from pathlib import Path
def saved_case(p):
    data=Path(p).read_text(encoding="utf-8")
    return data
def write_case(p):
    Path(p).write_text("sample",encoding="utf-8")
''',encoding="utf-8")
            report=scan_source(root)
            self.assertEqual(report["parse_errors"],[])
            self.assertEqual(report["totals"]["possible_read_calls"],1)
            self.assertEqual(report["totals"]["possible_write_calls"],1)
            item=report["reader_writer_files"][0]
            self.assertEqual(item["source"],"components/gravity/sample.py")
            self.assertEqual(item["read_calls"],1)
            self.assertEqual(item["write_calls"],1)

    def test_open_read_and_write_modes_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            p=root/"unit.py"
            p.write_text('''def f(p):
    with open(p,"r",encoding="utf-8") as stream:
        stream.read()
    with open(p,"w",encoding="utf-8") as stream:
        stream.write("v")
''',encoding="utf-8")
            report=scan_source(root)
            self.assertGreaterEqual(report["totals"]["possible_read_calls"],1)
            self.assertGreaterEqual(report["totals"]["possible_write_calls"],1)
            records=report["files"][0]["occurrences"]
            self.assertTrue(any(x["kind"]=="POTENTIAL_READ_CALL" and
                                x.get("method")=="open" for x in records))
            self.assertTrue(any(x["kind"]=="POTENTIAL_WRITE_CALL" and
                                x.get("method")=="open" for x in records))

    def test_real_module_inventory_is_not_a_claim_of_complete_migration(self):
        root=Path(__file__).resolve().parents[1]
        result=scan_source(root)
        self.assertFalse(result["parse_errors"],result["parse_errors"])
        self.assertGreater(result["totals"]["possible_read_calls"],0)
        self.assertGreater(result["totals"]["possible_write_calls"],0)
        self.assertTrue(any(x["source"]=="components/gravity/gui_and_reports.py"
                            for x in result["reader_writer_files"]))


if __name__=="__main__":
    unittest.main()
