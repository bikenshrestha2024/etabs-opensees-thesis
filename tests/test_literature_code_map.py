"""Tests for the literature-to-code map generator (offline, stdlib only).

[REF docs/00_RESEARCH_REFERENCES.md R01-R13]
"""
from __future__ import annotations

import ast
import builtins
import csv
import io
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import audit_literature_code_map as tool

ROOT = Path(__file__).resolve().parents[1]
REGISTER_IDS = ["R%02d" % n for n in range(1, 14)]
REGISTER_TEXT = (
    "| ID | Bibliographic source | Source URL | Appropriate use | Explicit transfer restriction |\n"
    "|---|---|---|---|---|\n"
    "| R01 | Paper one | [Source](https://peer.berkeley.edu/x) | use | none |\n"
    "| R02 | Paper two | [Source](https://doi.org/10.1000/Abc.2) | use | none |\n"
    "| R03 | Paper three | [Source](https://doi.org/10.1000/abc.3) | use | none |\n"
)
MASTER_TEXT = (
    '"ID","Category","Title","Authors","Journal_or_report","Publication_date_or_status","DOI"\n'
    '"L001","c","Two again","a","j","2020","10.1000/abc.2"\n'
    '"L002","c","No doi","a","j","2020",""\n'
)


def make_fixture(base):
    """Create a tiny repo-shaped tree; returns its root."""
    root = Path(base)
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00_RESEARCH_REFERENCES.md").write_text(REGISTER_TEXT, encoding="utf-8")
    (root / "LITERATURE").mkdir()
    (root / "LITERATURE" / "MASTER_LITERATURE_INDEX.csv").write_text(MASTER_TEXT, encoding="utf-8")
    (root / "LITERATURE" / "secret.pdf").write_bytes(b"%PDF-1.4 confidential R03")
    (root / "components").mkdir()
    (root / "components" / "wall.py").write_text(
        '"""Wall model.\n\n[REF R01 PEER 2015/12]\n"""\n'
        "# see doi 10.1000/ABC.2 for the formulation\n"
        "DATA = 'R03'  # plain literal below is not a citation\n"
        "X = 'R03'\n", encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_wall.py").write_text(
        'def test_a():\n    assert "R03" in "R03"\n', encoding="utf-8")
    return root


class LiteratureCodeMapTests(unittest.TestCase):
    def test_fixture_mapping_statuses(self):
        with tempfile.TemporaryDirectory() as name:
            rows = {r["reference_id"]: r for r in tool.build_map(make_fixture(name))}
        self.assertEqual(rows["R01"]["status"], "CITED_IN_CODE")
        self.assertIn("REF-tag", rows["R01"]["match_kinds"])
        self.assertEqual(rows["R02"]["status"], "CITED_IN_CODE")  # DOI, case-insensitive
        self.assertEqual(rows["R02"]["also_listed_as"], "L001")
        self.assertEqual(rows["L001"]["status"], "CITED_IN_CODE")
        # plain string literals and assertIn-style test data are not citations
        self.assertEqual(rows["R03"]["status"], "UNIMPLEMENTED")
        self.assertEqual(rows["L002"]["status"], "UNIMPLEMENTED")

    def test_real_repo_output_is_deterministic_and_has_r01_to_r13(self):
        first = tool.build_map(ROOT)
        second = tool.build_map(ROOT)
        self.assertEqual(tool.render_markdown(first), tool.render_markdown(second))
        self.assertEqual(tool.render_csv(first), tool.render_csv(second))
        ids = [r["reference_id"] for r in first]
        md = tool.render_markdown(first)
        for ref in REGISTER_IDS:
            self.assertIn(ref, ids)
            self.assertIn("| %s |" % ref, md)

    def test_cli_writes_identical_bytes_on_two_runs_inside_repo_copy(self):
        with tempfile.TemporaryDirectory() as name:
            root = make_fixture(name)
            tool.write_outputs(root, "docs/validation")
            md1 = (root / "docs/validation" / tool.MD_NAME).read_bytes()
            csv1 = (root / "docs/validation" / tool.CSV_NAME).read_bytes()
            tool.write_outputs(root, "docs/validation")
            self.assertEqual(md1, (root / "docs/validation" / tool.MD_NAME).read_bytes())
            self.assertEqual(csv1, (root / "docs/validation" / tool.CSV_NAME).read_bytes())
            self.assertEqual(tool.main(["--root", str(root), "--check"]), 0)
            (root / "components" / "extra.py").write_text("# R03 [REF R03]\n", encoding="utf-8")
            self.assertEqual(tool.main(["--root", str(root), "--check"]), 1)
            rows = list(csv.DictReader(io.StringIO(csv1.decode("utf-8"))))
            self.assertEqual([r["reference_id"] for r in rows], ["R01", "R02", "R03", "L001", "L002"])

    def test_committed_map_is_current(self):
        self.assertEqual(tool.main(["--root", str(ROOT), "--check"]), 0,
                         "run: python tools/audit_literature_code_map.py")

    def test_no_network_no_pdf_and_stays_inside_repo(self):
        opened = []
        real_open = builtins.open
        real_path_open = Path.open

        def spy_open(file, *args, **kwargs):
            opened.append(str(file))
            return real_open(file, *args, **kwargs)

        def spy_path_open(self, *args, **kwargs):
            opened.append(str(self))
            return real_path_open(self, *args, **kwargs)

        def deny(*args, **kwargs):
            raise AssertionError("network access attempted")

        with tempfile.TemporaryDirectory() as name:
            root = make_fixture(name)
            with mock.patch.object(socket, "socket", deny), \
                    mock.patch.object(socket, "create_connection", deny), \
                    mock.patch.object(socket, "getaddrinfo", deny), \
                    mock.patch.object(builtins, "open", spy_open), \
                    mock.patch.object(Path, "open", spy_path_open):
                tool.write_outputs(root, "docs/validation")
            self.assertFalse([p for p in opened if p.lower().endswith(".pdf")], opened)
            with self.assertRaises(ValueError):
                tool.write_outputs(root, root.parent / "outside_repo_dir")
            self.assertFalse((root.parent / "outside_repo_dir").exists())

    def test_tool_source_has_no_network_imports(self):
        tree = ast.parse((ROOT / "tools" / "audit_literature_code_map.py").read_text(encoding="utf-8"))
        banned = {"socket", "urllib", "http", "requests", "ftplib", "subprocess", "ssl"}
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(imported & banned, set())


if __name__ == "__main__":
    unittest.main()
