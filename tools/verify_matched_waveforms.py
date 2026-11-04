"""Read-only verification of user-supplied SeismoMatch matched accelerograms.

Research audit basis: docs/ground_motions/seismomatch_20261104/
Uses only Python standard library. No waveform data is uploaded or modified.
Does not reproduce Newmark spectra: see the full numerical audit report.
No match to a nominal target is a substitute for original SeismoMatch logs.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = (ROOT / "docs" / "ground_motions" / "seismomatch_20261104"
            / "matched_component_register.csv")


def parse_matched(path):
    """Read a SeismoMatch two-column (time seconds, acceleration g) export."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(str(source))
    payload = source.read_bytes()
    text = payload.decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    first = "\n".join(lines[:8]).lower()
    if "time series matched accelerogram" not in first:
        raise ValueError(f"Not a confirmed matched SeismoMatch header: {source.name}")
    dt_match = re.search(r"time\s*step\s*:\s*([\d.eE+-]+)\s*s", first)
    if not dt_match:
        raise ValueError(f"Missing source time-step declaration: {source.name}")
    if not re.search(r"acc\s*\(g\)", first):
        raise ValueError(f"Acceleration source units not identified as g: {source.name}")
    header_dt = float(dt_match.group(1))
    if not math.isfinite(header_dt) or header_dt <= 0:
        raise ValueError("Invalid header dt")
    # Parse only after the verified time/acceleration column heading.
    # Once data begin, malformed lines cannot be silently dropped: that
    # could shift duration, change peak acceleration or corrupt XY/YX pairing.
    column_header = next(
        (i for i, line in enumerate(lines) if
         re.search(r"time\s*\(\s*sec\s*\).*acc\s*\(\s*g\s*\)", line, re.I)),
        None)
    if column_header is None:
        raise ValueError(f"Missing Time(sec) Acc(g) columns: {source.name}")
    time = []
    acceleration = []
    for lineno in range(column_header + 1, len(lines)):
        line = lines[lineno].strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) != 2:
            raise ValueError(f"Malformed data at line {lineno + 1}: expected exactly 2 columns")
        try:
            t, a = (float(fields[0]), float(fields[1]))
        except ValueError as exc:
            raise ValueError(f"Non-numeric waveform at line {lineno + 1}") from exc
        if not math.isfinite(t) or not math.isfinite(a):
            raise ValueError(f"Nonfinite waveform value at line {lineno + 1}")
        time.append(t)
        acceleration.append(a)
    if len(time) < 3:
        raise ValueError(f"Too few data samples: {source.name}")
    if abs(time[0]) > 1e-8:
        raise ValueError(f"Source time must begin at 0: {source.name}")
    max_dt_error = max(abs((b - a) - header_dt)
                       for a, b in zip(time, time[1:]))
    if max_dt_error > max(1e-8, header_dt*1e-5):
        raise ValueError(f"Nonuniform or decreasing sample time: {source.name}")
    return {
        "name": source.name,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "samples": len(time),
        "dt_s": header_dt,
        "end_time_s": time[-1],
        "max_abs_acceleration_g": max(map(abs, acceleration)),
        "sample_dt_max_error_s": max_dt_error,
        "units": "g",
        "header_verified": True,
    }


def check_source(source, row):
    record = parse_matched(source)
    errors = []
    if record["sha256"] != row["matched_sha256"]:
        errors.append("SHA256_MISMATCH")
    if not math.isclose(record["dt_s"], float(row["matched_dt_s"]),
                        rel_tol=0, abs_tol=1e-10):
        errors.append("DT_MISMATCH")
    if not math.isclose(record["end_time_s"], float(row["matched_end_time_s"]),
                        rel_tol=0, abs_tol=1e-8):
        errors.append("DURATION_MISMATCH")
    if not math.isclose(record["max_abs_acceleration_g"],
                        float(row["matched_pga_g"]),
                        rel_tol=0, abs_tol=1e-5):
        errors.append("PGA_MISMATCH")
    return {**record, "event": row["event"], "component": row["component"],
            "status": "SOURCE_REGISTER_MATCH" if not errors else "MISMATCH",
            "errors": errors}


