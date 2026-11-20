"""Map every thesis literature reference to the code and tests that cite it.

[REF docs/00_RESEARCH_REFERENCES.md R01-R13 and evidence-tier policy]
[REF LITERATURE/README.md rules 1-7]

Reads only metadata and source text: ``docs/00_RESEARCH_REFERENCES.md``,
``LITERATURE/MASTER_LITERATURE_INDEX.csv`` and ``*.py`` files under
``components/``, ``src/`` and ``tests/``.  It never opens a PDF, never uses the
network and never writes outside ``--out-dir`` (which must be inside ``--root``).

Citation matching (provenance only, never validation):
  * register IDs ``R01``-``R13`` and master IDs ``L###`` inside a ``[REF ...]``
    tag, a comment or a docstring (plain string literals such as test data are
    ignored so that ``assertIn("R01", ...)`` is not counted as a citation);
  * the reference DOI anywhere in the file text (case-insensitive);
  * the register Source URL when it has a path (``URL``), and the register
    author-year (``AUTHOR-YEAR``: first two surnames joined by comma/and/&, or
    ``Surname et al.`` followed by the year) anywhere in the file text, string
    literals included, because these are specific enough not to be test data.

Cross-links: a register row and a master row are the same source when they share
a DOI, or when the master title is contained in the register title, the years
agree and the master first-author surname appears in the register author part
(``TITLE_YEAR_AUTHOR``).  Citations propagate across a link.  No match is shown
as ``UNKNOWN``.

Files scanned are the git-tracked ones (``git ls-files``) so untracked scratch
files cannot make ``--check`` stale; without a git work tree at ``--root`` the
filesystem is walked instead.  ``--check`` compares with normalised newlines.

Status values:
  CITED_IN_CODE        at least one components/ or src/ file cites the reference
  CITED_IN_TESTS_ONLY  only tests/ files cite it
  UNIMPLEMENTED        no components/, src/ or tests/ file cites it
A citation records where a source is *used as provenance*; it does not mean the
source's formulation was reproduced or the building model was verified.

Output is sorted and has no timestamps, so repeated runs are byte-identical.

    python tools/audit_literature_code_map.py            # write docs/validation/LITERATURE_CODE_MAP.{md,csv}
    python tools/audit_literature_code_map.py --check    # exit 1 if committed files are stale

Windows / Spyder / Python 3.12; standard library only.
"""
from __future__ import annotations

import argparse
import ast
import csv
import io
import re
import subprocess
import sys
import tokenize
from pathlib import Path

REGISTER = "docs/00_RESEARCH_REFERENCES.md"
MASTER = "LITERATURE/MASTER_LITERATURE_INDEX.csv"
SCAN_DIRS = ("components", "src", "tests")
CODE_DIRS = ("components", "src")
DEFAULT_OUT = "docs/validation"
MD_NAME = "LITERATURE_CODE_MAP.md"
CSV_NAME = "LITERATURE_CODE_MAP.csv"
# The tool's own test names every R-ID on purpose; it is not a citation.
SELF_EXCLUDE = frozenset({"tests/test_literature_code_map.py"})
MAX_BYTES = 2_000_000

ID_RE = re.compile(r"\b(?:R(?:0[1-9]|1[0-3])|L\d{3})\b")
TAG_RE = re.compile(r"\[REF [^\]]+\]")
REGISTER_ROW = re.compile(r"^\|\s*(R(?:0[1-9]|1[0-3]))\s*\|(.*)\|\s*$")
DOI_IN_URL = re.compile(r"https?://(?:dx\.)?doi\.org/([^\s)]+)", re.I)
URL_IN_CELL = re.compile(r"\((https?://[^\s)]+)\)")
AUTHOR_YEAR_HEAD = re.compile(r"^(?P<names>.+?)\s*\((?P<year>(?:19|20)\d{2})\)")
CSV_FIELDS = (
    "reference_id", "series", "doi", "also_listed_as", "link_basis", "status",
    "citing_code_files", "citing_test_files", "match_kinds", "title",
)


def canonical_doi(raw):
    """Return a lower-case DOI without resolver prefix or trailing punctuation.

    [REF LITERATURE/README.md rule 1 (DOI is the canonical identity)]
    """
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", raw.strip(), flags=re.I)
    value = value.rstrip(".,;:]}")
    while value.endswith(")") and value.count(")") > value.count("("):
        value = value[:-1]
    return value.lower()


