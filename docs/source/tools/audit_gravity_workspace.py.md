# Local gravity workspace duplicate audit

**Source:** `tools/audit_gravity_workspace.py`.

This is a **read-only** filesystem audit for the user's selected ETABS export case. It scans the `02_GRAVITY` subtree and gravity-named evidence under historical `OpenSees_Analysis_Results`, hashes file bytes with SHA-256, and groups *exact byte-identical files*. It does not compare or approve structural reactions, merge solver runs, change any files, or upload private data.

Run locally on Windows:

```powershell
python tools/audit_gravity_workspace.py "D:\Thesis Opensees\ETABS 11-21-2026\1"
python tools/audit_gravity_workspace.py "D:\Thesis Opensees\ETABS 11-21-2026\1" --write
```

`--write` creates one time-stamped `02_GRAVITY/06_REVIEW/GRAVITY_WORKSPACE_AUDIT/<timestamp>/` folder with `EXACT_DUPLICATE_REVIEW.json` and `README_FIRST.txt`. This remains local; the default invocation prints only summary totals. Symlinked sources are refused and inaccessible paths are recorded as skipped. Large folders can take time to hash. Set `--max-files` to cap scanning.

**Do not delete duplicates automatically.** A byte-identical report belonging to two separate solver cases is still case-specific evidence; some snapshots are intentionally immutable. Treat the report as a disposition queue: confirm the exact source/model SHA, load profile, physical supports, solver completion, and registry links before deciding whether a particular review copy can be archived or discarded. Native ETABS–OpenSees equivalence is an independent engineering gate.
