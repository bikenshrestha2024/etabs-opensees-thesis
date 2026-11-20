"""Tests for the literature-to-code map generator (offline, stdlib only).

[REF docs/00_RESEARCH_REFERENCES.md R01-R13]
"""
from __future__ import annotations

import ast
import builtins
import csv
import io
import shutil
import socket
import subprocess
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
        # subprocess is allowed only for `git ls-files` / `git rev-parse` (checked below).
        banned = {"socket", "urllib", "http", "requests", "ftplib", "ssl"}
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(imported & banned, set())
        git_calls = [n for n in ast.walk(tree) if isinstance(n, ast.List) and n.elts
                     and isinstance(n.elts[0], ast.Constant) and n.elts[0].value == "git"]
        self.assertTrue(git_calls)
        for call in git_calls:
            words = [e.value for e in call.elts if isinstance(e, ast.Constant)]
            self.assertTrue({"ls-files", "rev-parse"} & set(words), words)

    def test_check_accepts_crlf_checkout(self):
        with tempfile.TemporaryDirectory() as name:
            root = make_fixture(name)
            tool.write_outputs(root, "docs/validation")
            for file_name in (tool.MD_NAME, tool.CSV_NAME):
                path = root / "docs/validation" / file_name
                path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
            self.assertEqual(tool.main(["--root", str(root), "--check"]), 0)

    def test_gitattributes_pins_map_to_lf(self):
        text = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("docs/validation/LITERATURE_CODE_MAP.* text eol=lf", text)

    @unittest.skipUnless(shutil.which("git"), "git not installed")
    def test_scan_uses_git_tracked_files_only(self):
        with tempfile.TemporaryDirectory() as name:
            root = make_fixture(name)
            git = ["git", "-C", str(root)]
            subprocess.run(git + ["init", "-q"], check=True)
            subprocess.run(git + ["add", "-A"], check=True)
            (root / "components" / "scratch.py").write_text("# [REF R03]\n", encoding="utf-8")
            self.assertNotIn("components/scratch.py", tool.scan_files(root))
            rows = {r["reference_id"]: r for r in tool.build_map(root)}
            self.assertEqual(rows["R03"]["status"], "UNIMPLEMENTED")
            tool.write_outputs(root, "docs/validation")
            # untracked scratch file present: --check must still be current
            self.assertEqual(tool.main(["--root", str(root), "--check"]), 0)

    def test_scan_falls_back_to_filesystem_without_git_repo(self):
        with tempfile.TemporaryDirectory() as name:
            root = make_fixture(name)
            self.assertIn("components/wall.py", tool.scan_files(root))

    def test_url_and_author_year_citations_detected(self):
        register = REGISTER_TEXT + (
            "| R04 | Stokley and Lowes (2024), PEER 2024/11, Layered Shell Model | [Source](https://peer.berkeley.edu/) | use | none |\n"
            "| R05 | Cao et al. (2024), BRB eccentricity | [Source](https://example.org/papers/cao-2024) | use | none |\n"
            "| R06 | Ji, Sun and Wang (2023), T walls | [Source](https://doi.org/10.1000/zzz.6) | use | none |\n")
        with tempfile.TemporaryDirectory() as name:
            root = make_fixture(name)
            (root / "docs" / "00_RESEARCH_REFERENCES.md").write_text(register, encoding="utf-8")
            (root / "components" / "val.py").write_text(
                "S={'u':'https://example.org/papers/cao-2024','n':'Stokley and Lowes: flexure walls'}\n",
                encoding="utf-8")
            (root / "components" / "other.py").write_text(
                "X='Ji alone, Sun elsewhere; Cao et al. 2019'\n", encoding="utf-8")
            rows = {r["reference_id"]: r for r in tool.build_map(root)}
        self.assertEqual(rows["R04"]["status"], "CITED_IN_CODE")
        self.assertIn("AUTHOR-YEAR", rows["R04"]["match_kinds"])
        self.assertEqual(rows["R05"]["status"], "CITED_IN_CODE")
        self.assertIn("URL", rows["R05"]["match_kinds"])
        self.assertEqual(rows["R06"]["status"], "UNIMPLEMENTED")  # near misses do not count

    def test_exact_title_year_author_cross_link_between_series(self):
        register = REGISTER_TEXT + (
            "| R04 | Stokley and Lowes (2024), PEER 2024/11, Evaluation of a Layered Shell Model | [Source](https://peer.berkeley.edu/) | use | none |\n"
            "| R05 | Stokley and Lowes (2023), Evaluation of a Layered Shell Model | [Source](https://peer.berkeley.edu/) | use | none |\n")
        master = MASTER_TEXT + (
            '"L003","c","Evaluation of a Layered Shell Model","Stokley; Lowes","j","2024",""\n'
            '"L004","c","Something else entirely different","Stokley; Lowes","j","2024",""\n')
        with tempfile.TemporaryDirectory() as name:
            root = make_fixture(name)
            (root / "docs" / "00_RESEARCH_REFERENCES.md").write_text(register, encoding="utf-8")
            (root / "LITERATURE" / "MASTER_LITERATURE_INDEX.csv").write_text(master, encoding="utf-8")
            (root / "components" / "val.py").write_text("# Stokley and Lowes layered shell\n", encoding="utf-8")
            rows = {r["reference_id"]: r for r in tool.build_map(root)}
        self.assertEqual(rows["L003"]["also_listed_as"], "R04")
        self.assertEqual(rows["R04"]["also_listed_as"], "L003")
        self.assertEqual(rows["L003"]["status"], "CITED_IN_CODE")
        self.assertEqual(rows["L003"]["link_basis"], "TITLE_YEAR_AUTHOR")
        self.assertEqual(rows["L004"]["link_basis"], "UNKNOWN")  # no exact title match
        self.assertEqual(rows["L004"]["status"], "UNIMPLEMENTED")
        self.assertEqual(rows["R05"]["also_listed_as"], "")  # year differs


if __name__ == "__main__":
    unittest.main()