def load_register(root):
    """Parse R01-R13 rows from the research register table (no network)."""
    text = (root / REGISTER).read_text(encoding="utf-8-sig")
    entries = {}
    for line in text.splitlines():
        match = REGISTER_ROW.match(line)
        if not match:
            continue
        cells = [c.strip() for c in match.group(2).split("|")]
        title = cells[0] if cells else ""
        doi_match = DOI_IN_URL.search(cells[1]) if len(cells) > 1 else None
        url_match = URL_IN_CELL.search(cells[1]) if len(cells) > 1 else None
        entries[match.group(1)] = {
            "id": match.group(1), "series": "REGISTER", "title": title,
            "doi": canonical_doi(doi_match.group(1)) if doi_match else "",
            "url": url_match.group(1) if url_match and not doi_match else "",
        }
    return entries


def load_master(root):
    """Read MASTER_LITERATURE_INDEX.csv rows that carry an ID or DOI."""
    entries = {}
    with (root / MASTER).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            ident = (row.get("ID") or "").strip()
            doi = canonical_doi(row.get("DOI") or "")
            if not ident and not doi:
                continue
            ident = ident or "DOI:" + doi
            entries[ident] = {
                "id": ident, "series": "MASTER", "doi": doi,
                "title": (row.get("Title") or "").strip(),
                "authors": (row.get("Authors") or "").strip(),
                "year": (re.search(r"(?:19|20)\d{2}", row.get("Publication_date_or_status") or "")
                         or [""])[0],
            }
    return entries


def _norm(text):
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def url_pattern(url):
    """Regex for a register Source URL that has a path (a bare host is too generic); else None."""
    bare = re.sub(r"^https?://(?:www\.)?", "", url.strip()).rstrip("/")
    if "/" not in bare:
        return None
    return re.compile(r"(?<![a-z0-9])" + re.escape(bare.lower()) + r"(?![a-z0-9])")


def register_author_year(entry):
    """``(names_text, year, regex)`` from a register title like 'A, B and C (2015), ...'; else None.

    Two or more surnames: first two joined by comma/and/&.  ``X et al.``: needs the year
    within 30 characters after.  A single author is too generic and is not matched.
    """
    head = AUTHOR_YEAR_HEAD.match(entry["title"])
    if not head:
        return None
    names, year = head.group("names"), head.group("year")
    if re.search(r"\bet al\b", names):
        first = re.split(r"\s+et al", names)[0].strip()
        return names, year, re.compile(r"\b" + re.escape(first) + r"\s+et\s+al\.?[^\n]{0,30}?" + year)
    surnames = [n for n in re.split(r",\s*|\s+and\s+|\s*&\s*", names) if n.strip()]
    if len(surnames) < 2:
        return None
    return names, year, re.compile(
        r"\b" + re.escape(surnames[0]) + r"(?:,|\s+and|\s+&)\s+" + re.escape(surnames[1]) + r"\b")


def title_year_author_link(reg, mas):
    """True when a master row is exactly the register source: title contained, same year, first author in names."""
    parsed = register_author_year(reg)
    first = re.sub(r"\s+et al\.?$", "", re.split(r"\s*;\s*", mas.get("authors", ""))[0]).split()
    if not parsed or not first or len(_norm(mas["title"])) < 20:
        return False
    names, year, _ = parsed
    return (year == mas.get("year") and _norm(mas["title"]) in _norm(reg["title"])
            and re.search(r"\b" + re.escape(first[-1]) + r"\b", names) is not None)


def _git_tracked(root):
    """Tracked ``*.py`` paths under SCAN_DIRS, or None when root is not a git work-tree top level."""
    try:
        top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        if Path(top).resolve() != Path(root).resolve():
            return None
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--"] + list(SCAN_DIRS),
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return [p for p in out.decode("utf-8", errors="replace").split("\0") if p.endswith(".py")]


def scan_files(root):
    """Sorted repo-relative ``*.py`` paths under components/, src/ and tests/.

    Uses ``git ls-files`` when ``root`` is a git work tree (untracked scratch files are
    ignored); otherwise walks the filesystem.
    """
    root = Path(root)
    candidates = _git_tracked(root)
    if candidates is None:
        candidates = []
        for name in SCAN_DIRS:
            base = root / name
            if base.is_dir():
                candidates.extend(p.relative_to(root).as_posix() for p in base.rglob("*.py"))
    found = []
    for rel in candidates:
        path = root / rel
        if "__pycache__" in path.parts or rel in SELF_EXCLUDE:
            continue
        if path.is_file() and path.stat().st_size <= MAX_BYTES:
            found.append(rel)
    return sorted(set(found))


