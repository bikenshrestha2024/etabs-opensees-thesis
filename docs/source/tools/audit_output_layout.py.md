# tools/audit_output_layout.py — source guide

**What:** read-only audit of one run directory against the [uniform output-folder standard](../../OUTPUT_FOLDER_STANDARD.md). `audit_run_layout(run_dir)` returns `{run_dir, ok, missing, unexpected, symlinks, manifest_issues, status}`.

**When:** after a run, or before archiving or citing one, to confirm it follows `create_case_run`'s layout.

**Why:** producers differ (see the standard's producer table); a quick check shows which run folders are non-conforming without touching them.

**How:** Python standard library plus `components.inputs.output_contract` (`RUN_SUBFOLDERS`, `inspect_case_manifest`, reused unchanged; its `issues` are passed through as `manifest_issues`). It lists the run directory with `os.scandir`, never follows symlinks (a linked run dir or entry is reported in `symlinks`), uses `pathlib` so Windows paths work, and never creates, moves or deletes anything. `ok` requires all eight subfolders as real directories, no other entry, no symlink and no manifest issue. Status is always `LAYOUT_ONLY_NOT_ENGINEERING_ACCEPTANCE`.

**Where:** source `tools/audit_output_layout.py`; tests `tests/test_audit_output_layout.py`. CLI: `python tools/audit_output_layout.py RUN_DIR [--json]`, exit 0 if ok else 1.

**Which:** directory names and `00_INPUT_SOURCE/CASE_MANIFEST.json` only. It opens no model, imports no solver and does not touch any EDB.

**Who:** software maintainer owns the tool; the thesis author owns any engineering reading of a run.
