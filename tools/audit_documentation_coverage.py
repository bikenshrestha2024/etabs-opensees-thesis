"""Inventory active Python module/test source guides without importing native solvers.

[REF docs/review/20261112_IMPLEMENTATION_VERIFICATION_REGISTER.md]
Path coverage is NOT semantic, numerical, security or NBC acceptance.
Windows / Spyder / conda-forge Python 3.12; standard library only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def audit_guides(root):
    """Count active source-guide coverage, without declaring quality.

    [REF docs/review/20261112_IMPLEMENTATION_VERIFICATION_REGISTER.md]
    """
    root = Path(root).resolve()
    groups = {}
    for group in ("components", "tests"):
        files = sorted(
            p for p in (root / group).rglob("*.py")
            if p.is_file() and "__pycache__" not in p.parts
        ) if (root / group).is_dir() else []
        covered, missing = [], []
        for source in files:
            relative = source.relative_to(root).as_posix()
            guide = root / "docs" / "source" / (relative + ".md")
            (covered if guide.is_file() and guide.stat().st_size > 0 else missing).append(relative)
        groups[group] = {
            "source_files": len(files),
            "guides_present_nonempty": len(covered),
            "guides_missing_or_empty": len(missing),
            "missing_paths": missing,
        }
    return {
        "schema": "THESIS_DOCUMENTATION_PATH_COVERAGE_V1",
        "groups": groups,
        "status": (
            "COMPONENT_GUIDE_PATHS_COMPLETE"
            if groups["components"]["source_files"] > 0
            and not groups["components"]["missing_paths"]
            else "COMPONENT_GUIDE_PATHS_INCOMPLETE"
        ),
        "limitations": (
            "Only source-guide existence and nonempty size are measured. "
            "A guide can be outdated or incomplete; process explanations, "
            "actual author and reviewer, DOI, numerical validation and native "
            "model checks still require human source-grounded review."
        ),
    }


def main(argv=None):
    """Run offline guide scan and optionally save JSON to a local folder.

    [REF docs/review/20261112_IMPLEMENTATION_VERIFICATION_REGISTER.md]
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--fail-on-missing-component-guides",
                        action="store_true")
    options = parser.parse_args(argv)
    result = audit_guides(options.root)
    if options.output is not None:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(json.dumps(result, indent=2) + "\n",
                                  encoding="utf-8")
    print(json.dumps(result, indent=2))
    if options.fail_on_missing_component_guides and (
        result["status"] != "COMPONENT_GUIDE_PATHS_COMPLETE"
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
