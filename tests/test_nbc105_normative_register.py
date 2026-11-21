"""Deterministic tests of the normative register loader, validator and fail-closed gate.

[REF NBC105-2025 normative register] These tests exercise the gate logic and the
committed register's internal consistency. A pass is not engineering acceptance
and does not certify the standard or any building.
"""
import contextlib
import copy
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import nbc105_normative_extract as X  # noqa: E402
from components.nbc105 import normative_register as N  # noqa: E402


def _row(i, disp="DEFINITION_ONLY", **kw):
    r = {c: "" for c in N.REGISTER_COLUMNS}
    r.update(id=f"N1-{i:04d}", clause="1", subclause="1.1", printed_page="1", kind="SHALL",
            locator="x", sha256="a" * 64, disposition=disp)
    r.update(kw)
    return r


class RealRegister(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = N.load_register()
        cls.gate = N.normative_register_gate()

    def test_gate_never_certifies_and_counts_match(self):
        g = self.gate
        self.assertFalse(g["certified"])
        self.assertNotIn("CERTIFIED", {g["status"]})
        self.assertEqual(g["rows"], len(self.rows))
        self.assertEqual(sum(g["disposition_counts"].values()), len(self.rows))
        self.assertEqual(g["unreviewed_rows"], sum(1 for r in self.rows if not r["disposition"]))
        self.assertEqual(g["unverified_gap_rows"], sum(1 for r in self.rows if r["disposition"] == "UNVERIFIED_GAP"))
        self.assertEqual(len(g["external_gates"]), 3)

    def test_committed_register_has_no_blank_invalid_or_unresolved_rows(self):
        problems = N.validate_register(self.rows)
        for key, found in problems.items():
            self.assertEqual(found, [], key)
        self.assertEqual(self.gate["status"], "REGISTER_REVIEWED_EXTERNAL_GATES_OPEN")

    def test_manifest_row_count_matches_and_ids_are_unique(self):
        manifest = json.loads(N.manifest_path().read_text(encoding="utf-8"))
        self.assertEqual(manifest["rows"], len(self.rows))
        self.assertEqual(len({r["id"] for r in self.rows}), len(self.rows))

    def test_dispositions_and_columns_match_the_extractor(self):
        self.assertEqual(N.DISPOSITIONS, X.DISPOSITIONS)
        self.assertEqual(N.REGISTER_COLUMNS, X.REGISTER_COLUMNS)

    def test_register_files_are_lf_only(self):
        for name in ("NORMATIVE_REGISTER.csv", "DISPOSITION_RULES.csv", "CLAUSE_SUMMARY.md", "EXTRACTION_MANIFEST.json"):
            data = (N.REGISTER_DIR / name).read_bytes()
            self.assertNotIn(b"\r", data, name)

    def test_clause_summary_is_current(self):
        expected = X.clause_summary_markdown(self.rows)
        actual = (N.REGISTER_DIR / "CLAUSE_SUMMARY.md").read_text(encoding="utf-8")
        self.assertEqual(actual.replace("\r\n", "\n"), expected)

    def test_pinned_special_rows_have_the_expected_disposition(self):
        by_loc = {(r["clause"], r["locator"][:20]): r for r in self.rows}
        table_c1 = [r for r in self.rows if r["clause"] == "C"]
        self.assertEqual([r["disposition"] for r in table_c1], ["EXTERNAL_DATA_REQUIRED"])
        t101 = [r for r in self.rows if r["locator"].startswith("Table 10-1") and r["kind"] == "TABLE"]
        self.assertEqual(t101[0]["disposition"], "IMPLEMENTED_AND_TESTED")
        self.assertIn("0.5 s", t101[0]["evidence_note"])
        t52 = [r for r in self.rows if r["locator"].startswith("Table 5-2:") and r["kind"] == "TABLE_ROW"]
        self.assertGreaterEqual(len(t52), 21)
        self.assertTrue(by_loc)


class GateFailsClosed(unittest.TestCase):
    def test_blank_row_blocks_with_counts(self):
        g = N.normative_register_gate([_row(1), _row(2, disp="")], check_references=False)
        self.assertEqual(g["status"], "BLOCKED_NOT_CERTIFIED")
        self.assertEqual(g["unreviewed_rows"], 1)
        self.assertFalse(g["certified"])

    def test_unverified_gap_blocks_with_counts(self):
        g = N.normative_register_gate([_row(1), _row(2, disp="UNVERIFIED_GAP", evidence_note="open")], check_references=False)
        self.assertEqual(g["status"], "BLOCKED_NOT_CERTIFIED")
        self.assertEqual(g["unverified_gap_rows"], 1)

    def test_all_good_rows_still_not_certified(self):
        rows = [_row(1), _row(2, disp="MANUAL_PROJECT_CHECK", evidence_note="drawings")]
        g = N.normative_register_gate(rows, check_references=False)
        self.assertEqual(g["status"], "REGISTER_REVIEWED_EXTERNAL_GATES_OPEN")
        self.assertFalse(g["certified"])
        self.assertEqual(g["open_external_rows"]["MANUAL_PROJECT_CHECK"], 1)

    def test_validation_findings(self):
        rows = [
            _row(1, disp="BOGUS"),
            _row(2, disp="IMPLEMENTED_AND_TESTED"),
            _row(2, disp="MANUAL_PROJECT_CHECK"),
            _row(3, disp="PROJECT_NOT_APPLICABLE"),
            _row(4, disp="IMPLEMENTED_UNTESTED", implementation_ref="components/nbc105/constants.py::NO_SUCH_NAME"),
            _row(5, sha256="zz"),
            _row(6, clause="Z"),
        ]
        p = N.validate_register(rows)
        self.assertEqual(p["invalid_disposition"], ["N1-0001"])
        self.assertEqual(p["missing_reference"], ["N1-0002"])
        self.assertEqual(p["duplicate_id"], ["N1-0002"])
        self.assertEqual(p["missing_note"], ["N1-0002", "N1-0003"])
        self.assertTrue(p["unresolved_reference"][0].startswith("N1-0004: missing symbol"))
        self.assertEqual(p["bad_hash"], ["N1-0005"])
        self.assertEqual(p["unknown_clause"], ["N1-0006"])

    def test_unsafe_reference_paths_are_rejected(self):
        for ref in ("../outside.py::x", "/etc/passwd::x", "components/nbc105/constants.py::NOPE", "tests/missing_file.py::t"):
            p = N.validate_register([_row(1, disp="IMPLEMENTED_UNTESTED", implementation_ref=ref)])
            self.assertEqual(len(p["unresolved_reference"]), 1, ref)

    def test_real_reference_resolves(self):
        ref = "components/nbc105/constants.py::GRAVITY_M_S2"
        self.assertEqual(N.validate_register([_row(1, disp="IMPLEMENTED_UNTESTED", implementation_ref=ref)])["unresolved_reference"], [])

    def test_missing_or_bad_register_blocks(self):
        orig = N.REGISTER_CSV
        try:
            N.REGISTER_CSV = ROOT / "docs" / "nbc105" / "normative_register" / "does_not_exist.csv"
            g = N.normative_register_gate()
        finally:
            N.REGISTER_CSV = orig
        self.assertEqual(g["status"], "BLOCKED_NOT_CERTIFIED")
        self.assertTrue(g["blocking_reasons"][0].startswith("register unreadable"))
        self.assertEqual(N.normative_register_gate([])["status"], "BLOCKED_NOT_CERTIFIED")

    def test_does_not_mutate_input(self):
        rows = [_row(1)]
        before = copy.deepcopy(rows)
        N.normative_register_gate(rows, check_references=False)
        self.assertEqual(rows, before)


class Wiring(unittest.TestCase):
    def test_audit_cli_reports_register_and_exits_blocked(self):
        from components.nbc105.__main__ import main
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["--audit"])
        self.assertEqual(code, 2)
        obj = json.loads(out.getvalue())
        self.assertEqual(obj["approval"], "NOT_CERTIFIED_SOURCE_AND_NATIVE_EVIDENCE_OPEN")
        self.assertFalse(obj["normative_register"]["certified"])
        self.assertEqual(obj["normative_register"]["rows"], len(N.load_register()))

    def test_acceptance_exposes_register_and_stays_blocked(self):
        from components.nbc105.acceptance import evaluate_project_evidence
        rec = {"source_sha256": "a" * 64, "period_policy": "x", "adopted_periods": {},
               "final_rs": []}
        report = evaluate_project_evidence(rec)
        self.assertEqual(report["overall"], "BLOCKED_NOT_FULL_ENGINEERING_ACCEPTANCE")
        gate = report["gates"]["full_nbc_source_requirement_audit"]
        self.assertEqual(gate["status"], "OPEN")
        self.assertEqual(gate["normative_register_rows"], report["normative_register"]["rows"])
        self.assertFalse(report["normative_register"]["certified"])


if __name__ == "__main__":
    unittest.main()
