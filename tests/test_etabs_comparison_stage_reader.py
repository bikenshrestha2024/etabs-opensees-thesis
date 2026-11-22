"""ETABS comparison reader must retain canonical all-stage discovery.

[REF docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md]
This is navigation coverage, not a native numerical equivalence check.
"""
import inspect
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from components.validation import etabs_comparison


class ETABSComparisonStageReaderTests(unittest.TestCase):
    def test_collect_uses_canonical_stage_discovery_with_legacy_fallback(self):
        text=inspect.getsource(etabs_comparison.collect)
        self.assertIn("result_roots",text)
        for stage in ("GRAVITY","ESM","MODAL","MRSM","LTHA","NLTHA"):
            self.assertIn("'"+stage+"'",text)
        self.assertIn("include_legacy=True",text)
        self.assertIn("model_sha256",text)
        self.assertIn("selected_state",text)

    def test_same_source_root_is_discovered_without_accepting_missing_results(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            model=root/"OpenSees_Complete_Model_Data_V118.json"
            model.write_text('{"source":"fixture"}',encoding="utf-8")
            (root/"05_MRSM").mkdir()
            with patch("components.inputs.project_workbooks.source_limit_state",
                       return_value=("ULS","fixture")),patch(
                       "components.inputs.project_workbooks.analysis_output_folder",
                       return_value=root/"03_ESM"),patch(
                       "components.inputs.output_layout.result_roots",
                       return_value=(root/"05_MRSM",)) as roots:
                issues=[]
                result=etabs_comparison.collect(root,issues)
            self.assertEqual(result,[])
            self.assertTrue(roots.called)
            self.assertEqual(roots.call_args.kwargs.get("include_legacy"),True)


if __name__=="__main__":
    unittest.main()
