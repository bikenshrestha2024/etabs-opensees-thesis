"""Verify both GUI stages expose the same guarded on-demand gravity Excel action."""
from __future__ import annotations

import ast
from pathlib import Path
import unittest


class GravityExcelActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(Path(__file__).resolve().parents[1] /
                    "components/ui/application.py").read_text(encoding="utf-8")
        cls.tree=ast.parse(cls.source)

    def test_import_and_gravity_stage_share_one_callback(self):
        pairs=[]
        for node in ast.walk(self.tree):
            if not (isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                    and node.func.id=="action"):
                continue
            options={k.arg:k.value for k in node.keywords}
            title=options.get("text")
            callback=options.get("command")
            if (isinstance(title,ast.Constant) and
                    "gravity" in str(title.value).lower() and
                    "excel" in str(title.value).lower() and
                    isinstance(callback,ast.Attribute) and
                    callback.attr=="_generate_storey_gravity_excel"):
                stage=(node.args[0].id if node.args and isinstance(node.args[0],ast.Name)
                       else "")
                pairs.append(stage)
        self.assertIn("group_0_1",pairs)
        self.assertIn("group_2_0",pairs)
        self.assertEqual(len(pairs),2)

    def test_generator_checks_active_conversion_and_uses_saved_export(self):
        cls=next(n for n in self.tree.body
                 if isinstance(n,ast.ClassDef) and n.name=="App")
        method=next(n for n in cls.body
                    if isinstance(n,ast.FunctionDef)
                    and n.name=="_generate_storey_gravity_excel")
        text=ast.get_source_segment(self.source,method)
        self.assertIn("_conversion_process",text)
        self.assertIn("_storey_gravity_excel_running",text)
        self.assertIn("OpenSees_Complete_Model_Data_V118.json",text)
        self.assertIn("OpenSees_Complete_Export_Report_V118.json",text)
        self.assertIn("components.gravity.storey_loads",text)
        self.assertNotIn("prepare_complete_export(",text)
        self.assertNotIn("convert_model(",text)


if __name__=="__main__":
    unittest.main()
