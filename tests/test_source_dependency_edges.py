"""Regression: static module audits must account for relative imports.

No ETABS, OpenSees or native engineering execution.
"""
import ast
import tempfile
import unittest
from pathlib import Path

from tools.module_import_edges import import_targets
from tools.audit_cross_module_consistency import scan_consistency
from tools.audit_output_writer_reader_pairs import build_matrix


class SourceDependencyEdgesTests(unittest.TestCase):
    def test_relative_and_absolute_modules_and_no_fabricated_symbols(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for sub in ("components/inputs","components/gravity","components/model"):
                (root/sub).mkdir(parents=True,exist_ok=True)
            (root/"components/inputs/workbook.py").write_text("",encoding="utf-8")
            (root/"components/gravity/reader.py").write_text("",encoding="utf-8")
            src=("import components.model.assembly\n"
                 "from ..inputs import workbook\n"
                 "from . import reader\n"
                 "from .reader import callable_symbol\n"
                 "from components.model import analysis_basis\n"
                 "from . import missing_symbol\n")
            got=import_targets(ast.parse(src),"components/gravity/workflow.py",root=root)
            self.assertIn("components.inputs.workbook",got)
            self.assertIn("components.gravity.reader",got)
            self.assertIn("components.model.assembly",got)
            self.assertIn("components.model",got)
            self.assertNotIn("components.gravity.missing_symbol",got)
            self.assertNotIn("components.gravity.reader.callable_symbol",got)

    def test_package_levels_and_no_invalid_parent_guess(self):
        src="from ...inputs import workbook\nfrom ....invalid import x\nfrom . import local\n"
        got=import_targets(ast.parse(src),"components/gravity/deep/workflow.py")
        self.assertIn("components.inputs",got)
        self.assertIn("components.gravity.deep",got)
        self.assertFalse(any(".invalid" in x for x in got))

    def test_relative_edges_reach_both_integrated_audits(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for sub in ("components/inputs","components/gravity"):
                (root/sub).mkdir(parents=True,exist_ok=True)
            (root/"components/inputs/workbook.py").write_text("VALUE=1\n",encoding="utf-8")
            (root/"components/gravity/reader.py").write_text("VALUE=2\n",encoding="utf-8")
            (root/"components/gravity/runner.py").write_text(
                "from ..inputs import workbook\n"
                "from . import reader\n"
                "def load():\n"
                "    return workbook.VALUE + reader.VALUE\n",encoding="utf-8")
            module=scan_consistency(root)
            self.assertIn({"from_owner":"GRAVITY","to_owner":"SOURCE_INPUTS",
                           "source_files_with_import":1},
                          module["module_owner_import_links"])
            matrix=build_matrix(root)
            selected=next(row for row in matrix["sources"]
                          if row["source"]=="components/gravity/runner.py")
            self.assertIn("components.inputs.workbook",selected["local_imports"])
            self.assertIn("components.gravity.reader",selected["local_imports"])

    def test_root_source_does_not_invent_relative_import_target(self):
        self.assertEqual(import_targets(ast.parse("from . import helper\n"),
                                        "runner.py"),[])


if __name__=="__main__":
    unittest.main()
