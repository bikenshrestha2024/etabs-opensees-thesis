"""Audit the cross-references printed inside NBC 105:2025.

[REF NBC105-2025 Clauses 1-10, Annexes A-C (printed pp.1-114); docs/nbc105/CROSS_REFERENCE_REGISTER.md]

Every "clause X", "section X", "Table X", "Figure X", "Equation X" and "Annex X"
that the standard prints inside its own text is a cross-reference. Some of them
point at the wrong target (a drift limit sent to 5.6 Accidental Eccentricity, a
map called Figure 4-4 that is Figure 4-3). The reviewed classification lives in
``docs/nbc105/CROSS_REFERENCE_REGISTER.csv``:

    VALID                               the printed target is the right one
    MISDIRECTED_CORRECT_TARGET_IS_X     wrong target; X (column correct_target) is right
    AMBIGUOUS                           more than one reading; both targets are stated

The standard's text is not copied: a row stores the matched phrase, a short
locator and the SHA-256 of the whole printed line.

    python tools/nbc105_crossref_audit.py --check
    python tools/nbc105_crossref_audit.py --check --pdf NBC105.pdf     # also re-extract
    python tools/nbc105_crossref_audit.py --extract --pdf NBC105.pdf   # list references
    python tools/nbc105_crossref_audit.py --markdown                   # rewrite the .md

--check needs no PDF (CSV integrity, target existence in the normative register,
corrected citations in code and docs, stale-citation scan). With --pdf it also
fails on any printed reference that is not classified in the CSV. Needs poppler
``pdftotext`` on PATH only for --pdf/--extract. Windows/Spyder compatible.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "nbc105"
CROSSREF_CSV = DOCS / "CROSS_REFERENCE_REGISTER.csv"
CROSSREF_MD = DOCS / "CROSS_REFERENCE_REGISTER.md"
REGISTER_CSV = DOCS / "normative_register" / "NORMATIVE_REGISTER.csv"

CLASS_VALID = "VALID"
CLASS_MISDIRECTED = "MISDIRECTED_CORRECT_TARGET_IS_X"
CLASS_AMBIGUOUS = "AMBIGUOUS"
CLASSES = (CLASS_VALID, CLASS_MISDIRECTED, CLASS_AMBIGUOUS)
UNCLASSIFIED = "UNCLASSIFIED"

COLUMNS = ("ref_id", "printed_page", "pdf_page", "context", "reference_text", "target",
           "classification", "correct_target", "rationale", "citation_files",
           "corrected_citation", "line_sha256", "locator")

_KEYWORD = (r"(?P<kw>clauses?|sub-?clauses?|sections?|tables?|figures?|equations?|eq\.|"
            r"annex(?:es)?|chapter)")
_NUMBER = r"[A-C]?-?\d+(?:[.\-]\d+)*(?:\s?\([0-9a-z]+\))?"
_REF = re.compile(
    r"(?i)\b" + _KEYWORD + r"\s*\(?(?P<num>" + _NUMBER + r"|[A-C]\b)"
    r"(?P<more>(?:\s*(?:,|and|&)\s*\(?" + _NUMBER + r")*)")
_HEADING = re.compile(r"^\s{0,12}(\d+(?:\.\d+){0,4})\s{1,8}[A-Za-z]")
_ANNEX_HEADING = re.compile(r"^\s*ANNEX\s+([A-C])\b")


def _load_extractor():
    spec = importlib.util.spec_from_file_location(
        "nbc105_normative_extract", ROOT / "tools" / "nbc105_normative_extract.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _normalise_target(kw: str, num: str) -> str:
    """Canonical target text: 'Table 4-1', 'Figure 4-4', 'Equation 3.6.3', 'Annex C', '5.6'."""
    kw = kw.lower().rstrip("s") if kw.lower() not in ("eq.",) else "eq."
    num = re.sub(r"\s+", "", num).rstrip(".")
    if kw in ("table", "figure"):
        base = re.sub(r"\([0-9a-z]+\)$", "", num)
        return f"{kw.capitalize()} " + base.replace(".", "-", 1) if "-" not in base else f"{kw.capitalize()} {base}"
    if kw in ("equation", "eq."):
        return "Equation " + num
    if kw.startswith("annex"):
        return "Annex " + num.upper()
    return re.sub(r"\([0-9a-z]+\)$", "", num)      # "5.1 (4)" -> clause 5.1 (the item is not a target)


def _line_is_caption(stripped: str, match_start: int, kw: str) -> bool:
    return match_start == 0 and kw.lower().startswith(("table", "figure"))


def extract_references(page_texts, first_pdf_page=None):
    """Return the raw printed references found in per-page ``pdftotext -layout`` text.

    [REF NBC105-2025 cross-references]
    Each item: pdf_page, context (nearest preceding heading, annex-prefixed), reference_text,
    target, line_sha256, locator. Caption lines ("Table 4-1 ...") are not references.
    """
    ext = _load_extractor()
    first = first_pdf_page or ext.FIRST_BODY_PDF_PAGE
    out, seen = [], set()
    context, annex = "", ""
    for offset, page in enumerate(page_texts):
        pdf_page = first + offset
        for raw in page.split("\n"):
            line = raw.rstrip()
            stripped = line.strip()
            if not stripped:
                continue
            ah = _ANNEX_HEADING.match(stripped)
            if ah:
                annex, context = ah.group(1), "Annex " + ah.group(1)
                continue
            h = _HEADING.match(line)
            if h and not re.search(_REF, stripped[: h.end()]):
                context = (annex + "." if annex else "") + h.group(1)
            for m in _REF.finditer(stripped):
                if _line_is_caption(stripped, m.start(), m.group("kw")):
                    continue
                nums = [m.group("num")] + re.findall(_NUMBER, m.group("more") or "")
                for num in nums:
                    target = _normalise_target(m.group("kw"), num)
                    sha = hashlib.sha256(" ".join(stripped.split()).encode("utf-8")).hexdigest()
                    key = (pdf_page, target, sha)
                    if key in seen:
                        continue
                    seen.add(key)
                    words = stripped[: m.end()].split()
                    out.append(dict(pdf_page=pdf_page, context=context,
                                    reference_text=f"{m.group('kw')} {num}".strip(),
                                    target=target, line_sha256=sha,
                                    locator=" ".join(words[-8:])))
    return out


def extract_from_pdf(pdf_path):
    """Run pdftotext -layout over the body pages and extract references. [REF NBC105-2025 cross-references]"""
    ext = _load_extractor()
    raw = subprocess.run(
        ["pdftotext", "-layout", "-f", str(ext.FIRST_BODY_PDF_PAGE), "-l",
         str(ext.LAST_BODY_PDF_PAGE), str(pdf_path), "-"],
        check=True, capture_output=True).stdout.decode("utf-8", "replace")
    pages = raw.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    refs = extract_references(pages)
    for r in refs:
        r["printed_page"] = ext.printed_page_for_pdf_page(r["pdf_page"])
    return refs


def read_crossrefs(path=CROSSREF_CSV):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_crossrefs(rows, path=CROSSREF_CSV):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLUMNS})


def _key(row):
    return (int(row["pdf_page"]), row["target"], row["line_sha256"])


def unclassified_references(extracted, classified_rows):
    """Printed references with no classified row in the CSV (the audit's failure list).

    [REF NBC105-2025 cross-references]
    """
    done = {_key(r) for r in classified_rows if r["classification"] in CLASSES}
    return [r for r in extracted if _key(r) not in done]


def _register_targets():
    """Targets that exist in the normative register: clauses (with annex prefix), tables, figures, equations."""
    clauses, named = set(), set()
    with open(REGISTER_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            clauses.add(r["subclause"])
            m = re.match(r"(Table|Figure)\s+([A-C]?-?\d+(?:[-.]\d+)*)", r["locator"])
            if m:
                named.add(f"{m.group(1)} {m.group(2).replace('.', '-')}")
            e = re.match(r"Equation\s+(\S+)", r["locator"])
            if e:
                named.add("Equation " + e.group(1))
    return clauses, named


def _context_annex(context: str) -> str:
    m = re.match(r"([A-C])[.\s]", context + ".")
    return m.group(1) if m and context[:1] in "ABC" and (len(context) == 1 or context[1] in ". ") else ""


def check_rows(rows):
    """Integrity problems of the classified CSV (empty list means clean). [REF NBC105-2025 cross-references]"""
    problems = []
    clauses, named = _register_targets()
    ids = set()
    for r in rows:
        rid = r.get("ref_id", "?")
        if rid in ids:
            problems.append(f"{rid}: duplicate ref_id")
        ids.add(rid)
        cls = r.get("classification", "")
        if cls == UNCLASSIFIED or cls not in CLASSES:
            problems.append(f"{rid}: classification '{cls}' is not one of {CLASSES}")
            continue
        if not r.get("rationale", "").strip():
            problems.append(f"{rid}: rationale is required")
        if cls in (CLASS_MISDIRECTED, CLASS_AMBIGUOUS) and not r.get("correct_target", "").strip():
            problems.append(f"{rid}: {cls} needs correct_target")
        if cls == CLASS_MISDIRECTED and not r.get("corrected_citation", "").strip():
            problems.append(f"{rid}: MISDIRECTED needs corrected_citation (the text code and docs must carry)")
        if cls == CLASS_VALID and r.get("correct_target", "").strip():
            problems.append(f"{rid}: VALID must not name a different correct_target")
        # target existence in the normative register
        annex = _context_annex(r.get("context", ""))
        for field in ("target", "correct_target"):
            t = r.get(field, "").strip()
            if not t or (field == "target" and cls == CLASS_MISDIRECTED and False):
                continue
            for part in [p.strip() for p in t.split(";") if p.strip()]:
                if re.match(r"^(Table|Figure|Equation)\s", part):
                    if part.startswith("Equation"):
                        continue          # equations are numbered in image text; verified by hand
                    if annex:
                        continue          # annex tables/figures restart their own numbering
                    if field == "target" and cls == CLASS_MISDIRECTED:
                        continue          # the printed target may not exist (e.g. Figure 4-4)
                    if part not in named:
                        problems.append(f"{rid}: {field} '{part}' not in the normative register")
                elif re.match(r"^\d+(\.\d+)*$", part):
                    full = (annex + "." + part) if annex else part
                    if full not in clauses:
                        problems.append(f"{rid}: {field} '{full}' not a clause of the normative register")
        for rel in [p.strip() for p in r.get("citation_files", "").split(";") if p.strip()]:
            path = ROOT / rel
            if not path.exists():
                problems.append(f"{rid}: citation file {rel} does not exist")
            elif r.get("corrected_citation", "") and r["corrected_citation"] not in path.read_text(
                    encoding="utf-8", errors="replace"):
                problems.append(f"{rid}: {rel} does not cite the corrected target '{r['corrected_citation']}'")
    return problems


def stale_citation_scan(roots=("components", "tools", "docs"), skip=("docs/nbc105/normative_register",)):
    """Lines that send drift limits to 5.6 without naming 5.5.3 or accidental eccentricity.

    [REF NBC105-2025 8.1.3.1 / 9.3.3.1 cross-reference to 5.6]
    """
    bad = []
    pat = re.compile(r"(?i)\b(?:clause|section|§)\s*5\.6\b")
    for root in roots:
        for path in (ROOT / root).rglob("*"):
            rel = path.relative_to(ROOT).as_posix()
            if (not path.is_file() or path.suffix not in (".py", ".md", ".csv") or
                    any(rel.startswith(s) for s in skip) or rel.startswith("docs/nbc105/CROSS_REFERENCE") or
                    "Saved_Project" in rel):
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                low = line.lower()
                if pat.search(line) and ("drift" in low or "inter-story" in low or "interstory" in low):
                    if "5.5.3" not in line and "eccentricity" not in low:
                        bad.append(f"{rel}:{n}")
    return bad


def markdown(rows):
    """Render the human-readable register. [REF NBC105-2025 cross-references]"""
    by = {c: [r for r in rows if r["classification"] == c] for c in CLASSES}
    lines = [
        "# NBC 105:2025 cross-reference register",
        "",
        "Generated by `tools/nbc105_crossref_audit.py --markdown` from `CROSS_REFERENCE_REGISTER.csv`. "
        "Every printed cross-reference is classified; the test `tests/test_nbc105_followup_crossref_audit.py` "
        "fails on any unclassified one. The standard's text is not copied (matched phrase, locator, line hash only).",
        "",
        f"Total {len(rows)}: VALID {len(by[CLASS_VALID])}, MISDIRECTED {len(by[CLASS_MISDIRECTED])}, "
        f"AMBIGUOUS {len(by[CLASS_AMBIGUOUS])}.",
        "",
        "## Misdirected and ambiguous references",
        "",
        "| Ref | Printed p. | Where | Printed reference | Correct target | Why |",
        "|---|---|---|---|---|---|",
    ]
    for r in by[CLASS_MISDIRECTED] + by[CLASS_AMBIGUOUS]:
        lines.append(f"| {r['ref_id']} | {r['printed_page']} | {r['context']} | {r['reference_text']} "
                     f"({r['classification']}) | {r['correct_target']} | {r['rationale']} |")
    lines += ["", "## Valid references", "", "| Ref | Printed p. | Where | Printed reference | Note |",
              "|---|---|---|---|---|"]
    for r in by[CLASS_VALID]:
        lines.append(f"| {r['ref_id']} | {r['printed_page']} | {r['context']} | {r['reference_text']} | {r['rationale']} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    """CLI. [REF NBC105-2025 cross-references]"""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pdf", help="path to the NBC 105:2025 PDF (not stored in the repo)")
    ap.add_argument("--extract", action="store_true", help="list printed references (needs --pdf); "
                    "add --merge to write unclassified rows into the CSV")
    ap.add_argument("--merge", action="store_true", help="with --extract: add new references as UNCLASSIFIED")
    ap.add_argument("--check", action="store_true", help="validate the classified CSV (and the PDF if given)")
    ap.add_argument("--markdown", action="store_true", help="regenerate CROSS_REFERENCE_REGISTER.md")
    a = ap.parse_args(argv)
    if a.extract:
        if not a.pdf:
            ap.error("--extract needs --pdf")
        refs = extract_from_pdf(a.pdf)
        rows = read_crossrefs() if CROSSREF_CSV.exists() else []
        new = unclassified_references(refs, rows)
        print(f"{len(refs)} printed references, {len(new)} not classified")
        for r in new:
            print(f"  p.{r['printed_page']} {r['context']}: {r['reference_text']} -> {r['target']}")
        if a.merge and new:
            start = len(rows)
            for i, r in enumerate(new, start + 1):
                rows.append(dict(r, ref_id=f"XR-{i:04d}", classification=UNCLASSIFIED))
            write_crossrefs(rows)
        return 0
    if a.markdown:
        CROSSREF_MD.write_text(markdown(read_crossrefs()), encoding="utf-8", newline="\n")
        print(f"wrote {CROSSREF_MD}")
        return 0
    if a.check:
        rows = read_crossrefs()
        problems = check_rows(rows)
        stale = stale_citation_scan()
        problems += [f"stale 5.6 drift citation at {s}" for s in stale]
        if a.pdf:
            for r in unclassified_references(extract_from_pdf(a.pdf), rows):
                problems.append(f"unclassified printed reference p.{r['printed_page']}: {r['reference_text']}")
        for p in problems:
            print("FAIL", p)
        print("cross-reference audit:", "FAILED" if problems else "OK", f"({len(rows)} classified)")
        return 1 if problems else 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
