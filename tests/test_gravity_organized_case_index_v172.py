"""Regression tests for published 32/76/97 gravity evidence navigation."""
import json
import tempfile
import unittest
from pathlib import Path
from components.gravity.reaction_case_registry import publish_gravity_case_index


class OrganizedGravityCaseTests(unittest.TestCase):
    def test_three_cases_are_separate_and_original_outputs_are_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            selection = Path(temp)
            results = selection / "OpenSees_Analysis_Results" / "ULS_model"
            results.mkdir(parents=True)
            strategies = {
                "ETABS_NONZERO_REACTION_DIAGNOSTIC": 32,
                "ETABS_SOURCE_SUPPORTS": 76,
                "CONTINUOUS_WALL_BASE_FIXED": 97,
            }
            for strategy, count in strategies.items():
                native = results / "legacy" / strategy
                native.mkdir(parents=True)
                native_result = native / "Gravity_Result_V110.json"
                native_result.write_text('{"ok":true}', encoding="utf-8")
                (native / "Gravity_Reactions_V123.png").write_bytes(b"plot-unchanged")
                record = {
                    "result_path": str(native_result),
                    "scenario": strategy,
                    "profile": "GRAVITY_1.0D_1.0L",
                    "support_count": count,
                    "model_sha256": "a" * 64,
                    "applied_load_kN": 100.0,
                    "summed_reaction_kN": 100.0,
                    "equilibrium_error_percent": 0.0,
                }
                published = publish_gravity_case_index(results, record)
                summary = json.loads(published.read_text())
                self.assertEqual(summary["support_count"], count)
                self.assertEqual(summary["support_strategy"], strategy)
                self.assertEqual(Path(summary["result_path"]), native_result)
                self.assertEqual(published.parent.name,strategy)
                self.assertEqual(published.parent.parent.name,"CASES")
                self.assertFalse((published.parent / "Gravity_Reactions_V123.png").exists())
                self.assertEqual((native / "Gravity_Reactions_V123.png").read_bytes(), b"plot-unchanged")
                self.assertEqual(native_result.read_text(), '{"ok":true}')
            for strategy in strategies:
                self.assertTrue((selection / "02_GRAVITY" / "00_INDEXES" / "CASES" / strategy).is_dir())

    def test_canonical_gravity_run_does_not_create_nested_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            selection = Path(temp)
            canonical = selection / "02_GRAVITY" / "RUNS" / "ULS" / "X"
            native = canonical / "20261115T000000Z"
            native.mkdir(parents=True)
            result = native / "Gravity_Result_V110.json"
            result.write_text('{"ok":true}', encoding="utf-8")
            record = {
                "result_path": str(result),
                "scenario": "ETABS_NONZERO_REACTION_DIAGNOSTIC",
                "profile": "AS_CONFIGURED",
                "support_count": 32,
                "model_sha256": "a" * 64,
                "applied_load_kN": 100.0,
                "summed_reaction_kN": 100.0,
                "equilibrium_error_percent": 0.0,
            }
            published = publish_gravity_case_index(canonical, record)
            self.assertEqual(published.parent.parent.parent.parent, selection / "02_GRAVITY")
            self.assertTrue((selection / "02_GRAVITY" / "00_INDEXES" / "LATEST_GRAVITY_CASES.json").exists())
            self.assertFalse((canonical / "02_GRAVITY").exists())
            self.assertEqual(result.read_text(), '{"ok":true}')



if __name__ == "__main__":
    unittest.main()
