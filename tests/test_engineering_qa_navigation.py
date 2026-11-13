"""Check category structure and local Markdown links in the P-Delta review Q&A.

No solver/ETABS/PDF inputs or runtime files are accessed.
[REF docs/source/tests/test_engineering_qa_navigation.py.md]
"""
from pathlib import Path
import re
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "REVIEW_MAIN" / "09_ENGINEERING_QA"
PAGES = [
    QA / "README.md",
    QA / "01_CODE_BASIS" / "README.md",
    QA / "02_PDELTA_INITIAL_STATES" / "README.md",
    QA / "02_PDELTA_INITIAL_STATES" / "01_SIGNED_EL_VS_GRAVITY_START.md",
    QA / "03_GRAVITY_MASS" / "README.md",
    QA / "04_ETABS_OPENSEES" / "README.md",
    QA / "05_TIME_HISTORY" / "README.md",
]
BACKLINKS = [
    ROOT / "REVIEW_MAIN" / "README.md",
    ROOT / "07_REVIEW_MAIN" / "README.md",
    ROOT / "REVIEW_MAIN" / "00_MODEL" / "20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md",
    ROOT / "REVIEW_MAIN" / "07_TIME_HISTORY" / "20261113_NBC_GRAVITY_PRELOAD_TO_EQ_TRANSIENT_DECISION.md",
    ROOT / "KNOWLEDGE_BASE" / "06_COORDINATED_RUNBOOK" / "README.md",
]
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


class EngineeringQANavigation(unittest.TestCase):
    def test_expected_categories_exist(self):
        for path in PAGES:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), str(path))

    def test_all_new_internal_markdown_links_resolve(self):
        for path in PAGES + BACKLINKS:
            with self.subTest(source=str(path)):
                data = path.read_text(encoding="utf-8")
                for href in LINK.findall(data):
                    href = unquote(href.split("#", 1)[0]).strip()
                    if not href or "://" in href or href.startswith("mailto:"):
                        continue
                    self.assertTrue((path.parent / href).resolve().exists(),
                                    f"Broken review link in {path}: {href}")

    def test_conclusions_and_open_gates_are_not_hidden(self):
        detailed = PAGES[3].read_text(encoding="utf-8")
        for required in (
            "COMPULSORY", "GRAVITY_INITIALIZED_DYNAMIC",
            "SIGNED_EL_BIASED_DIAGNOSTIC", "loadConst",
            "wipeAnalysis", "5.2", "double-count",
            "2025", "NOT", "CSI", "OpenSees",
        ):
            with self.subTest(required=required):
                self.assertIn(required, detailed)

    def test_canonical_review_gateway_has_qa_link(self):
        self.assertIn("09_ENGINEERING_QA", BACKLINKS[0].read_text(encoding="utf-8"))
        self.assertIn("09_ENGINEERING_QA", BACKLINKS[1].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