def _docstring_and_comment_text(text):
    """Return text of comments and docstrings only (plain literals excluded)."""
    pieces = []
    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node, clean=False)
                if doc:
                    pieces.append(doc)
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                pieces.append(token.string)
    except (SyntaxError, tokenize.TokenError, ValueError):
        pieces = [ln for ln in text.splitlines() if ln.lstrip().startswith("#")]
    return "\n".join(pieces)


def file_ids(text):
    """Return ({ID: kinds}) cited by tag, comment or docstring in one file."""
    found = {}
    for tag in TAG_RE.findall(text):
        for ident in ID_RE.findall(tag):
            found.setdefault(ident, set()).add("REF-tag")
    for ident in ID_RE.findall(_docstring_and_comment_text(text)):
        found.setdefault(ident, set()).add("ID")
    return found


def build_map(root):
    """Return sorted row dicts mapping each reference to citing files."""
    root = Path(root).resolve()
    register = load_register(root)
    master = load_master(root)
    entries = list(register.values()) + list(master.values())
    doi_patterns = {}
    dois = {}
    for entry in entries:
        if entry["doi"]:
            dois.setdefault(entry["doi"], []).append(entry["id"])
            doi_patterns.setdefault(entry["doi"], re.compile(
                r"(?<![a-z0-9])" + re.escape(entry["doi"]) + r"(?![a-z0-9])"))
    # links: id -> {other id: basis}
    links = {e["id"]: {} for e in entries}
    for ids in dois.values():
        for a in ids:
            for b in ids:
                if a != b:
                    links[a][b] = "DOI"
    for reg in register.values():
        for mas in master.values():
            if mas["id"] not in links[reg["id"]] and title_year_author_link(reg, mas):
                links[reg["id"]][mas["id"]] = links[mas["id"]][reg["id"]] = "TITLE_YEAR_AUTHOR"
    text_patterns = []  # (kind, ref id, regex) matched against whole lower/original text
    for reg in register.values():
        pattern = url_pattern(reg["url"]) if reg.get("url") else None
        if pattern:
            text_patterns.append(("URL", reg["id"], pattern, True))
        parsed = register_author_year(reg)
        if parsed:
            text_patterns.append(("AUTHOR-YEAR", reg["id"], parsed[2], False))
    hits = {}  # ref id -> {"code": set, "tests": set, "kinds": set}

    def record(ref, rel, kind):
        for target in (ref, *links.get(ref, {})):
            slot = hits.setdefault(target, {"code": set(), "tests": set(), "kinds": set()})
            slot["code" if rel.split("/", 1)[0] in CODE_DIRS else "tests"].add(rel)
            slot["kinds"].add(kind)

    for rel in scan_files(root):
        text = (root / rel).read_text(encoding="utf-8-sig", errors="replace")
        for ident, kinds in file_ids(text).items():
            for kind in kinds:
                record(ident, rel, kind)
        lowered = text.lower()
        for doi, pattern in doi_patterns.items():
            if doi in lowered and pattern.search(lowered):
                for ident in dois[doi]:
                    record(ident, rel, "DOI")
        for kind, ident, pattern, fold in text_patterns:
            if pattern.search(lowered if fold else text):
                record(ident, rel, kind)
    rows = []
    for entry in entries:
        slot = hits.get(entry["id"], {"code": set(), "tests": set(), "kinds": set()})
        linked = links[entry["id"]]
        status = ("CITED_IN_CODE" if slot["code"] else
                  "CITED_IN_TESTS_ONLY" if slot["tests"] else "UNIMPLEMENTED")
        basis = ("DOI" if "DOI" in linked.values() else
                 "TITLE_YEAR_AUTHOR" if linked else "UNKNOWN")
        rows.append({
            "reference_id": entry["id"], "series": entry["series"],
            "doi": entry["doi"], "also_listed_as": ";".join(sorted(linked)),
            "link_basis": basis, "status": status,
            "citing_code_files": ";".join(sorted(slot["code"])),
            "citing_test_files": ";".join(sorted(slot["tests"])),
            "match_kinds": ";".join(sorted(slot["kinds"])),
            "title": entry["title"],
        })
    rows.sort(key=lambda r: (r["series"] != "REGISTER", r["reference_id"]))
    return rows


