"""The existing NBC settings UI must expose the ten canonical rule modules."""
import inspect
import unittest

from components.nbc105.dispatch import available_operations
from components.ui import nbc105_settings_panel


class NBCClauseGUIRouting(unittest.TestCase):
    def test_reference_viewer_exposes_canonical_calculator(self):
        source=inspect.getsource(nbc105_settings_panel.launch)
        self.assertIn("open_clause_calculator",source)
        self.assertIn("available_operations",source)
        self.assertIn("run_operation",source)
        self.assertIn("available_annex_operations",source)
        self.assertIn("run_annex_operation",source)
        self.assertIn("NBC clauses 1–10",source)
        self.assertEqual(set(available_operations()),set(range(1,11)))

if __name__=="__main__":
    unittest.main()
