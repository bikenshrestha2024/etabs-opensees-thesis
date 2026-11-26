"""Extract every normative unit of NBC 105:2025 into a machine-checked register.

[REF NBC105-2025 Clauses 1-10, Annexes A-C (printed pp.1-114); docs/nbc105/NORMATIVE_REGISTER_GUIDE.md]

The standard's text is NOT copied into the repository. A register row stores a
locator (first words of the unit), a SHA-256 of the whitespace-normalised full
unit, structural metadata and the review disposition. Disposition columns are
filled from the human-authored ``DISPOSITION_RULES.csv`` by ``--apply``.

    python tools/nbc105_normative_extract.py --pdf NBC105.pdf --extract
    python tools/nbc105_normative_extract.py --apply
    python tools/nbc105_normative_extract.py --pdf NBC105.pdf --check
    python tools/nbc105_normative_extract.py --summary

Units: none (text processing). Side effects: writes only under
docs/nbc105/normative_register/. Needs poppler ``pdftotext`` for --extract and
--check; --apply and --summary need no PDF. Windows: the executable is looked up
on PATH as ``pdftotext``.

An extracted row set is a *candidate enumeration*: it proves nothing about
engineering compliance and never certifies the standard.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter, OrderedDict
from pathlib import Path

__all__ = [
    "REGISTER_COLUMNS", "KINDS", "DISPOSITIONS", "printed_page_for_pdf_page",
    "extract_units", "extract_from_pdf", "apply_rules", "read_register",
    "write_register", "check_register", "clause_summary_markdown",
    "normalise_text", "unit_sha256",
]

REPO_ROOT = Path(__file__).resolve().parents[1]
REG_DIR = REPO_ROOT / "docs" / "nbc105" / "normative_register"
REGISTER_CSV = REG_DIR / "NORMATIVE_REGISTER.csv"
RULES_CSV = REG_DIR / "DISPOSITION_RULES.csv"
MANIFEST_JSON = REG_DIR / "EXTRACTION_MANIFEST.json"
SUMMARY_MD = REG_DIR / "CLAUSE_SUMMARY.md"

FIRST_BODY_PDF_PAGE = 22          # printed p.1
LAST_BODY_PDF_PAGE = 138          # printed p.114 (end of Annex C)
GROUP_ORDER = [str(i) for i in range(1, 11)] + ["A", "B", "C"]

KINDS = ("SHALL", "SHOULD", "MAY", "LIMIT", "STATEMENT", "CLAUSE", "TABLE",
         "TABLE_ROW", "TABLE_NOTE", "FOOTNOTE", "EQUATION", "FIGURE",
         "DEFINITION")
DISPOSITIONS = ("IMPLEMENTED_AND_TESTED", "IMPLEMENTED_UNTESTED",
                "MANUAL_PROJECT_CHECK", "PROJECT_NOT_APPLICABLE",
                "DEFINITION_ONLY", "EXTERNAL_DATA_REQUIRED", "UNVERIFIED_GAP",
                "DEFERRED_DESIGN_PHASE")
REGISTER_COLUMNS = (
    "id", "clause", "subclause", "printed_page", "kind", "locator", "sha256",
    "topic", "inherited_kind", "disposition", "implementation_ref",
    "test_ref", "evidence_note", "finding", "rule")

# Tables whose body is one hashed unit (row-per-row listing adds no information).
ROW_COLLAPSE_TABLES = ("Table C-1",)

_SHALL = re.compile(
    r"\b(shall not|shall|must not|must|is required|are required|is mandatory|"
    r"are mandatory|mandatory|not permitted|not allowed|required to|is to be|"
    r"are to be|have to|has to|prohibited)\b", re.I)
_SHOULD = re.compile(r"\b(should|recommended|preferably|desirable|advisable)\b", re.I)
_MAY = re.compile(r"\b(may|permitted|permissible|is allowed|are allowed|can be used|can be taken)\b", re.I)
_LIMIT = re.compile(
    r"(to be taken as|shall be taken|taken as|at least|not less than|not exceed|"
    r"not more than|less than|greater than|more than|minimum|maximum|exceed|"
    r"limit|up to|equal to|not be less|not be more|not greater|at most|"
    r"lower of|higher of|lesser of|greater of)", re.I)
_DIGIT = re.compile(r"\d")
_HEADING = re.compile(r"^\s{0,6}(\d{1,2}(?:\.\d{1,2}){0,5})\.?(\s{1,10})(\S.*)$")
_ANNEX_START = re.compile(r"^\s*ANNEX\s+([ABC])\s*:")
_TABLE_TITLE = re.compile(r"^\s*(Table\s+[A-C0-9]+[.-][0-9A-Z]+)\b[:.]?\s*(.*)$", re.I)
_FIGURE_TITLE = re.compile(r"^\s*(Figure\s+[A-C0-9]+[.-][0-9A-Z]+)\b[:.]?\s*(.*)$", re.I)
_LISTMARK = re.compile(
    r"^\s*(\(?[a-z]\)|\([a-z]\)|\([ivx]{1,4}\)|[ivx]{1,4}\)|\(\d{1,2}\)|\d{1,2}\)|"
    r"[a-z]\.|[ivx]{1,4}\.|[•·▪–—-])\s+\S")
_PAGE_NO = re.compile(r"^\s*\d{1,3}\s*$")
_EQ_LABEL = re.compile(r"(?:Eq\.?\s*)?\(?(?<!\d)(\d{1,2}(?:\.\d{1,2}){0,3}\s*\(\d{1,2}[a-z]?\))")
_SPLIT = re.compile(r"(?<=[.;?!])\s+(?=[A-Z(•\"'])")
_ABBREV = ("e.g.", "i.e.", "etc.", "Fig.", "fig.", "No.", "no.", "Sec.", "Cl.",
           "cl.", "Eq.", "eq.", "viz.", "vs.", "Ref.", "Art.", "approx.", "Max.",
           "Min.", "max.", "min.", "Sr.", "S.N.", "Dr.", "i.e", "e.g", "al.")


def normalise_text(text: str) -> str:
    """Whitespace/Unicode-normalised form used for hashing. [REF NBC105-2025 register]"""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("­", "").replace("​", "")
    return re.sub(r"\s+", " ", text).strip()


def unit_sha256(text: str) -> str:
    """SHA-256 hex of the normalised unit. [REF NBC105-2025 register]"""
    return hashlib.sha256(normalise_text(text).encode("utf-8")).hexdigest()


def printed_page_for_pdf_page(pdf_page: int) -> int:
    """Printed page for a 1-based PDF page. [REF NBC105-2025 printed pagination]

    Printed N = PDF N-21 up to PDF 47 (printed p.26), PDF 48-49 are the Figure 4-3
    map insert plus the second printed p.26 sheet, PDF N-23 from printed p.27 on."""
    if pdf_page < FIRST_BODY_PDF_PAGE:
        raise ValueError("front matter has no printed body page")
    if pdf_page <= 47:
        return pdf_page - 21
    if pdf_page in (48, 49):      # Figure 4-3 map insert; text footer reads 25 / 26
        return 26
    return pdf_page - 23


def _is_garbled(ch: str) -> bool:
    o = ord(ch)
    if o < 0x100:
        return False
    if 0x380 <= o <= 0x3FF or 0x2000 <= o <= 0x22FF or 0xFB00 <= o <= 0xFB4F:
        return False
    if 0x2300 <= o <= 0x23FF or 0x2500 <= o <= 0x25FF:
        return False
    return True


def _garble_count(s: str) -> int:
    return sum(1 for c in s if _is_garbled(c))


def _clean_lines(page_text: str):
    lines = [ln.rstrip() for ln in page_text.replace("\r", "").split("\n")]
    while lines and not lines[-1].strip():
        lines.pop()
    footer = None
    if lines and _PAGE_NO.match(lines[-1]):
        footer = int(lines.pop().strip())
    return lines, footer


def _sentences(par: str):
    par = normalise_text(par)
    if not par:
        return []
    protected = par
    for ab in _ABBREV:
        protected = protected.replace(ab, ab.replace(".", "․"))
    protected = re.sub(r"(?<=\b[A-Z])\.(?=\s*[A-Z]\b)", "․", protected)
    parts = _SPLIT.split(protected)
    return [p.replace("․", ".").strip() for p in parts if p.strip()]


def _classify(sentence: str):
    if _SHALL.search(sentence):
        return "SHALL"
    if _SHOULD.search(sentence):
        return "SHOULD"
    if _MAY.search(sentence):
        return "MAY"
    if _LIMIT.search(sentence) and _DIGIT.search(sentence):
        return "LIMIT"
    if re.search(r"=|\d\s*(%|percent|mm|m\b|kN|MPa|N/mm|s\b|Hz)", sentence):
        return "STATEMENT"
    return None


def _locator(text: str, n: int = 12) -> str:
    words = normalise_text(text).split(" ")
    return " ".join(words[:n])


class _Builder:
    def __init__(self):
        self.rows = []
        self.counters = Counter()
        self.group = "1"
        self.sub = "1"
        self.topic = ""
        self.section_kind = None  # DEFINITIONS / NOTATIONS context
        self.table = None
        self.last_kind = None      # kind of the previous sentence (lead-in inheritance)
        self.lead_kind = None
        self.warnings = []
        self.expect_note = False
        self.last_note = None
        self.after_table = False
        self.table_sub = "1"

    def sub_id(self, num: str) -> str:
        return num if self.group.isdigit() else f"{self.group}.{num}"

    def add(self, kind, text, page, inherited="N", locator=None, sub=None, topic=None):
        g = self.group
        self.counters[g] += 1
        self.rows.append(OrderedDict(
            id=f"N{g}-{self.counters[g]:04d}", clause=g,
            subclause=sub or self.sub, printed_page=page, kind=kind,
            locator=locator or _locator(text), sha256=unit_sha256(text),
            topic=topic if topic is not None else self.topic,
            inherited_kind=inherited, disposition="", implementation_ref="",
            test_ref="", evidence_note="", finding="", rule=""))


def _flush_paragraph(b, lines, page):
    """Turn a prose paragraph (list of raw lines) into register rows."""
    if not lines:
        return
    segs = []                       # split prose from equation (glyph-garbled) runs
    for ln in lines:
        g = _garble_count(ln) >= 2
        if segs and segs[-1][0] == g:
            segs[-1][1].append(ln)
        else:
            segs.append((g, [ln]))
    if len(segs) > 1:
        for g, ls in segs:
            if g:
                b.after_table = False
                _equation(b, normalise_text(" ".join(ls)), page)
            else:
                _flush_paragraph(b, ls, page)
        return
    joined = normalise_text(" ".join(x.strip() for x in lines))
    if b.expect_note or (b.after_table and re.match(r"^(Notes?\b|[*\u2020]|\d\s)", joined)):
        kind = "TABLE_NOTE" if re.match(r"^Notes?\b", joined) else "FOOTNOTE"
        b.add(kind, joined, page, sub=b.table_sub)
        b.last_note = (kind, joined, page)
        b.expect_note = False
        return
    if b.after_table and b.last_note and joined[:1].islower():
        kind, prev, pg = b.last_note          # footnote text continued after a blank line
        b.rows.pop(); b.counters[b.group] -= 1
        b.add(kind, prev + " " + joined, pg, sub=b.table_sub)
        b.last_note = (kind, prev + " " + joined, pg)
        return
    b.last_note = None
    b.after_table = False
    if b.section_kind == "DEFINITIONS":
        b.add("DEFINITION", joined, page)
        return
    # split paragraph at list markers; keep lead-in
    items, cur = [], []
    for ln in lines:
        if _LISTMARK.match(ln) and cur:
            items.append((" ".join(cur), False))
            cur = [ln.strip()]
        else:
            cur.append(ln.strip())
    if cur:
        items.append((" ".join(cur), False))
    first = True
    for item, _ in items:
        is_item = bool(_LISTMARK.match(item)) and not first
        first = False
        text = normalise_text(item)
        if _garble_count(text) >= 3 and _garble_count(text) > len(text) * 0.15:
            _equation(b, text, page)
            continue
        for sent in _sentences(text):
            if _garble_count(sent) >= 3:
                _equation(b, sent, page)
                continue
            if re.search(r"[\u2026.]{4,}\s*\d{1,2}(?:\.\d{1,2})*\s*\(\d+\)", sent):
                _equation(b, sent, page)
                continue
            kind = _classify(sent)
            inherited = "N"
            if kind is None and is_item and b.lead_kind:
                kind, inherited = b.lead_kind, "Y"
            if kind is None and len(sent.split()) >= 4:
                kind = "STATEMENT"   # explanatory / unclassified prose stays visible
            if kind is None:
                b.last_kind = None
                continue
            if sent.rstrip().endswith(":"):
                b.lead_kind = kind
            elif not is_item:
                b.lead_kind = None
            b.add(kind, sent, page, inherited)


def _equation(b, text, page):
    found = _EQ_LABEL.findall(text)
    label = re.match(r'(.*)', found[-1]) if found else None
    loc = (f"Equation {re.sub(r'\\s+', '', label.group(1))}" if label
           else f"Equation block near {b.sub}")
    b.add("EQUATION", re.sub(r"\s+", "", text), page, locator=loc)


def _table_rows(b, table_name, body_lines, page):
    """Emit TABLE_ROW rows for the logical rows of a table body."""
    if table_name in ROW_COLLAPSE_TABLES:
        return
    rows, cur = [], []
    for ln in body_lines:
        s = ln.strip()
        if not s:
            continue
        starts = bool(re.match(r"^\d{1,3}\s{2,}\S", ln.strip() and ln.strip() + "  x")) \
            or bool(re.search(r"\S\s{2,}\S", ln)) or bool(re.match(r"^\s{0,3}\d{1,3}\s{2,}", ln))
        # a row starts when the line has >=2 cells; a wrapped-cell line has one fragment
        if starts:
            if cur:
                rows.append(cur)
            cur = [s]
        else:
            if cur:
                cur.append(s)
            else:
                cur = [s]
    if cur:
        rows.append(cur)
    for r in rows:
        text = normalise_text(" ".join(r))
        if len(text) < 2:
            continue
        b.add("TABLE_ROW", f"{table_name} | {text}", page,
              locator=f"{table_name}: {_locator(text, 9)}")


def extract_units(page_texts, first_pdf_page=FIRST_BODY_PDF_PAGE, start_group="1"):
    """Extract normative units from a list of per-page ``pdftotext -layout`` strings.

    [REF NBC105-2025 Clauses 1-10, Annexes A-C]
    ``page_texts[0]`` is PDF page ``first_pdf_page``. Returns ``(rows, info)``.
    Deterministic: depends only on the text. Pure function (no I/O).
    """
    b = _Builder()
    b.group = start_group
    b.sub = start_group
    info = {"footer_mismatch": [], "pages": len(page_texts), "headings": [],
            "tables": [], "figures": []}
    para, para_page = [], None
    table = None  # dict(name, lines, page, blank_run)
    pending_note = None

    def flush_para():
        nonlocal para, para_page
        if para:
            _flush_paragraph(b, para, para_page)
        para, para_page = [], None

    table_page_holder = [1]

    def close_table():
        nonlocal table
        if table is None:
            return
        table_page_holder[0] = table["page"]
        tail = _split_table_tail(table)
        body = table["lines"]
        text = " ".join(x.strip() for x in body if x.strip())
        b.add("TABLE", f"{table['name']} {table['title']} | {text}", table["page"],
              locator=f"{table['name']} {_locator(table['title'], 8)}".strip(),
              sub=table["sub"])
        info["tables"].append({"name": table["name"], "rows": 0})
        if table["name"] in ROW_COLLAPSE_TABLES:
            n = sum(1 for x in body if re.match(r"^\s*\d{1,4}\s{2,}\S", x))
            info["tables"][-1]["rows"] = n
            b.rows[-1]["locator"] += f" [{n} data rows hashed as one unit]"
        _table_rows(b, table["name"], body, table["page"])
        b.table_sub = table["sub"]
        b.after_table = True
        table = None
        if tail:
            if re.match(r"^\s*[\d*\u2020]\s*$", tail[0]) and len(tail) == 1:
                b.expect_note = True
            else:
                _flush_paragraph(b, tail, table_page_holder[0])

    for offset, raw in enumerate(page_texts):
        pdf_page = first_pdf_page + offset
        printed = printed_page_for_pdf_page(pdf_page)
        lines, footer = _clean_lines(raw)
        if footer is not None and footer != printed and pdf_page != 48:
            info["footer_mismatch"].append((pdf_page, printed, footer))
        blank_run = 0
        for ln in lines:
            s = ln.strip()
            if not s:
                blank_run += 1
                if table is not None:
                    table["blank"] = table.get("blank", 0) + 1
                    table["lines"].append("")
                if table is None:
                    flush_para()
                continue
            blank_run = 0
            m = _ANNEX_START.match(ln)
            if m:
                close_table(); flush_para()
                b.group = m.group(1)
                b.sub = f"{b.group}"
                b.topic = s.split(":", 1)[1].strip().title() if ":" in s else s
                continue
            if re.match(r"^\s*PART\s+\d+\b", ln) and s == s.upper():
                continue
            if b.group == "C" and table is None and re.match(r"^\s*SN\s+District\b", ln):
                flush_para()
                table = {"name": "Table C-1", "title": "Seismic zoning factor by local unit (title not printed)",
                         "lines": [], "page": printed, "sub": "C", "blank": 0}
                continue
            tm = _TABLE_TITLE.match(ln)
            if tm and (ln.startswith(" ") or True) and len(s) < 120:
                close_table(); flush_para()
                name = re.sub(r"\s+", " ", tm.group(1)).replace("TABLE", "Table")
                table = {"name": name, "title": tm.group(2).strip(), "lines": [],
                         "page": printed, "sub": b.sub, "blank": 0}
                continue
            fm = _FIGURE_TITLE.match(ln)
            if fm and len(s) < 140:
                close_table(); flush_para()
                title = fm.group(2).strip()
                b.add("FIGURE", f"{fm.group(1)} {title}", printed,
                      locator=f"{fm.group(1)} {_locator(title, 8)}".strip())
                info["figures"].append(fm.group(1))
                continue
            hm = _HEADING.match(ln)
            if hm and _plausible_heading(b, hm, ln):
                close_table(); flush_para()
                num, title = hm.group(1), hm.group(3).strip()
                if b.group.isdigit() and num.split(".")[0] != b.group:
                    b.group = num.split(".")[0]
                b.sub = b.sub_id(num)
                b.topic = title.rstrip(":").strip()
                up = title.upper()
                b.section_kind = ("DEFINITIONS" if up.startswith("DEFINITION") else
                                  "NOTATIONS" if up.startswith("NOTATION") else None)
                b.lead_kind = None
                b.add("CLAUSE", f"{b.sub} {title}", printed, locator=f"{b.sub} {_locator(title, 10)}")
                info["headings"].append(b.sub)
                continue
            if table is not None:
                if _table_continues(table, ln):
                    table["lines"].append(ln)
                    continue
                # table ended: following lone digits / Note are table notes
                close_table()
            if b.section_kind == "NOTATIONS" and re.match(r"^\s{0,12}\S+\s{2,}\S", ln):
                flush_para()
                b.add("DEFINITION", s, printed, locator=_locator(s, 10))
                continue
            if para_page is None:
                para_page = printed
            para.append(ln)
    close_table(); flush_para()
    return b.rows, {**info, "warnings": b.warnings}


def _plausible_heading(b, hm, line):
    num = hm.group(1)
    title = hm.group(3)
    if b.group.isdigit() and "." not in num and len(hm.group(2)) > 4:
        return False
    if re.search(r"\s{3,}\S+\s*$", line) and re.search(r"\d\s*$", line):
        return False
    if len(title) > 110 or not title[0].isalpha() or not title[0].isupper():
        return False
    if re.search(r"[.,;]\s*$", title) and not title.isupper():
        return False
    parts = num.split(".")
    if b.group.isdigit():
        top = int(parts[0])
        if top > 10 or top < 1:
            return False
        if top != int(b.group) and top not in (int(b.group), int(b.group) + 1):
            return False
        if top != int(b.group) and len(parts) != 1:
            return False
        if len(parts) > 1 and int(parts[1]) > 12 and top != 5:
            return False
        if len(parts) == 1 and not (title.upper() == title or title[:1].isupper()):
            return False
    else:
        if int(parts[0]) > 12:
            return False
        if len(parts) == 1 and len(title.split()) > 8:
            return False
    if len(title.split()) > 14:
        return False
    return True


def _table_continues(table, ln):
    s = ln.strip()
    indent = len(ln) - len(ln.lstrip())
    multi = bool(re.search(r"\S\s{2,}\S", ln))
    if multi or indent >= 8:
        return True
    if len(s) <= 6:
        return True
    # one-fragment wrapped cell: stays in table until a blank line followed by prose
    if table["lines"] and table["lines"][-1].strip() == "":
        return False
    return len(s) < 38 and table["blank"] == 0


def _split_table_tail(table):
    """Remove and return note lines at the end of a table body.

    A note block starts with a lone footnote marker (digit, * or dagger) on its
    own line, or the word Note(s), and contains no multi-column lines.
    [REF NBC105-2025 table notes]"""
    lines = table["lines"]
    while lines and not lines[-1].strip():
        lines.pop()
    for i in range(len(lines) - 1, 0, -1):
        s = lines[i].strip()
        if not s:
            continue
        if re.search(r"\S\s{2,}\S", lines[i]) and not re.match(r"^Notes?\b", s):
            break
        if re.match(r"^([\d*\u2020]|Notes?\b.*)$", s) or re.match(r"^[\d*\u2020]\s+[A-Za-z]", s):
            tail = [x.strip() for x in lines[i:] if x.strip()]
            if all(not re.search(r"\S\s{2,}\S", x) for x in lines[i + 1:] if x.strip()):
                del lines[i:]
                return tail
            break
    return []


def extract_from_pdf(pdf_path):
    """Run ``pdftotext -layout`` on the PDF and extract units. [REF NBC105-2025 register]"""
    out = subprocess.run(
        ["pdftotext", "-layout", "-f", str(FIRST_BODY_PDF_PAGE), "-l",
         str(LAST_BODY_PDF_PAGE), str(pdf_path), "-"],
        check=True, capture_output=True).stdout.decode("utf-8", "replace")
    pages = out.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return extract_units(pages)


# --------------------------------------------------------------------------
# register I/O, rule application, check, summary
# --------------------------------------------------------------------------
RULE_COLUMNS = ("selector", "kind_filter", "disposition", "implementation_ref",
                "test_ref", "evidence_note", "finding")


def read_register(path=REGISTER_CSV):
    """Read the register CSV into a list of dicts. [REF NBC105-2025 register]"""
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_register(rows, path=REGISTER_CSV):
    """Write the register with LF line endings, fixed column order. [REF NBC105-2025 register]"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=REGISTER_COLUMNS, lineterminator="\n",
                       extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in REGISTER_COLUMNS})
    Path(path).write_bytes(buf.getvalue().encode("utf-8"))


