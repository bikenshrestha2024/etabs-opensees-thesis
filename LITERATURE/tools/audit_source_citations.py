#!/usr/bin/env python3
"""Offline literature-citation scanner. Python 3.12+; no pip dependencies.

Run: python LITERATURE/tools/audit_source_citations.py
Run: python LITERATURE/tools/audit_source_citations.py --check

Read-only scan of active source code and documentation; writes generated
citation CSV, unmatched-DOI CSV and category indexes to LITERATURE only.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "LITERATURE"
EXT = {".py", ".md", ".json", ".yaml", ".yml", ".rst", ".toml", ".txt"}
EXCLUDE = (
    "LITERATURE/", "Saved_Project_V156/", "archive/", "docs/json/",
    "docs/source/", "Research_Components/results/", "Research_Components/study/",
    "excel/historical/", "Worked_Example_", "Verification_V",
)
URL_RE = re.compile(r'https?://[^\s"<>]+', re.I)
DOI_RE = re.compile(r'10\.\d{4,9}/[^\s"<>]+', re.I)
CATS = {
    "FVD": r"fvd|viscous.?damper|damper|damping",
    "BRB": r"brb|buckling.restrain|brace",
    "Shear_Wall": r"shear.?wall|mvlem|fsam|layered.?shell|shear.flexure",
    "Outrigger": r"outrigger|belt.?truss|cap.?truss",
    "Reinforcing_Steel": r"steel02|steelmpf|rebar|reinforc|menegotto",
    "Concrete": r"concrete01|concrete02|concretecm|confinement|chang.?mander",
    "Ground_Motions": r"ground.?motion|seismomatch|accelerogram|spectral.?match",
    "Codes_Standards": r"nbc.?105|dudbc|aci.?318|is.?456|asce.?41|standard",
    "OpenSees_Methods": r"opensees|integrator|solver|numerical.?method",
    "Material_Calibration": r"calibrat|sensitivity|bayesian|material.?param",
}


def tracked():
    try:
        b = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"],
                           capture_output=True, check=True, timeout=20).stdout
        raw = [ROOT / p.decode("utf-8", "replace") for p in b.split(b"\0") if p]
        method = "git ls-files"
    except (OSError, subprocess.CalledProcessError):
        raw = list(ROOT.rglob("*"))
        method = "filesystem fallback"
    result = []
    for f in raw:
        if not f.is_file() or f.suffix.lower() not in EXT or f.stat().st_size > 2000000:
            continue
        p = f.relative_to(ROOT).as_posix()
        if any(p.startswith(prefix) for prefix in EXCLUDE) or "/__pycache__/" in p:
            continue
        result.append(f)
    return sorted(set(result)), method


def canonical(raw):
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", raw.strip(), flags=re.I).rstrip(".,;:)]}").lower()


def csv_text(head, rows):
    b = io.StringIO(newline="")
    writer = csv.writer(b)
    writer.writerow(head)
    writer.writerows(rows)
    return b.getvalue()


def generate():
    known = {}
    with (LIB / "MASTER_LITERATURE_INDEX.csv").open(encoding="utf-8-sig", newline="") as fp:
        for row in csv.DictReader(fp):
            if row.get("DOI", "").strip():
                known[canonical(row["DOI"])] = row
    files, method = tracked()
    rows, unlisted, by_category = [], defaultdict(list), defaultdict(list)
    errors = []
    for f in files:
        p = f.relative_to(ROOT).as_posix()
        try:
            lines = f.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        except OSError as exc:
            errors.append([p, str(exc)])
            continue
        for no, line in enumerate(lines, 1):
            items = set()
            for match in DOI_RE.findall(line):
                items.add(("DOI", canonical(match)))
            for match in URL_RE.findall(line):
                url = match.rstrip(".,;:)]}")
                if "doi.org/" not in url.lower():
                    items.add(("URL", url))
            for kind, ref in sorted(items):
                data = known.get(ref, {}) if kind == "DOI" else {}
                id_ = data.get("ID", "")
                title = data.get("Title", "")
                tags = [c for c, pattern in CATS.items()
                        if re.search(pattern, p + " " + line, flags=re.I)]
                if not tags:
                    tags = ["OpenSees_Methods"]
                for tag in tags:
                    entry = [tag, p, no, kind, ref, id_, title, line.strip()[:180]]
                    rows.append(entry)
                    by_category[tag].append(entry)
                if kind == "DOI" and not id_:
                    unlisted[ref].append(p + ":" + str(no))
    out = {
        "LITERATURE/CODE_CITATION_OCCURRENCES.csv": csv_text(
            ["Category", "Source_file", "Line", "Type", "Reference", "ID", "Title", "Context"], rows),
        "LITERATURE/UNCATALOGUED_DOIS.csv": csv_text(
            ["DOI", "Occurrences", "Example_source_locations"],
            [[doi, len(loc), "; ".join(loc[:15])] for doi, loc in sorted(unlisted.items())]),
    }
    for category in CATS:
        entries = by_category[category]
        uniq = {}
        for x in entries:
            uniq.setdefault((x[3], x[4]), [x[5], x[6], []])[2].append(x[1] + ":" + str(x[2]))
        lines = ["# " + category.replace("_", " ") + ": citations used in source",
                 "", "GENERATED by audit_source_citations.py; citations are NOT parameter calibration.",
                 "", "| Master ID | Reference | Referenced at |", "|---|---|---|"]
        for (kind, ref), (id_, title, places) in sorted(uniq.items()):
            dest = "https://doi.org/" + ref if kind == "DOI" else ref
            label = (title or ref).replace("|", "/")[:120]
            loc = ", ".join(places[:8]).replace("|", "/")
            lines.append("| " + (id_ or "UNMATCHED") + " | [" + label + "](" + dest + ") | " + loc + " |")
        out["LITERATURE/" + category + "/CODE_REFERENCES.md"] = "\n".join(lines) + "\n"
    manifest = {
        "source": "LITERATURE/tools/audit_source_citations.py",
        "method": method, "files_scanned": len(files),
        "reference_occurrences_with_category_expansion": len(rows),
        "distinct_reference_strings": len(set((x[3], x[4]) for x in rows)),
        "unmatched_doi_count": len(unlisted), "errors": errors,
        "limitations": "DOI and URL regex only; author-year references without DOI require human review. Archived/generated files excluded.",
    }
    out["LITERATURE/CODE_CITATION_SCAN_SCOPE.json"] = json.dumps(manifest, indent=2) + "\n"
    return out, manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    generated, manifest = generate()
    changed = []
    for name, content in generated.items():
        p = ROOT / name
        if p.exists() and p.read_text(encoding="utf-8-sig") == content:
            continue
        changed.append(name)
        if not options.check:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    print(json.dumps({**manifest, "changed_files": changed}, indent=2))
    return 1 if options.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
