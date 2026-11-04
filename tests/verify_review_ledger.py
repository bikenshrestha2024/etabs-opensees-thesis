"""Integrity tests for ledger; source inspection claims remain human-audited."""
import csv
import tempfile
import unittest
from pathlib import Path
from tools.validate_review_ledger import validate_ledger, LEDGER, BASE, FIELDS

class LedgerVerification(unittest.TestCase):
    def test_baseline_complete(self):
        result=validate_ledger()
        self.assertGreater(result["files"],200)
        self.assertLess(result["actually_inspected"],result["files"])
        self.assertGreater(result["not_reviewed"],100)
    def test_duplicate_entries_cannot_masquerade_as_coverage(self):
        with LEDGER.open(newline="",encoding="utf8") as h:
            rows=list(csv.DictReader(h))
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"ledger.csv"
            with path.open("w",newline="",encoding="utf8") as h:
                w=csv.DictWriter(h,fieldnames=FIELDS)
                w.writeheader()
                w.writerows(rows+[dict(rows[0])])
            with self.assertRaisesRegex(ValueError,"duplicate"):
                validate_ledger(path)
    def test_unreviewed_row_cannot_claim_findings(self):
        with LEDGER.open(newline="",encoding="utf8") as h:
            rows=list(csv.DictReader(h))
        idx=next(i for i,r in enumerate(rows) if r["review_status"]=="NOT_REVIEWED")
        rows[idx]["finding_or_risk"]="Verified by AI"
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"ledger.csv"
            with path.open("w",newline="",encoding="utf8") as h:
                w=csv.DictWriter(h,fieldnames=FIELDS)
                w.writeheader()
                w.writerows(rows)
            with self.assertRaisesRegex(ValueError,"invented findings"):
                validate_ledger(path)

if __name__=="__main__":
    unittest.main()
