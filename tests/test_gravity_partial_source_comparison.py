"""Regression: incomplete 32/76/97 solve matrix must not invent reactions."""
import json
import tempfile
import unittest
from pathlib import Path

from components.gravity.three_case_comparison import join_source_etabs_reactions


class PartialGravityComparisonTests(unittest.TestCase):
    def test_32_only_preserves_76_source_rows_without_fabricating_solver_values(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            audit = {
                "mode": "ETABS_NONZERO_REACTION_DIAGNOSTIC",
                "case": "1. DL + LL",
                "original_support_count": 76,
                "kept_support_count": 32,
                "tolerance_kN": 1e-6,
                "etabs_total_FZ_kN": 32000.0,
                "mapping": [
                    {
                        "opensees_node": i,
                        "etabs_unique": str(1000 + i),
                        "etabs_FZ_kN": 1000.0 if i <= 32 else 0.0,
                        "source_restraints": [1] * 6,
                        "selected": i <= 32,
                    }
                    for i in range(1, 77)
                ],
            }
            (root / "ETABS_Nonzero_Reaction_Support_Audit.json").write_text(
                json.dumps(audit), encoding="utf-8"
            )
            available = {
                "32": (
                    {"result_path": str(root / "Gravity_Result_V110.json")},
                    {"reactions": [{"node_tag": i, "rz_kN": 1000.0}
                                   for i in range(1, 33)]},
                )
            }
            solved = [
                {"node_tag": i, "rz_32_kN": 1000.0,
                 "rz_76_kN": None, "rz_97_kN": None}
                for i in range(1, 33)
            ]
            rows, summary = join_source_etabs_reactions(available, solved)
            self.assertEqual(len(rows), 76)
            self.assertEqual(summary["source_rows_without_any_solved_reaction"], 44)
            self.assertEqual(summary["available_solved_case_columns"], ["32"])
            self.assertEqual(summary["sum_abs_delta_primary_32_kN"], 0.0)
            self.assertEqual(rows[40]["opensees_node"], 41)
            self.assertIsNone(rows[40]["opensees_32_Rz_kN"])
            self.assertIsNone(rows[40]["opensees_76_Rz_kN"])
            self.assertEqual(rows[40]["original_ETABS_FZ_kN"], 0.0)

    def test_duplicate_solved_tags_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            audit = {
                "mode": "ETABS_NONZERO_REACTION_DIAGNOSTIC",
                "case": "1. DL + LL", "original_support_count": 76,
                "kept_support_count": 32, "etabs_total_FZ_kN": 32000.,
                "mapping": [
                    {"opensees_node": i, "etabs_unique": str(i),
                     "etabs_FZ_kN": 1000. if i <= 32 else 0.,
                     "source_restraints": [1] * 6, "selected": i <= 32}
                    for i in range(1, 77)
                ],
            }
            (root / "ETABS_Nonzero_Reaction_Support_Audit.json").write_text(
                json.dumps(audit), encoding="utf-8"
            )
            available = {"32": (
                {"result_path": str(root / "Gravity_Result_V110.json")},
                {"reactions": [{"node_tag": i} for i in range(1, 33)]},
            )}
            repeated = [
                {"node_tag": 1, "rz_32_kN": 1000.,
                 "rz_76_kN": None, "rz_97_kN": None}
            ] * 2
            with self.assertRaisesRegex(ValueError, "Duplicate solved"):
                join_source_etabs_reactions(available, repeated)


if __name__ == "__main__":
    unittest.main()