def _sub_key(sub):
    return tuple(sub.replace(".", " ").split())


def _id_key(rid):
    c, n = rid[1:].split("-")
    return (GROUP_ORDER.index(c), int(n))


def _rule_matches(sel, row):
    kind, _, val = sel.partition(":")
    if kind == "id":
        if ".." in val:
            lo, hi = val.split("..")
            return _id_key(lo) <= _id_key(row["id"]) <= _id_key(hi)
        return row["id"] == val
    if kind == "table":
        return (row["kind"] in ("TABLE", "TABLE_ROW", "TABLE_NOTE", "FOOTNOTE")
                and (row["locator"].startswith(val + ":") or row["locator"].startswith(val + " ")
                     or row["locator"].startswith(val + "]")
                     or row.get("_table") == val))
    if kind == "sub":
        rs, vs = _sub_key(row["subclause"]), _sub_key(val)
        return rs[:len(vs)] == vs
    if kind == "loc":      # loc:<clause>|<locator prefix>  (stable against re-numbering of ids)
        clause, _, prefix = val.partition("|")
        return row["clause"] == clause and row["locator"].startswith(prefix)
    if kind == "kind":     # kind:CLAUSE  (all rows of a kind)
        return row["kind"] == val
    return False


def _specificity(sel, rule):
    kind, _, val = sel.partition(":")
    base = {"id": 4000, "kind": 3500, "loc": 3000, "table": 2000, "sub": 1000}[kind]
    if kind == "sub":
        base += len(_sub_key(val)) * 10
    if kind == "id" and ".." in val:
        base -= 500
    return base + (5 if rule["kind_filter"] else 0)


