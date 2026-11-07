"""Fail-closed thesis evidence dashboard regression tests (standard library)."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from components.validation.thesis_evidence_dashboard import STAGES, audit, save_reports

class EvidenceDashboardChecks(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/"source.txt").write_text("reproducible source",encoding="utf8")
        self.digest=hashlib.sha256((self.root/"source.txt").read_bytes()).hexdigest()

    def payload(self,n=0):
        return {"stages":{name:{"status":"VERIFIED" if idx<n else "NOT_STARTED",
             "evidence":[{"path":"source.txt","sha256":self.digest}] if idx<n else []}
             for idx,(name,_) in enumerate(STAGES)}}

    def check(self,data):
        return audit(data,manifest_dir=self.root)

    def test_no_evidence_cannot_pass(self):
        p=self.payload()
        p["stages"][STAGES[0][0]]={"status":"VERIFIED","evidence":[]}
        r=self.check(p)
        self.assertFalse(r["stages"][0]["identity_verified"])
        self.assertFalse(r["engineering_accepted"])

    def test_modified_evidence_fails(self):
        p=self.payload(1)
        (self.root/"source.txt").write_text("changed")
        self.assertEqual(self.check(p)["stages"][0]["evaluated_status"],"BLOCKED")

    def test_stage_cannot_skip_predecessor(self):
        p=self.payload()
        p["stages"][STAGES[1][0]]={"status":"VERIFIED",
            "evidence":[{"path":"source.txt","sha256":self.digest}]}
        self.assertIn("Earlier stage",self.check(p)["stages"][1]["issues"])

    def test_all_verified_identity_is_not_code_approval(self):
        r=self.check(self.payload(len(STAGES)))
        self.assertTrue(r["all_stage_identities_verified"])
        self.assertFalse(r["engineering_accepted"])
        save_reports(r,self.root/"out")
        self.assertTrue((self.root/"out"/"Thesis_Evidence_Dashboard.csv").is_file())
        self.assertTrue((self.root/"out"/"Thesis_Evidence_Dashboard.json").is_file())

    def test_nonexistent_or_bad_hash_blocks(self):
        p=self.payload(1)
        p["stages"][STAGES[0][0]]["evidence"]=[{"path":"not-here.csv","sha256":"bad"}]
        r=self.check(p)
        self.assertIn("not found",r["stages"][0]["issues"])
        self.assertEqual(r["stages"][0]["evaluated_status"],"BLOCKED")

    def test_invalid_status_rejected(self):
        p=self.payload()
        p["stages"][STAGES[0][0]]["status"]="CERTIFIED"
        with self.assertRaises(ValueError):
            self.check(p)

if __name__=="__main__":
    unittest.main()
