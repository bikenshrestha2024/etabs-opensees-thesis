"""Consistency audit of the NBC 105:2025 documentation package.

Scope today: clauses 1, 4 and 5, the shared constants, PROJECT_DECLARATIONS,
WALL_GROUPING_AW_METHOD, the compliance matrices, the module guides and the
registry rows. Clauses 2, 3, Annex C and the UBC/SEAOC sources are deferred, so
register rows marked NOT_STARTED need no module or matrix.

A unit-test pass here is a documentation-consistency check only. It is not
engineering acceptance of any building and implies no native ETABS or OpenSees run.
"""
from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NBC_DOCS = ROOT / "docs" / "nbc105"
GUIDE_DIR = ROOT / "docs" / "source" / "components" / "nbc105"
MODULE_DIR = ROOT / "components" / "nbc105"
REGISTRY = ROOT / "engineering" / "registry" / "CANONICAL_MODULES.csv"

NOT_STARTED = "NOT_STARTED"
# A paragraph (or table row) mentioning a non-9.81 gravity value must carry one of these markers.
HISTORY_MARKERS = ("superseded", "supersedes", "superseding", "withdrawn", "history")
GRAVITY_NON_PRINTED = re.compile(r"9\.80665|9806\.65|9\.80(?!\d)|9\.8(?![\d])")
MATRIX_STATUS_VOCABULARY = {
    "IMPLEMENTED_AND_TESTED", "DEFINITION_ONLY", "REFERENCE_ONLY",
    "USER_RESPONSIBILITY", "CALLER_RESPONSIBILITY", "NOT_TRANSCRIBED",
    "NOT_APPLICABLE", "PRINCIPLE_ONLY",
}
# Statuses that may legitimately have no code location.
NO_CODE_STATUSES = {
    "DEFINITION_ONLY", "NOT_APPLICABLE", "PRINCIPLE_ONLY",
    "NOT_TRANSCRIBED", "USER_RESPONSIBILITY", "CALLER_RESPONSIBILITY",
}
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _nbc_md_files() -> list[Path]:
    return sorted(NBC_DOCS.glob("*.md")) + sorted(GUIDE_DIR.glob("*.md"))


def _table_after(text: str, header_prefix: str) -> list[list[str]]:
    """Rows (cells) of the first pipe table whose header starts with header_prefix."""
    lines = text.splitlines()
    rows: list[list[str]] = []
    start = None
    for i, line in enumerate(lines):
        if line.startswith(header_prefix):
            start = i
            break
    if start is None:
        return rows
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def _register_rows() -> list[dict]:
    text = _read(NBC_DOCS / "README.md")
    out = []
    for cells in _table_after(text, "| Clause | Title"):
        out.append({
            "clause": cells[0], "title": cells[1], "page": cells[2],
            "status": cells[3], "module": cells[4], "matrix": cells[5],
        })
    return out


def _link_target(cell: str) -> str | None:
    m = LINK.search(cell)
    return m.group(1) if m else None


def _paragraphs(text: str) -> list[str]:
    """Blank-line separated blocks; a block is one sentence group for marker purposes."""
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


class RegisterTests(unittest.TestCase):
    def test_register_has_rows(self) -> None:
        rows = _register_rows()
        self.assertGreaterEqual(len(rows), 13)
        self.assertEqual(rows[0]["clause"], "1")



    def test_not_started_rows_have_no_module_or_matrix_claim(self) -> None:
        for row in _register_rows():
            if row["status"] == NOT_STARTED:
                self.assertEqual(row["module"], "", row["clause"])
                self.assertEqual(row["matrix"], "", row["clause"])



class GravityTests(unittest.TestCase):
    def test_constant_is_printed_value(self) -> None:
        from components.nbc105 import constants
        self.assertEqual(constants.GRAVITY_M_S2, 9.81)
        self.assertEqual(constants.NBC_NOTATION_GRAVITY_M_S2, 9.81)

    def test_other_gravity_values_only_in_superseded_history(self) -> None:
        offenders = []
        for path in _nbc_md_files():
            for block in _paragraphs(_read(path)):
                if GRAVITY_NON_PRINTED.search(block) and not any(
                    m in block.lower() for m in HISTORY_MARKERS
                ):
                    offenders.append(f"{path.relative_to(ROOT)}: {block[:120]}")
        self.assertEqual(offenders, [])

    def test_key_docs_state_9_81(self) -> None:
        for name in (
            NBC_DOCS / "README.md",
            NBC_DOCS / "PROJECT_DECLARATIONS.md",
            NBC_DOCS / "clause_01_scope_definitions_matrix.md",
            NBC_DOCS / "clause_05_dynamic_characteristics_matrix.md",
            GUIDE_DIR / "constants.py.md",
        ):
            self.assertIn("9.81", _read(name), str(name.name))


class PageOffsetTests(unittest.TestCase):
    OFFSET = re.compile(r"(?:\bN|\bpage)\s*\+\s*(\d+)")

    def test_constant(self) -> None:
        from components.nbc105 import constants
        self.assertEqual(constants.PRINTED_PAGE_OFFSET, 21)


    def test_core_docs_state_both_offsets(self) -> None:
        for path in (
            NBC_DOCS / "README.md",
            NBC_DOCS / "clause_04_seismic_hazard_matrix.md",
            GUIDE_DIR / "constants.py.md",
        ):
            text = _read(path)
            self.assertRegex(text, r"21", path.name)
            self.assertRegex(text, r"(?:\+ ?|is |of )23", path.name)
            self.assertRegex(text, r"26", path.name)
            self.assertRegex(text, r"27", path.name)


class MatrixTests(unittest.TestCase):
    def _matrices(self) -> list[Path]:
        paths = sorted(NBC_DOCS.glob("clause_*_matrix.md"))
        self.assertTrue(paths)
        return paths


    def test_row_count_statement_matches_clause_1(self) -> None:
        path = NBC_DOCS / "clause_01_scope_definitions_matrix.md"
        text = _read(path)
        rows = _table_after(text, "| # | Clause | Printed page")
        m = re.search(r"\*\*Row count:\*\* (\d+) rows = (\d+) DEFINITION_ONLY, (\d+) IMPLEMENTED_AND_TESTED", text)
        self.assertTrue(m)
        tokens = [re.match(r"[A-Z_]+", r[6]).group(0) for r in rows]
        self.assertEqual(int(m.group(1)), len(rows))
        self.assertEqual(int(m.group(2)), tokens.count("DEFINITION_ONLY"))
        self.assertEqual(int(m.group(3)), tokens.count("IMPLEMENTED_AND_TESTED"))


class ModuleCoverageTests(unittest.TestCase):
    def _modules(self) -> list[Path]:
        return sorted(p for p in MODULE_DIR.glob("*.py"))

    def test_every_module_has_a_guide(self) -> None:
        for mod in self._modules():
            self.assertTrue((GUIDE_DIR / f"{mod.name}.md").exists(), mod.name)


    def test_every_guide_has_a_module(self) -> None:
        for guide in GUIDE_DIR.glob("*.py.md"):
            self.assertTrue((MODULE_DIR / guide.name[:-3]).exists(), guide.name)



class LinkTests(unittest.TestCase):
    def test_relative_links_resolve(self) -> None:
        broken = []
        for path in _nbc_md_files():
            for target in LINK.findall(_read(path)):
                if re.match(r"[a-z]+:", target) or target.startswith("#"):
                    continue
                dest = (path.parent / target.split("#")[0]).resolve()
                if not dest.exists():
                    broken.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