def read_rules(path=RULES_CSV):
    """Read the human-authored disposition rules. [REF NBC105-2025 register]"""
    with open(path, newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r.get("selector", "").strip()]


def apply_rules(rows, rules):
    """Fill disposition columns; the most specific matching rule wins.

    [REF NBC105-2025 register] Rows with no matching rule keep blank
    dispositions and therefore stay 'unreviewed' for the gate. Returns the
    number of rows that received a rule."""
    # annotate table membership for rows that follow a TABLE row (notes)
    cur = None
    for r in rows:
        if r["kind"] == "TABLE":
            cur = r["locator"].split(" ")[0] + " " + r["locator"].split(" ")[1] \
                if r["locator"].startswith("Table ") else None
        elif r["kind"] in ("TABLE_ROW",):
            pass
        elif r["kind"] in ("TABLE_NOTE", "FOOTNOTE") and cur:
            r["_table"] = cur
        else:
            cur = None
    n = 0
    for r in rows:
        best, bs = None, -1
        for i, rule in enumerate(rules):
            if rule["kind_filter"] and r["kind"] not in rule["kind_filter"].split("|"):
                continue
            if not _rule_matches(rule["selector"], r):
                continue
            sp = _specificity(rule["selector"], rule) * 1000 + i
            if sp > bs:
                best, bs = (i, rule), sp
        for c in ("disposition", "implementation_ref", "test_ref", "evidence_note",
                  "finding", "rule"):
            r[c] = ""
        if best:
            i, rule = best
            r["disposition"] = rule["disposition"].strip()
            r["implementation_ref"] = rule["implementation_ref"].strip()
            r["test_ref"] = rule["test_ref"].strip()
            r["evidence_note"] = rule["evidence_note"].strip()
            r["finding"] = rule["finding"].strip()
            r["rule"] = f"R{i + 2:03d}:{rule['selector']}"
            n += 1
        r.pop("_table", None)
    return n


