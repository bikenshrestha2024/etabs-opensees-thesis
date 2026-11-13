"""Module 01 import review regression: no ETABS, no native OpenSees."""
import ast
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[1]

class ImportOneTests(unittest.TestCase):
    def test_locked_excel_uses_unique_sibling_and_returns_actual_path(self):
        p=ROOT/"components/sections/mapping_audit.py"
        source=p.read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn("except PermissionError as exc:",source)
        self.assertIn("_OPEN_WORKBOOK_",source)
        self.assertIn("wb.save(alternate)",source)
        self.assertIn("path=alternate",source)
        self.assertIn("return path",source)

    def test_workflow_detects_nested_result_but_does_not_claim_pass(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location(
            "standalone_workflow",ROOT/"OpenSees_Workflow_V144.py")
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            run=root/"OpenSees_Analysis_Results"/"ULS_25F"/"Modal_ULS"
            run.mkdir(parents=True)
            (run/"NBC105_Modal_V111.json").write_text(
                json.dumps({"status":"failed"}),encoding="utf-8")
            records=module.workflow_status(root)
            self.assertEqual(len(records),9)
            self.assertIn("CANDIDATE",records[3][0])
            self.assertIn("NOT checked",records[3][1])
            self.assertIn("NO FILE",records[5][0])
            self.assertIn("absence does not prove",records[5][1])
            self.assertIn("01_MAIN_GUI.py",str(module.STEPS))
            self.assertIn("16_NONLINEAR_REVIEWED_MODEL.py",str(module.STEPS))

if __name__=="__main__":
    unittest.main()
