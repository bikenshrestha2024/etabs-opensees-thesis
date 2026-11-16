"""Validate locally produced Studio benchmark evidence without editing a thesis model.

PUBLICATION WARNING: input JSON can contain absolute paths or model-specific data.
Write sanitized summary only; keep all source files private and case-owned.
Reference: tools/verification_studio/THESIS_VALIDATION_MATRIX.md
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

EXPECTED = {f"B{i:02d}": (4, 11, 2, 3, 3, 15, 3, 3, 3, 2, 2, 7)[i - 1]
            for i in range(1, 13)}
NATIVE_STATUS = "NATIVE_OPENSEES_BENCHMARK_PASS"
ANALYTICAL_STATUS = "ANALYTICAL_ONLY_PASS"
UNVERIFIED = "NOT_VERIFIED"


def _finite_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}: numeric value required")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label}: finite value required")
    return result


def validate_directory(folder):
    """Fail closed on absent cases, mixed code fingerprints and false PASS claims.

    This gate validates the provided report data and its internal consistency;
    it does NOT rerun OpenSees or establish a CSI/ETABS model match.
    """
    folder = Path(folder).expanduser().resolve()
    results = []
    issues = []
    code_hashes = set()
    versions = set()
    solver_versions = set()
    metric_total = 0
    for case, count in EXPECTED.items():
        path = folder / (case + ".json")
        if not path.is_file():
            issues.append(f"{case}: MISSING_RESULT")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict) or data.get("case_id") != case:
                raise ValueError("case identity mismatch")
            expected_status = "ANALYTICAL_PASS" if case == "B12" else "PASS"
            if data.get("status") != expected_status:
                raise ValueError(f"status {data.get('status')!r}, expected {expected_status}")
            expected_solver = "NONE_ANALYTICAL_ONLY" if case == "B12" else "OpenSeesPy"
            if data.get("solver") != expected_solver:
                raise ValueError("solver identity incompatible with case type")
            if data.get("etabs_native_equivalence") != UNVERIFIED:
                raise ValueError("unsubstantiated ETABS equivalence assertion")
            metrics = data.get("metrics")
            if not isinstance(metrics, list) or len(metrics) != count:
                raise ValueError(f"expected {count} recorded metrics")
            tolerance = _finite_number(data.get("tolerance_relative"), "relative tolerance")
            if not 0 < tolerance < 1:
                raise ValueError("relative tolerance out of range")
            for index, metric in enumerate(metrics, 1):
                if not isinstance(metric, dict) or metric.get("passed") is not True:
                    raise ValueError(f"metric {index}: not passed")
                actual = _finite_number(metric.get("actual"), "actual")
                expected = _finite_number(metric.get("expected"), "expected")
                allowed = max(1e-7, tolerance * abs(expected))
                if abs(actual - expected) > allowed + 1e-10 * allowed:
                    raise ValueError(f"metric {index}: result exceeds stated tolerance")
            fingerprints = data.get("source_sha256")
            if not isinstance(fingerprints, dict) or len(fingerprints) != 1:
                raise ValueError("exactly one self-contained source fingerprint required")
            digest = fingerprints.get("ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py")
            if not isinstance(digest, str) or len(digest) != 64 or any(
                c not in "0123456789abcdefABCDEF" for c in digest
            ):
                raise ValueError("invalid source SHA256")
            versions.add(str(data.get("software_version")))
            code_hashes.add(digest.lower())
            if case != "B12":
                solver_versions.add(str(data.get("solver_version")))
            metric_total += len(metrics)
            results.append({"case_id": case, "status": NATIVE_STATUS if case != "B12"
                            else ANALYTICAL_STATUS, "metrics_passed": len(metrics)})
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            issues.append(f"{case}: {exc}")
    if len(versions) != 1:
        issues.append("MIXED_OR_MISSING_STUDIO_VERSIONS")
    if len(code_hashes) != 1:
        issues.append("MIXED_OR_MISSING_STUDIO_SOURCE_HASHES")
    if len(solver_versions) != 1 or "unavailable" in solver_versions:
        issues.append("MIXED_OR_UNKNOWN_NATIVE_SOLVER_VERSION")
    # A symmetric 6x6 m component patch can conserve load with nonconverged
    # deflection; do not infer the thesis MESH_04/08/16 result has converged.
    return {
        "schema": "thesis-studio-independent-benchmarks-v1",
        "status": "EVIDENCE_CONSISTENT" if not issues else "EVIDENCE_REJECTED",
        "native_component_cases_passed": len([r for r in results if r["status"] == NATIVE_STATUS]),
        "analytical_only_cases_passed": len([r for r in results if r["status"] == ANALYTICAL_STATUS]),
        "metrics_passed": metric_total,
        "studio_version": sorted(versions)[0] if len(versions) == 1 else None,
        "studio_source_sha256": sorted(code_hashes)[0] if len(code_hashes) == 1 else None,
        "openseespy_version": sorted(solver_versions)[0] if len(solver_versions) == 1 else None,
        "cases": results,
        "issues": issues,
        "thesis_model_equivalence": UNVERIFIED,
        "thesis_32_support_reaction_equivalence": UNVERIFIED,
        "thesis_mesh_convergence": UNVERIFIED,
        "thesis_full_record_nltha": UNVERIFIED,
        "note": "Independent component benchmark consistency only. Not native ETABS reproduction or model acceptance."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True,
                        help="Private local directory with B01.json through B12.json")
    parser.add_argument("--out", required=True,
                        help="Private local JSON summary filename; never commit raw runs")
    args = parser.parse_args(argv)
    report = validate_directory(args.results)
    target = Path(args.out).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: native={report['native_component_cases_passed']} "
          f"analytical={report['analytical_only_cases_passed']} "
          f"metrics={report['metrics_passed']}")
    return 0 if report["status"] == "EVIDENCE_CONSISTENT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