def normalise_newlines(data):
    """CRLF -> LF so a Windows (autocrlf) checkout compares equal to the generated bytes."""
    return data.replace(b"\r\n", b"\n")


def render_csv(rows):
    """Deterministic CSV text (LF line endings)."""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _cell(value):
    return (value or "-").replace("|", "\\|").replace(";", "<br>") if value else "-"


def render_markdown(rows):
    """Deterministic Markdown map (no timestamps, no counts that depend on order)."""
    totals = {}
    for row in rows:
        key = (row["series"], row["status"])
        totals[key] = totals.get(key, 0) + 1
    lines = [
        "# Literature-to-code map (generated)",
        "",
        "Generated by `python tools/audit_literature_code_map.py`; do not edit by hand. "
        "Inputs: `docs/00_RESEARCH_REFERENCES.md`, `LITERATURE/MASTER_LITERATURE_INDEX.csv`, "
        "and `*.py` under `components/`, `src/`, `tests/`. No PDF is read.",
        "",
        "**A citation here is provenance only.** `CITED_IN_CODE` does not mean the "
        "source formulation was reproduced, and nothing in this file is `PROJECT_VERIFIED`. "
        "`UNIMPLEMENTED` means no tag, comment, docstring or DOI in those folders cites "
        "the reference; the source may still be a background reference. Citations "
        "that give none of an ID, a DOI, a Source URL with a path or the register author "
        "names are not detected by this map. Match kinds: `REF-tag` "
        "(ID inside a `[REF ...]` tag), `ID` (ID in a comment or docstring), `DOI`, `URL` "
        "(register Source URL), `AUTHOR-YEAR` (register author names). Rows listed in "
        "`Also listed as` are the same source (`DOI` or exact `TITLE_YEAR_AUTHOR` match; "
        "`UNKNOWN` means no exact match was found) and share citations.",
        "",
        "## Totals",
        "",
        "| Series | Status | Count |",
        "|---|---|---|",
    ]
    for (series, status), count in sorted(totals.items()):
        lines.append("| %s | %s | %d |" % (series, status, count))
    for series, heading in (("REGISTER", "Research register R01-R13"),
                            ("MASTER", "Master literature index (ID or DOI)")):
        lines += ["", "## " + heading, "",
                  "| ID | DOI | Status | components/ and src/ | tests/ | Match kinds | Also listed as | Link basis |",
                  "|---|---|---|---|---|---|---|---|"]
        for row in rows:
            if row["series"] == series:
                lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    row["reference_id"], _cell(row["doi"]), row["status"],
                    _cell(row["citing_code_files"]), _cell(row["citing_test_files"]),
                    _cell(row["match_kinds"]), _cell(row["also_listed_as"]), row["link_basis"]))
    lines += ["", "Titles are in the CSV beside this file.", ""]
    return "\n".join(lines)


def write_outputs(root, out_dir):
    """Write MD and CSV to ``out_dir`` (must be inside ``root``); return paths."""
    root = Path(root).resolve()
    out_dir = Path(out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir = out_dir.resolve()
    if out_dir != root and root not in out_dir.parents:
        raise ValueError("output directory must stay inside the repository root")
    rows = build_map(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path, csv_path = out_dir / MD_NAME, out_dir / CSV_NAME
    md_path.write_bytes(render_markdown(rows).encode("utf-8"))
    csv_path.write_bytes(render_csv(rows).encode("utf-8"))
    return md_path, csv_path


def main(argv=None):
    """CLI entry point; ``--check`` compares against committed files."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, default=Path(DEFAULT_OUT))
    parser.add_argument("--check", action="store_true",
                        help="do not write; exit 1 when committed outputs differ")
    options = parser.parse_args(argv)
    root = options.root.resolve()
    if options.check:
        rows = build_map(root)
        out_dir = options.out_dir if options.out_dir.is_absolute() else root / options.out_dir
        stale = []
        for name, text in ((MD_NAME, render_markdown(rows)), (CSV_NAME, render_csv(rows))):
            path = out_dir / name
            if not path.is_file() or normalise_newlines(path.read_bytes()) != normalise_newlines(text.encode("utf-8")):
                stale.append(name)
        print("STALE: " + ", ".join(stale) if stale else "UP_TO_DATE")
        return 1 if stale else 0
    md_path, csv_path = write_outputs(root, options.out_dir)
    print("wrote %s and %s" % (md_path.relative_to(root).as_posix(),
                               csv_path.relative_to(root).as_posix()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