def audit(matched_dir, register=REGISTER):
    """Check complete register, filenames, source hashes, dt and pair pairing."""
    directory = Path(matched_dir).expanduser().resolve()
    if not directory.is_dir():
        raise NotADirectoryError(str(directory))
    with Path(register).open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 16:
        raise ValueError("Expected exactly 16 registered matched components")
    keys = [(r["event"], r["component"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate event/component in register")
    # Never permit a custom register to select files outside the chosen
    # matched directory or to alias two registered components to one file.
    names = [r["source_filename"] for r in rows]
    if len(set(names)) != len(names):
        raise ValueError("Two components share a source filename")
    if any(not name or Path(name).name != name or
           name in (".", "..") or "/" in name or "\\\\" in name
           for name in names):
        raise ValueError("Unsafe source filename in matched-record register")
    by_event = defaultdict(list)
    records = []
    for row in rows:
        if row["component"] not in ("A", "B"):
            raise ValueError("Only A and B horizontal components allowed")
        filepath = directory / row["source_filename"]
        if not filepath.is_file():
            records.append({
                "event": row["event"], "component": row["component"],
                "source": str(filepath), "status": "SOURCE_NOT_FOUND",
                "errors": ["SOURCE_NOT_FOUND"]})
            continue
        try:
            rec = check_source(filepath, row)
            records.append(rec)
            by_event[row["event"]].append(rec)
        except (ValueError, OSError) as exc:
            records.append({
                "event": row["event"], "component": row["component"],
                "source": str(filepath), "status": "PARSE_FAILURE",
                "errors": [str(exc)]})
    pairs = []
    for event in sorted(set(r["event"] for r in rows)):
        components = by_event[event]
        status = "COMPLETE" if len(components) == 2 and all(
            x["status"] == "SOURCE_REGISTER_MATCH" for x in components) else "INCOMPLETE"
        dt_equal = bool(len(components) == 2 and math.isclose(
            components[0]["dt_s"], components[1]["dt_s"],
            rel_tol=0, abs_tol=1e-10))
        duration_equal = bool(len(components) == 2 and math.isclose(
            components[0]["end_time_s"], components[1]["end_time_s"],
            rel_tol=0, abs_tol=1e-8))
        if not dt_equal:
            status = "PAIR_DT_MISMATCH_OR_MISSING"
        if not duration_equal:
            status = "PAIR_END_TIME_MISMATCH_OR_MISSING"
        pairs.append(dict(event=event, status=status,
                          same_sampling_interval=dt_equal,
                          same_end_time=duration_equal,
                          explicit_end_time_policy_required=not duration_equal))
    errors = [r for r in records if r["status"] != "SOURCE_REGISTER_MATCH"]
    pair_warnings = [p for p in pairs if p["status"] != "COMPLETE"]
    # SHA integrity, pair synchronization, and NBC design approval are three
    # different statements. An expected one-sample Loma mismatch must remain
    # visible rather than being reported as all eight pairs synchronized.
    source_integrity = "MATCH" if not errors else "FAIL"
    pair_integrity = "SYNCHRONIZED" if not pair_warnings else "REVIEW_REQUIRED"
    return {
        "audit_schema": "SEISMOMATCH_MATCHED_16_COMPONENT_REGISTER_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records), "pair_count": len(pairs),
        "records": records, "pairs": pairs,
        "source_discrepancies": len(errors),
        "pair_synchronization_review_count": len(pair_warnings),
        "source_integrity_status": source_integrity,
        "pair_synchronization_status": pair_integrity,
        "status": ("SOURCE_DISCREPANCIES" if errors else
                   "SOURCE_INTEGRITY_PASSED_PAIR_REVIEW_REQUIRED" if pair_warnings
                   else "SOURCE_AND_PAIR_INTEGRITY_PASSED"),
        "nbc105_scale_factor_033_to_3_verified": False,
        "nbc105_common_lower_factor_verified": False,
        "nbc105_modal_spectral_interval_verified": False,
        "independent_target_spectrum_pass": False,
        "units_in_opensees_kNmS": {
            "additional_matched_waveform_scale": 1.0,
            "g_to_m_per_s2": 9.80665},
        "warnings": [
            "Matched PGA ratio is not original SeismoMatch scaling factor.",
            "Inspect Gorkha matching source: 322.94 s vs original 120 s.",
            "Loma Prieta 0.005 s end mismatch requires explicit policy.",
            "Waveform provenance alone cannot approve NBC105 code compliance.",
        ]}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--matched-dir", type=Path, required=True)
    p.add_argument("--register", type=Path, default=REGISTER)
    p.add_argument("--output", type=Path, required=True)
    opts = p.parse_args(argv)
    report = audit(opts.matched_dir, opts.register)
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    opts.output.write_text(json.dumps(report, indent=2, allow_nan=False),
                           encoding="utf-8")
    print(json.dumps({"status": report["status"], "pairs": report["pair_count"],
                      "pairs_needing_review": report["pair_synchronization_review_count"],
                      "sources": report["record_count"],
                      "output": str(opts.output)}, indent=2))
    # Return 3 for physically inconsistent pair end times even when source
    # hashes match. A caller must explicitly review and accept the policy.
    if report["source_discrepancies"]:
        return 2
    return 3 if report["pair_synchronization_review_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
