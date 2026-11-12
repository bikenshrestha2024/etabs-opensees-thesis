"""Source contract: the user's 32-node GRAVITY DIAGNOSTIC display does not
alter the 76-source-support baseline of modal and other analyses."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GravitySupportDefaultPolicyTests(unittest.TestCase):
    def test_diagnostic_ui_default_is_labeled_non_equivalent(self):
        text = (ROOT / "components/gravity/gui_and_reports.py").read_text(
            encoding="utf-8-sig")
        ast.parse(text)
        self.assertIn(
            'self.wall_support_strategy_var.set("32 nonzero-reaction nodes (diagnostic)")',
            text)
        self.assertIn(
            '"32 nonzero-reaction nodes (diagnostic)": '
            '"ETABS_NONZERO_REACTION_DIAGNOSTIC"', text)
        self.assertIn('NOT equivalent', text)

    def test_full_build_keeps_source_restraints(self):
        text = (ROOT / "components/model/assembly.py").read_text(
            encoding="utf-8-sig")
        ast.parse(text)
        self.assertIn(
            "'OPENSEES_GRAVITY_WALL_SUPPORT_STRATEGY',", text)
        self.assertIn("'ETABS_SOURCE_SUPPORTS')", text)
        self.assertIn(
            "and not os.environ.get('OPENSEES_GRAVITY_GUI_MODE')", text)


if __name__ == "__main__":
    unittest.main()
