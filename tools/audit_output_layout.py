"""Read-only audit of one run directory against the uniform output-folder standard.

[REF docs/OUTPUT_FOLDER_STANDARD.md]
[REF docs/source/components/inputs/output_contract.py.md]

Checks that ``<export>/<stage>/RUNS/<state>/<case>/<run id>/`` contains exactly
the eight ``output_contract.RUN_SUBFOLDERS`` and nothing else, that no entry is
a symbolic link, and passes the ``inspect_case_manifest`` issues through
unchanged.  It never creates, moves, deletes or follows anything, and it reads
only directory names plus the case manifest.  A layout PASS is not solver
success and not engineering acceptance.

    python tools/audit_output_layout.py RUN_DIR [--json]    # exit 0 if ok else 1

Windows / Spyder / Python 3.12; standard library plus ``components.inputs.output_contract``.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.inputs.output_contract import (  # noqa: E402
    RUN_SUBFOLDERS, inspect_case_manifest)

STATUS = "LAYOUT_ONLY_NOT_ENGINEERING_ACCEPTANCE"


def audit_run_layout(run_dir):
    """[REF docs/OUTPUT_FOLDER_STANDARD.md]
    Return the layout verdict for one run directory without modifying it.

    ``missing``: required subfolders that are absent or not real directories.
    ``unexpected``: any other entry (file or folder) directly in the run dir.
    ``symlinks``: linked entries (never followed); the run dir itself if linked.
    ``manifest_issues``: ``inspect_case_manifest(...)["issues"]`` unchanged.
    """
    raw = Path(os.fspath(run_dir)).expanduser()
    result = {"run_dir": str(raw), "ok": False, "missing": [], "unexpected": [],
              "symlinks": [], "manifest_issues": [], "status": STATUS}
    if raw.is_symlink():
        result["symlinks"] = [str(raw)]
        result["missing"] = list(RUN_SUBFOLDERS)
        result["manifest_issues"] = inspect_case_manifest(raw)["issues"]
        return result
    present_dirs, unexpected, symlinks = set(), [], []
    if raw.is_dir():
        with os.scandir(raw) as entries:
            for entry in sorted(entries, key=lambda e: e.name):
                if entry.is_symlink():
                    symlinks.append(entry.name)
                    continue
                if entry.name in RUN_SUBFOLDERS and entry.is_dir(follow_symlinks=False):
                    present_dirs.add(entry.name)
                elif entry.name not in RUN_SUBFOLDERS:
                    unexpected.append(entry.name)
    # A subfolder name that is a plain file is neither present nor unexpected-by-name,
    # so it is reported as missing.
    result["missing"] = [n for n in RUN_SUBFOLDERS if n not in present_dirs]
    result["unexpected"] = unexpected
    result["symlinks"] = symlinks
    result["manifest_issues"] = inspect_case_manifest(raw)["issues"]
    result["ok"] = not (result["missing"] or unexpected or symlinks
                        or result["manifest_issues"])
    return result


def main(argv=None):
    """[REF docs/OUTPUT_FOLDER_STANDARD.md]
    CLI entry point; exit code 0 when the layout is ok, otherwise 1."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("run_dir")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    args = parser.parse_args(argv)
    result = audit_run_layout(args.run_dir)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("%s: %s (%s)" % (result["run_dir"], "OK" if result["ok"] else "NOT OK",
                               result["status"]))
        for key in ("missing", "unexpected", "symlinks", "manifest_issues"):
            if result[key]:
                print("  %s: %s" % (key, ", ".join(result[key])))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
