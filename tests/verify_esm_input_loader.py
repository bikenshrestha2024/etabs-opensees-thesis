"""ESM project-input importer smoke tests independent of ETABS COM.

The GUI init invokes Tk, Excel and ETABS references. This regression checks
the exact source control flow and explicit status behavior, without starting
the GUI or claiming that an ETABS workbook is correct.
"""
import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'components'/'equivalent_static'/'calculation_and_gui.py'

class ESMImportControlFlow(unittest.TestCase):
    def test_importer_has_defined_analysis_state(self):
        module=ast.parse(SOURCE.read_text(encoding="utf-8-sig"))
        cls=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=="ESMGui")
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="_load_project_inputs")
        local_assigned={n.id for node in ast.walk(method)
                        if isinstance(node,(ast.Assign,ast.AnnAssign,ast.NamedExpr))
                        for n in ([node.target] if isinstance(node,(ast.AnnAssign,ast.NamedExpr))
                                  else node.targets)
                        if isinstance(n,ast.Name)}
        self.assertIn("selected_state",local_assigned)
        self.assertNotIn("rayleigh_state",{
            n.id for n in ast.walk(method) if isinstance(n,ast.Name) and
            isinstance(n.ctx,ast.Load)})
    def test_failed_import_has_explicit_user_feedback(self):
        source=SOURCE.read_text(encoding="utf-8-sig")
        self.assertIn("ESM input import incomplete",source)
        self.assertIn("Automatic Excel/project import failed",source)
        self.assertIn("blank values must not be",source)

if __name__=="__main__":
    unittest.main()
