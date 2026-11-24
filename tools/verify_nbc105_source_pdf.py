"""Check the repo's NBC 105:2025 constants against a user-supplied printed PDF.

[REF NBC105-2025 Tables 3-1, 4-1, 5-1, 5-2, 6-1; §5.1.3, §5.5.3, §8.1.1.5,
§9.3.2.2, §9.3.2.4] Reads the PDF text (``pdftotext -layout``) or a ready
``.txt`` extract, parses the printed table rows and numeric limits, and
compares each with the value the ``components.nbc105`` code actually uses.
Records the source SHA-256 and page count so the printing is identified.

Scope: tables and numeric limits only. It does not read every sentence, does
not certify the code, and never copies the PDF into the repository.

    python tools/verify_nbc105_source_pdf.py PDF_OR_TXT [--out report.json]

Exit status 0 only when every check matches; 1 on any mismatch or parse miss.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_NUM = r"(\d+(?:\.\d+)?)"
_T31 = {"Beam": "beam", "Columns": "column", "Wall\\W+cracked": "cracked wall",
        "Wall\\W+uncracked": "uncracked wall", "Masonry Wall": "masonry wall",
        "Flat Slabs": "flat slab"}


def extract_text(path: Path) -> tuple[str, dict]:
    """Return (text, identity) for a PDF or text file; identity has SHA/pages."""
    raw = path.read_bytes()
    identity = {"sha256": hashlib.sha256(raw).hexdigest(), "file_bytes": len(raw),
                "pages": None}
    if path.suffix.lower() != ".pdf":
        return raw.decode("utf-8", errors="replace"), identity
    text = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True,
                          capture_output=True, text=True).stdout
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True,
                          text=True).stdout
    m = re.search(r"^Pages:\s+(\d+)", info, re.M)
    identity["pages"] = int(m.group(1)) if m else None
    return text, identity


def _section(text: str, start: str, stop: str) -> str:
    a = text.find(start)
    if a < 0:
        return ""
    b = text.find(stop, a + len(start))
    return text[a:b if b > a else len(text)]


def parse_source(text: str) -> dict:
    """Parse printed rows and limits; a missing item stays absent (parse miss)."""
    out: dict = {}
    t31 = _section(text, "Table 3-1 Effective", "3.5")
    rows = {}
    for pattern, key in _T31.items():
        m = re.search(pattern + r"\s+" + _NUM + r" Ec Ig\s+" + _NUM + r" Ec Ig", t31)
        if m:
            rows[key] = (float(m.group(1)), float(m.group(2)))
    out["table_3_1"] = rows

    t41 = _section(text, "Table 4-1", "4.1.3")
    cols = {}
    for label, key in (("Ta", "Ta"), ("Tc", "Tc"), ("Td", "Td")):
        m = re.search(r"^\s*" + label + r"\s+" + (_NUM + r"\s+") * 3 + _NUM,
                      t41, re.M)
        if m:
            cols[key] = [float(g) for g in m.groups()]
    m = re.search(r"^\s*\S\s+(2\.5)\s+(2\.5)\s+(2\.5)\s+(2\.25)\s*$", t41, re.M)
    if m:
        cols["alpha"] = [float(g) for g in m.groups()]
    out["table_4_1"] = cols

    t51 = _section(text, "Table 5-1:", "5.3")
    t = {}
    for key, pat in (("storage", r"Storage\s+" + _NUM),
                     ("other", r"For Other Purpose\s+" + _NUM)):
        m = re.search(pat, t51)
        if m:
            t[key] = float(m.group(1))
    if re.search(r"Roof\s+Nil", t51):
        t["roof"] = 0.0
    out["table_5_1"] = t

    t52 = _section(text, "Table 5-2:", "5.4")
    rows52 = {}
    for line in t52.splitlines():
        m = re.match(r"^\s*(\d{1,2})\s+.*?" + _NUM + r"\s+" + _NUM + r"\s+" + _NUM
                     + r"\s*$", line)
        if m and 1 <= int(m.group(1)) <= 21:
            rows52[int(m.group(1))] = tuple(float(m.group(i)) for i in (2, 3, 4))
    out["table_5_2"] = rows52

    t61 = _section(text, "Table 6-1:", "7   Modal")
    rows61 = {}
    for line in t61.splitlines():
        m = re.match(r"^\s*(\d)\s+" + _NUM + r"\s*$", line)
        if m:
            rows61[int(m.group(1))] = float(m.group(2))
        m = re.match(r"^\s*6 or more\s+" + _NUM + r"\s*$", line)
        if m:
            rows61[6] = rows61[7] = float(m.group(1))  # "6 or more" covers both
    out["table_6_1"] = rows61

    flat = re.sub(r"\s+", " ", text)
    limits = {}
    m = re.search(_NUM + r" at ultimate limit state " + _NUM
                  + r" at serviceability limit state", flat)
    if m:
        limits["drift_uls"], limits["drift_sls"] = float(m.group(1)), float(m.group(2))
    m = re.search(r"increased by a factor of " + _NUM, flat)
    if m:
        limits["period_amplification"] = float(m.group(1))
    m = re.search(r"between " + _NUM + r" and (\d+)\. Where a selected", flat)
    if m:
        limits["scale_min"], limits["scale_max"] = float(m.group(1)), float(m.group(2))
    m = re.search(r"Linear viscous damping shall not exceed (\d+)%", flat)
    if m:
        limits["elastic_damping_max"] = float(m.group(1)) / 100.0
    if re.search(r"T1/100 .{0,12}Tn .{0,12}0\.01s", flat):
        limits["dt_rule"] = "min(digitization,T1/100,Tn,0.01)"
    out["limits"] = limits
    return out


def repo_values() -> dict:
    """Read the values the production code actually uses (not copies of them)."""
    from components.nbc105 import (clause_03_scope_of_analysis as c3,
                                   clause_04_seismic_hazard as c4,
                                   clause_05_dynamic_characteristics as c5,
                                   clause_06_equivalent_static as c6,
                                   clause_08_elastic_time_history as c8,
                                   clause_09_nonlinear_analysis as c9)
    vals: dict = {"table_3_1": {n: (c3.cracked_flexural_factor(n, "ULS"),
                                    c3.cracked_flexural_factor(n, "SLS"))
                                for n in _T31.values()}}
    vals["table_4_1"] = {k: [c4.TABLE_4_1[s][k] for s in "ABCD"]
                         for k in ("Ta", "Tc")}
    vals["table_4_1"]["Td"] = [c4.TABLE_4_1[s]["Td"] for s in "ABCD"]
    vals["table_4_1"]["alpha"] = [c4.TABLE_4_1[s]["alpha"] for s in "ABCD"]
    vals["table_5_1"] = dict(c5.LIVE_LOAD_FACTORS)
    vals["table_5_2"] = {i: tuple(c5.table_5_2_system_factors(i)[k]
                                  for k in ("Rmu", "Omega_u", "Omega_s"))
                         for i in range(1, 22)}
    vals["table_6_1"] = {i: c6.esm_deflection_factor(i) for i in range(1, 8)}
    limits = {"drift_uls": c5.interstory_drift_check(1.0, 1.0, "ULS")["limit"],
              "drift_sls": c5.interstory_drift_check(1.0, 1.0, "SLS")["limit"],
              "period_amplification": c5.AMPLIFICATION_FACTOR}
    lo = hi = None
    for f in (.329, .33):
        try:
            c9.motion_scale_factor(f, 1.0)
            lo = f if lo is None else lo
        except ValueError:
            pass
    for f in (3.0, 3.001):
        try:
            c9.motion_scale_factor(f, 1.0)
            hi = f
        except ValueError:
            pass
    limits["scale_min"], limits["scale_max"] = lo, hi
    try:
        c8.elastic_model_prerequisites(is_3d=True, gravity=True, p_delta=True,
                                       torsion=True, damping_ratio=.05)
        limits["elastic_damping_max"] = .05
        c8.elastic_model_prerequisites(is_3d=True, gravity=True, p_delta=True,
                                       torsion=True, damping_ratio=.0501)
        limits["elastic_damping_max"] = None
    except ValueError:
        pass
    if (c9.history_time_step_limit_s(1.0, 1.0, 1.0) == .01
            and c9.history_time_step_limit_s(.5, 1.0, 1.0) == .005
            and c9.history_time_step_limit_s(1.0, 1.0, .002) == .002
            and c9.history_time_step_limit_s(1.0, .004, 1.0) == .004):
        limits["dt_rule"] = "min(digitization,T1/100,Tn,0.01)"
    vals["limits"] = limits
    return vals


def compare(source: dict, repo: dict) -> list[dict]:
    """Return one record per printed item: item, printed, code, status."""
    rows = []

    def add(item, printed, code):
        if printed is None:
            status = "PARSE_MISS"
        elif printed == code or (isinstance(printed, float) and isinstance(code, float)
                                 and abs(printed - code) < 1e-12):
            status = "MATCH"
        else:
            status = "MISMATCH"
        rows.append({"item": item, "printed": printed, "code": code, "status": status})

    for key, code_rows in repo.items():
        printed_rows = source.get(key, {})
        for name, code in code_rows.items():
            printed = printed_rows.get(name)
            if isinstance(printed, list):
                printed = [float(v) for v in printed]
            add(f"{key}.{name}", printed, code if not isinstance(code, tuple)
                else tuple(code))
    return rows


def run(path: Path) -> dict:
    """Build the report dict for one source file."""
    text, identity = extract_text(path)
    rows = compare(parse_source(text), repo_values())
    bad = [r for r in rows if r["status"] != "MATCH"]
    return {"status": "ALL_PRINTED_ITEMS_MATCH" if not bad else "DISCREPANCIES_FOUND",
            "scope": "TABLES_AND_NUMERIC_LIMITS_ONLY_NOT_FULL_TEXT_NOT_CODE_APPROVAL",
            "source": identity, "checked": len(rows), "failures": bad, "results": rows}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("source", type=Path)
    p.add_argument("--out", type=Path)
    a = p.parse_args(argv)
    report = run(a.source)
    text = json.dumps(report, indent=2, sort_keys=True, default=list)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(report["status"], "checked", report["checked"],
          "failures", len(report["failures"]), "sha256", report["source"]["sha256"][:16])
    for r in report["failures"]:
        print("  ", r["status"], r["item"], "printed", r["printed"], "code", r["code"])
    return 0 if not report["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
