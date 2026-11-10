"""Only stdlib static checks; no ETABS/solver side effects."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from tools.audit_module_boundaries import inspect_python,domain_for,save_audit

class BoundaryTests(unittest.TestCase):
    def test_domain_routing(self):
        self.assertEqual(domain_for("src/opensees_engine/standalone.py"),
                         "OPENSEES_INDEPENDENT_CORE")
        self.assertEqual(domain_for("components/model/assembly.py"),
                         "MIXED_SOURCE_ASSEMBLY_MIGRATION_REQUIRED")
        self.assertEqual(domain_for("components/gravity/solver_stack.py"),
                         "ETABS_OPENSEES_INTEGRATION")
    def test_forbidden_import_caught(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f=root/"test.py"
            f.write_text("from comtypes import client\n",encoding="utf-8")
            obj=inspect_python(f,"src/opensees_engine/test.py")
            self.assertEqual(obj["forbidden_imports"],["comtypes"])
    def test_normal_opensees_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f=root/"test.py"
            f.write_text("import openseespy.opensees as ops\ndef run(): pass\n",
                         encoding="utf-8")
            obj=inspect_python(f,"src/opensees_engine/test.py")
            self.assertFalse(obj["forbidden_imports"])
            self.assertEqual(obj["symbols"],["run"])
    def test_errors_reported_and_not_executed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f=root/"bad.py"
            f.write_text("raise Exception('do not execute')\n",encoding="utf-8")
            obj=inspect_python(f,"src/thesis_core/bad.py")
            self.assertEqual(obj["parse_status"],"PARSED")
            bad=root/"syntax.py"
            bad.write_text("def oops(:\n",encoding="utf-8")
            self.assertEqual(inspect_python(bad,"src/thesis_core/syntax.py")["parse_status"],
                             "SYNTAX_OR_ENCODING_ERROR")
    def test_report_writer(self):
        with tempfile.TemporaryDirectory() as d:
            result=save_audit({
                "active_python_files":0,"modules":[],
                "duplicate_content_groups_active":[],
                "forbidden_independent_core_imports":[],
                "parse_failures":[]},d)
            self.assertTrue((result/"MODULE_OWNERS.csv").is_file())

if __name__=="__main__":unittest.main()