def check_register(register_rows, fresh_rows):
    """Compare a stored register with a fresh extraction. [REF NBC105-2025 register]

    Returns a dict with unreviewed/gap counts and hash drift lists."""
    stored = {r["id"]: r for r in register_rows}
    fresh = {r["id"]: r for r in fresh_rows} if fresh_rows is not None else None
    rep = {
        "rows": len(register_rows),
        "unreviewed": [r["id"] for r in register_rows if not r["disposition"].strip()],
        "invalid_disposition": [r["id"] for r in register_rows
                                if r["disposition"].strip() and r["disposition"] not in DISPOSITIONS],
        "unverified_gap": [r["id"] for r in register_rows if r["disposition"] == "UNVERIFIED_GAP"],
        "drift_changed": [], "drift_missing_in_pdf": [], "drift_new_in_pdf": [],
        "pdf_compared": fresh is not None,
    }
    if fresh is not None:
        for rid, r in stored.items():
            f = fresh.get(rid)
            if f is None:
                rep["drift_missing_in_pdf"].append(rid)
            elif f["sha256"] != r["sha256"]:
                rep["drift_changed"].append(rid)
        rep["drift_new_in_pdf"] = [rid for rid in fresh if rid not in stored]
    rep["ok"] = not (rep["unreviewed"] or rep["invalid_disposition"] or rep["drift_changed"]
                     or rep["drift_missing_in_pdf"] or rep["drift_new_in_pdf"])
    return rep


