"""NBC 105 full-source audit must be evidence-based, not ten green modules.

Source section headings verified from the uploaded 2025 Second Revision,
printed contents pp. xiv–xx and Annexes A–C. This test does not claim that
individual paragraphs and detailing provisions have been validated.
"""
import unittest
from components.nbc105.compliance_coverage import (
    read_source_index, audit_source_index, source_index_path
)

class NBC105FullSourceGate(unittest.TestCase):
    def test_all_ten_clauses_and_all_three_annexes_present(self):
        report=audit_source_index(read_source_index())
        self.assertEqual(set(report["groups"]),set(map(str,range(1,11)))|{"A","B","C"})
        self.assertGreaterEqual(report["total_indexed_sections"],110)
        self.assertEqual(report["approval"],"NOT_CERTIFIED_SOURCE_AND_NATIVE_EVIDENCE_OPEN")

    def test_key_unverified_code_sections_are_never_ignored(self):
        report=audit_source_index(read_source_index())
        actual=set(report["indexed_ids"])
        for code in ("2.4.3","3.6.2","4.1.3.3","5.1.1","5.4.2.1",
                     "5.5.3","7.3","7.4","7.5","8.1.3",
                     "9.2.5","9.3.2.4","10.3.1","10.4",
                     "A.4.4.4","A.5.3","A.5.5","A.5.6",
                     "B.6.1.4","B.7.1.4","C.TABLE_C_1"):
            self.assertIn(code,actual)
        self.assertTrue(source_index_path().is_file())

    def test_cli_exposes_unverified_requirements_without_approving(self):
        import contextlib,io,json
        from components.nbc105.__main__ import main
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=main(["--audit"])
        self.assertEqual(code,2)
        obj=json.loads(output.getvalue())
        self.assertEqual(obj["approval"],"NOT_CERTIFIED_SOURCE_AND_NATIVE_EVIDENCE_OPEN")
        self.assertGreater(obj["open_requirements"],100)

    def test_section_missing_fails_source_index(self):
        items=read_source_index()
        items=[x for x in items if x["id"]!="A.5.6"]
        with self.assertRaisesRegex(ValueError,"missing"):
            audit_source_index(items)

    def test_duplicated_missing_page_or_empty_evidence_blocked(self):
        items=read_source_index()
        with self.assertRaises(ValueError):
            audit_source_index(items+[dict(items[0])])
        broken=[dict(x) for x in items]
        broken[0]["printed_page"]=0
        with self.assertRaises(ValueError):
            audit_source_index(broken)
        broken=[dict(x) for x in items]
        broken[0]["evidence_required"]=""
        with self.assertRaises(ValueError):
            audit_source_index(broken)

    def test_annex_helpers_have_existing_sources_and_are_not_clauses(self):
        original=read_source_index()
        for section in ("A.5.1","A.5.3","A.5.5","B.7.1.4"):
            row=next(x for x in original if x["id"]==section)
            self.assertTrue(row["reference_helper"].startswith("components/nbc105/annex_"))
            self.assertTrue(row["test_ref"])
        broken=[dict(x) for x in original]
        item=next(x for x in broken if x["id"]=="A.5.1")
        item["reference_helper"]="components/nbc105/annex_a_nonexistent.py"
        with self.assertRaisesRegex(ValueError,"annex helper"):
            audit_source_index(broken)

    def test_source_index_does_not_confuse_module_with_certification(self):
        report=audit_source_index(read_source_index())
        self.assertGreater(report["open_requirements"],0)
        self.assertIn("FULL_TEXT_PROVISION_AUDIT",report["mandatory_gates"])
        self.assertIn("ANNEX_A_REINFORCED_CONCRETE_DETAILING",report["mandatory_gates"])
        self.assertIn("NATIVE_ETABS_OPENSEES_COMPARISON",report["mandatory_gates"])
        self.assertIn("ANNEX_C_ALL_MUNICIPALITY_Z_VALUES",report["mandatory_gates"])

if __name__=="__main__":
    unittest.main()
