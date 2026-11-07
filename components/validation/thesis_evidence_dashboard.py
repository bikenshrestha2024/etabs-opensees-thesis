"""Read-only, fail-closed thesis NLTHA evidence identity dashboard.

Source SHA256 and stage identity do NOT constitute engineering or NBC design approval.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

STAGES = (
    ("00_PROVENANCE", "EDB/Excel/records/software source hashes"),
    ("01_ETABS_OPENSEES_GEOMETRY", "3D geometry, diaphragm, core openings"),
    ("02_MASS_AND_GRAVITY", "Mass, gravity and P-Delta balance"),
    ("03_RC_WALL_CALIBRATION", "RC core/coupling-beam/FSAM cyclic validation"),
    ("04_FRAME_AND_DEVICE_CALIBRATION", "RC, steel, FVD, BRB native benchmarks"),
    ("05_MODAL_DAMPING", "Modes, torsion and damping allocation"),
    ("06_NBC105_RECORD_PAIR_AUDIT", "Site, spectra, XY/YX source and record timing"),
    ("07_ZERO_X_Y_XY_DIAGNOSTIC", "First-step wall failure evidence"),
    ("08_FULL_XY_YX_NLTHA", "Full accepted histories, not shortened trials"),
    ("09_M0_M6_COMPARISON", "Paired, source-equivalent variant comparison"),
    ("10_REPORTING_AND_REVIEW", "Drift, twist, component energy and review"),
)
VALID = {"NOT_STARTED", "IN_PROGRESS", "BLOCKED", "EVIDENCE_READY", "VERIFIED"}

def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()

def _valid_hash(x):
    return isinstance(x, str) and len(x) == 64 and all(c in "0123456789abcdefABCDEF" for c in x)

def audit(manifest, *, manifest_dir, base_dir=None):
    """Validate reviewer-declared evidence identity and ordered dependencies.

    A VERIFIED claim is screened only for referenced local file identities.
    It does not verify that the contents establish physical correctness.
    """
    if not isinstance(manifest, dict) or not isinstance(manifest.get("stages"), dict):
        raise ValueError("Manifest must contain a stages object")
    base = Path(base_dir or manifest_dir).resolve()
    rows = []
    previous_verified = True
    for stage_id, description in STAGES:
        item = manifest["stages"].get(stage_id, {})
        if not isinstance(item, dict):
            raise ValueError(stage_id + ": stage must be an object")
        declared = item.get("status", "NOT_STARTED")
        if declared not in VALID:
            raise ValueError(stage_id + ": invalid declared status " + repr(declared))
        evidence = item.get("evidence", [])
        if not isinstance(evidence, list):
            raise ValueError(stage_id + ": evidence must be a list")
        issues, seen = [], set()
        if declared == "VERIFIED" and not evidence:
            issues.append("Verified stage has no source evidence")
        for entry in evidence:
            if not isinstance(entry, dict):
                issues.append("Malformed evidence entry")
                continue
            raw = entry.get("path")
            if not isinstance(raw, str) or not raw.strip():
                issues.append("Missing evidence path")
                continue
            path = Path(raw).expanduser()
            if not path.is_absolute():
                path = base / path
            path = path.resolve()
            if path in seen:
                issues.append("Duplicate evidence path")
            seen.add(path)
            digest = entry.get("sha256")
            if not _valid_hash(digest):
                issues.append("Absent or invalid expected SHA256: " + raw)
            if not path.is_file():
                issues.append("Evidence file not found: " + raw)
            elif _valid_hash(digest) and sha256_file(path).lower() != digest.lower():
                issues.append("Evidence SHA256 mismatch: " + raw)
        if declared == "VERIFIED" and not previous_verified:
            issues.append("Earlier stage not VERIFIED")
        verified = declared == "VERIFIED" and not issues
        evaluated = "VERIFIED_IDENTITY_ONLY" if verified else ("BLOCKED" if issues else declared)
        rows.append(dict(stage=stage_id, description=description,
                         declared_status=declared, evaluated_status=evaluated,
                         identity_verified=verified, evidence_count=len(evidence),
                         issues="; ".join(issues), engineering_accepted=False))
        previous_verified = verified
    return dict(schema="thesis-evidence-dashboard-v1",
                status="EVIDENCE_IDENTITY_SCREEN_ONLY_NOT_NBC_DESIGN_ACCEPTANCE",
                stages=rows,
                all_stage_identities_verified=all(r["identity_verified"] for r in rows),
                engineering_accepted=False)

def save_reports(result, output_dir, *, png=False):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "Thesis_Evidence_Dashboard.json").write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    with (out / "Thesis_Evidence_Dashboard.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(result["stages"][0]))
        writer.writeheader()
        writer.writerows(result["stages"])
    if png:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        rows = result["stages"]
        values = [int(r["identity_verified"]) for r in rows]
        fig, ax = plt.subplots(figsize=(11, 7))
        ax.barh(range(len(rows)), values,
                color=["#297d61" if v else "#b74b4b" for v in values])
        ax.set_yticks(range(len(rows)), [r["stage"] for r in rows])
        ax.invert_yaxis()
        ax.set_xlim(0, 1.15)
        ax.set_xticks([0, 1], ["Missing or unverified", "Identity verified"])
        ax.set_title("Thesis evidence identity only — NOT engineering approval")
        for i, r in enumerate(rows):
            ax.text(values[i] + 0.02, i, r["evaluated_status"], va="center", fontsize=8)
        fig.tight_layout()
        fig.savefig(out / "Thesis_Evidence_Dashboard.png", dpi=170)
        plt.close(fig)
    return out

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--base-dir")
    p.add_argument("--png", action="store_true")
    a = p.parse_args(argv)
    path = Path(a.manifest).resolve()
    result = audit(json.loads(path.read_text(encoding="utf-8-sig")),
                   manifest_dir=path.parent, base_dir=a.base_dir)
    save_reports(result, a.output_dir, png=a.png)
    print(json.dumps({"status": result["status"],
                      "identity_verified": result["all_stage_identities_verified"],
                      "output_dir": str(Path(a.output_dir).resolve())}, indent=2))
    return 0 if result["all_stage_identities_verified"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