def clause_summary_markdown(rows, findings_by_clause=None, gaps_note=""):
    """Per-clause summary (counts by disposition, findings, open gaps). [REF NBC105-2025 register]

    Generated text only; no standard text. Never states certification."""
    lines = ["# NBC 105:2025 normative register: clause summary", "",
             "Generated by `tools/nbc105_normative_extract.py --summary`. Do not edit by hand.",
             "Status: NOT CERTIFIED. Independent human sign-off is an external gate; "
             "a disposition is a source-to-code review note, not engineering acceptance.", ""]
    disp = list(DISPOSITIONS) + ["(blank)"]
    hdr = "| Clause | Rows | " + " | ".join(d.replace("_", " ").title() if d != "(blank)" else "Unreviewed" for d in disp) + " |"
    lines += [hdr, "|" + "---|" * (len(disp) + 2)]
    tot = Counter()
    for g in GROUP_ORDER:
        sub = [r for r in rows if r["clause"] == g]
        c = Counter(r["disposition"] or "(blank)" for r in sub)
        tot.update(c)
        lines.append(f"| {g} | {len(sub)} | " + " | ".join(str(c.get(d, 0)) for d in disp) + " |")
    lines.append(f"| all | {len(rows)} | " + " | ".join(str(tot.get(d, 0)) for d in disp) + " |")
    lines += ["", "## Rows by kind", ""]
    kc = Counter(r["kind"] for r in rows)
    lines.append(", ".join(f"{k}: {kc[k]}" for k in KINDS if kc[k]))
    lines += ["", "## Findings (code versus printed standard)", ""]
    seen = OrderedDict()
    for r in rows:
        if r["finding"].strip():
            seen.setdefault(r["finding"].strip(), []).append(r["id"])
    if not seen:
        lines.append("None recorded.")
    for f, ids in seen.items():
        lines.append(f"- {f} (rows: {', '.join(ids[:6])}{' ...' if len(ids) > 6 else ''}; {len(ids)} row(s))")
    lines += ["", "## Open gaps (UNVERIFIED_GAP rows)", ""]
    gaps = [r for r in rows if r["disposition"] == "UNVERIFIED_GAP"]
    if not gaps:
        lines.append("No UNVERIFIED_GAP rows.")
    by = OrderedDict()
    for r in gaps:
        by.setdefault((r["clause"], r["subclause"], r["evidence_note"]), []).append(r["id"])
    for (cl, sc, note), ids in by.items():
        lines.append(f"- {sc}: {len(ids)} row(s) ({ids[0]}..{ids[-1]}). {note}")
    if gaps_note:
        lines += ["", gaps_note]
    return "\n".join(lines) + "\n"


