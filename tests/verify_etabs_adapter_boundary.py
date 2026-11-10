"""Adapter isolation and canonical-implementation lookup tests."""
from __future__ import annotations
import ast
import unittest
from pathlib import Path
from src.etabs_adapter.bridge import available_existing_adapters,existing_adapter

ROOT=Path(__file__).resolve().parents[1]
class AdapterTests(unittest.TestCase):
    def test_routes_have_existing_source(self):
        refs=available_existing_adapters()
        self.assertIn("native_quantity",refs)
        self.assertIn("project_workbook",refs)
        for dotted in refs.values():
            module,name=dotted.rsplit(".",1)
            file=ROOT/Path(module.replace(".","/")+".py")
            self.assertTrue(file.is_file(),dotted)
            tree=ast.parse(file.read_text(encoding="utf-8-sig"))
            self.assertTrue(any(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))
                                and n.name==name for n in ast.walk(tree)),dotted)
    def test_malformed_route_rejected(self):
        with self.assertRaisesRegex(ValueError,"Unknown ETABS adapter"):
            existing_adapter("guess_a_new_exporter")
    def test_standalone_never_imports_etabs_adapter(self):
        for f in (ROOT/"src"/"opensees_engine").rglob("*.py"):
            tree=ast.parse(f.read_text(encoding="utf-8-sig"))
            imported=[]
            for n in ast.walk(tree):
                if isinstance(n,ast.Import):
                    imported.extend(a.name for a in n.names)
                elif isinstance(n,ast.ImportFrom):
                    imported.append(n.module or "")
            self.assertFalse([n for n in imported if "etabs_adapter" in n],
                             str(f))
if __name__=="__main__":unittest.main()
