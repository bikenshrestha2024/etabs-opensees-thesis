"""Study-scoped saved history browser tests; no OpenSees solver needed."""
import tempfile
import unittest
from pathlib import Path

from components.ui.history_inspection import (
    choose_default_history_scope,
    history_scope_name,
)


class HistoryScopeTests(unittest.TestCase):
    def test_prefers_lth_in_mixed_results_without_mixing_nonlinear(self):
        scopes = [
            "Gravity_Results",
            "EXPLORATORY_FRAME_NL_20261112",
            "LTH_ULS_Trial_20261112_155716",
        ]
        selected = choose_default_history_scope(scopes)
        self.assertEqual(selected, "LTH_ULS_Trial_20261112_155716")

    def test_explicit_user_scope_persists(self):
        scopes = ["LTH_ULS_Trial", "EXPLORATORY_FRAME_NL"]
        self.assertEqual(
            choose_default_history_scope(scopes, "EXPLORATORY_FRAME_NL"),
            "EXPLORATORY_FRAME_NL",
        )

    def test_explicit_mixed_scope_survives_refresh(self):
        scopes = ["LTH_ULS_Trial", "EXPLORATORY_FRAME_NL"]
        self.assertEqual(
            choose_default_history_scope(scopes, "All analyses (mixed)"),
            "All analyses (mixed)",
        )

    def test_current_folder_with_saved_history_is_selected(self):
        self.assertEqual(
            choose_default_history_scope(["(This directory)", "record_inputs"]),
            "(This directory)",
        )

    def test_multiple_non_lth_scopes_are_explicitly_mixed_only_by_user(self):
        self.assertEqual(
            choose_default_history_scope(["EXPLORATORY_X", "EXPLORATORY_Y"]),
            "All analyses (mixed)",
        )

    def test_scope_uses_top_level_folder_and_direct_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertEqual(
                history_scope_name(root, root / "LTH_ULS" / "Analysis" / "run_history.csv"),
                "LTH_ULS",
            )
            self.assertEqual(
                history_scope_name(root, root / "run_history.csv"),
                "(This directory)",
            )


if __name__ == "__main__":
    unittest.main()