def _merge_for_extract(fresh_rows, old_rows):
    """Keep dispositions of old rows whose (clause, sha256) is unchanged (id order kept)."""
    for r in fresh_rows:
        for c in ("disposition", "implementation_ref", "test_ref", "evidence_note",
                  "finding", "rule"):
            r[c] = ""
    return fresh_rows


def main(argv=None):
    """CLI. [REF NBC105-2025 register]"""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pdf", help="path to the NBC 105:2025 PDF (not stored in the repo)")
    ap.add_argument("--extract", action="store_true", help="write register (blank dispositions) + manifest, then apply rules if present")
    ap.add_argument("--apply", action="store_true", help="apply DISPOSITION_RULES.csv to the stored register")
    ap.add_argument("--check", action="store_true", help="report unreviewed rows and hash drift")
    ap.add_argument("--summary", action="store_true", help="regenerate CLAUSE_SUMMARY.md")
    a = ap.parse_args(argv)
    if a.extract:
        if not a.pdf:
            ap.error("--extract needs --pdf")
        rows, info = extract_from_pdf(a.pdf)
        pdf_sha = hashlib.sha256(Path(a.pdf).read_bytes()).hexdigest()
        if RULES_CSV.exists():
            apply_rules(rows, read_rules())
        write_register(rows)
        ver = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True)
        manifest = OrderedDict(
            standard="NBC 105:2025", pdf_sha256=pdf_sha,
            extractor_note="pdftotext -layout; hashes may drift with a different poppler version",
            poppler=(ver.stderr or ver.stdout).splitlines()[0] if (ver.stderr or ver.stdout) else "unknown",
            rows=len(rows), by_clause=OrderedDict((g, sum(1 for r in rows if r["clause"] == g)) for g in GROUP_ORDER),
            by_kind=dict(sorted(Counter(r["kind"] for r in rows).items())),
            footer_page_mismatches=len(info["footer_mismatch"]),
            tables=len(info["tables"]), figures=len(info["figures"]))
        MANIFEST_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, indent=2))
        return 0
    if a.apply:
        rows = read_register()
        n = apply_rules(rows, read_rules())
        write_register(rows)
        print(f"rules applied to {n} of {len(rows)} rows")
        return 0
    if a.summary:
        rows = read_register()
        SUMMARY_MD.write_text(clause_summary_markdown(rows), encoding="utf-8", newline="\n")
        print("wrote", SUMMARY_MD)
        return 0
    if a.check:
        rows = read_register()
        fresh = extract_from_pdf(a.pdf)[0] if a.pdf else None
        rep = check_register(rows, fresh)
        print(json.dumps({k: (v if not isinstance(v, list) else {"count": len(v), "first": v[:10]})
                          for k, v in rep.items()}, indent=2))
        return 0 if rep["ok"] else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
