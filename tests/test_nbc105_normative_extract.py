"""Deterministic tests of the NBC 105:2025 normative-unit extractor (synthetic text only).

[REF NBC105-2025 register] The real PDF is not stored in the repository; these
tests use short invented pages with the same layout features. A pass proves the
tool's parsing rules, not any engineering compliance.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import nbc105_normative_extract as X  # noqa: E402

PAGE1 = """5   Invented Clause

5.1   BASE SHEAR

      The designer shall compute the coefficient. It may be reduced by 10 percent.
      The value should not exceed 0.5 for ordinary cases.
      Narrative sentence without any number or modal verb here.

5.1.1 Sub Rule
      (a) first item that has no keyword at all here;

                       Table 5-9: Invented Factors

  Class         Value        Cap
  A              1.0         2.0
  B              1.5         2.5

1
    The value for class B shall be doubled.

                       Figure 5-9: Invented Figure

                                     30
"""
PAGE2 = """5.2   NEXT

      A story is soft if stiffness is less than 70% of the story above.
"""


class ExtractorTests(unittest.TestCase):
    def rows(self):
        return X.extract_units([PAGE1, PAGE2], first_pdf_page=50, start_group="5")[0]

    def test_page_mapping_matches_documented_offsets(self):
        self.assertEqual(X.printed_page_for_pdf_page(22), 1)
        self.assertEqual(X.printed_page_for_pdf_page(47), 26)
        self.assertEqual(X.printed_page_for_pdf_page(49), 26)
        self.assertEqual(X.printed_page_for_pdf_page(50), 27)
        self.assertEqual(X.printed_page_for_pdf_page(137), 114)
        with self.assertRaises(ValueError):
            X.printed_page_for_pdf_page(21)

    def test_kinds_and_subclauses(self):
        rows = self.rows()
        kinds = {(r["kind"], r["subclause"]) for r in rows}
        self.assertIn(("CLAUSE", "5.1"), kinds)
        self.assertIn(("SHALL", "5.1"), kinds)
        self.assertIn(("MAY", "5.1"), kinds)
        self.assertIn(("TABLE", "5.1.1"), kinds)
        self.assertIn(("FIGURE", "5.1.1"), kinds)
        self.assertIn(("FOOTNOTE", "5.1.1"), kinds)
        self.assertTrue(any(r["kind"] == "LIMIT" and r["subclause"] == "5.2" for r in rows))
        self.assertTrue(any(r["kind"] == "TABLE_ROW" and "Table 5-9" in r["locator"] for r in rows))

    def test_ids_are_sequential_and_locator_is_short(self):
        rows = self.rows()
        self.assertEqual(rows[0]["id"], "N5-0001")
        self.assertEqual([r["id"] for r in rows], [f"N5-{i:04d}" for i in range(1, len(rows) + 1)])
        for r in rows:
            self.assertLessEqual(len(r["locator"].split()), 20)
            self.assertEqual(len(r["sha256"]), 64)

    def test_deterministic_and_hash_normalises_whitespace(self):
        self.assertEqual(self.rows(), self.rows())
        self.assertEqual(X.unit_sha256("a  b\n c"), X.unit_sha256("a b c"))
        self.assertNotEqual(X.unit_sha256("a b c"), X.unit_sha256("a b d"))

    def test_rule_precedence_most_specific_wins_and_blank_when_unmatched(self):
        rows = self.rows()
        rules = [
            {"selector": "sub:5", "kind_filter": "", "disposition": "DEFINITION_ONLY",
             "implementation_ref": "", "test_ref": "", "evidence_note": "broad", "finding": ""},
            {"selector": "sub:5.1.1", "kind_filter": "FOOTNOTE", "disposition": "MANUAL_PROJECT_CHECK",
             "implementation_ref": "", "test_ref": "", "evidence_note": "narrow", "finding": ""},
        ]
        X.apply_rules(rows, rules)
        by = {r["kind"]: r for r in rows if r["kind"] in ("FOOTNOTE", "FIGURE")}
        self.assertEqual(by["FOOTNOTE"]["disposition"], "MANUAL_PROJECT_CHECK")
        self.assertEqual(by["FIGURE"]["disposition"], "DEFINITION_ONLY")
        X.apply_rules(rows, [])
        self.assertTrue(all(r["disposition"] == "" for r in rows))

    def test_check_reports_unreviewed_and_hash_drift(self):
        rows = self.rows()
        rep = X.check_register(rows, rows)
        self.assertFalse(rep["ok"])
        self.assertEqual(len(rep["unreviewed"]), len(rows))
        for r in rows:
            r["disposition"] = "DEFINITION_ONLY"
        self.assertTrue(X.check_register(rows, self.rows())["ok"])
        changed = self.rows()
        changed[3]["sha256"] = "0" * 64
        rep = X.check_register(rows, changed)
        self.assertEqual(rep["drift_changed"], [rows[3]["id"]])
        self.assertFalse(rep["ok"])

    def test_summary_never_claims_certification(self):
        rows = self.rows()
        text = X.clause_summary_markdown(rows)
        self.assertIn("NOT CERTIFIED", text)
        self.assertNotIn("CERTIFIED\n", text.replace("NOT CERTIFIED", ""))


if __name__ == "__main__":
    unittest.main()
