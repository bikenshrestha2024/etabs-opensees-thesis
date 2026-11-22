# Export-case output layout repair (copy-only)

**Source:** `tools/repair_project_output_layout.py`.

## Intended use

Provides an explicit **dry run by default** and a deliberate `--apply` option to categorize loose *generated* root files via the repository's established `components.inputs.export_mirror` and to create SHA256-verified snapshots of existing ESM/Rayleigh artifacts under `03_ESM/REVIEW_SNAPSHOTS/HISTORICAL_<case>`. The tool never moves, deletes, edits, or rewrites the original solver files and never changes an EDB, restraints, mass or NBC engineering equation.

Run from your checked-out repository on the same Windows machine as the local export:

```powershell
python tools/repair_project_output_layout.py "D:\PROJECT\EXPORT_CASE"
python tools/repair_project_output_layout.py "D:\PROJECT\EXPORT_CASE" --apply
```

The first command only reports counts. `--apply` copies existing recognized ESM/Rayleigh case files into a clearly identified historical **review** snapshot. Neither mode executes the solver or certifies code compliance. Original files remain in the legacy tree because old runner paths and referenced manifests can depend on them.

If a current root source has changed after its earlier categorized copy was created, the tool preserves the old copy and stores the new SHA256-identified bytes under `01_ETABS_EXPORT/09_REVIEW/ROOT_SOURCE_REVISIONS`. The report explicitly marks the primary categorized mirror as stale; it does not overwrite historical evidence or mark it current. No automatic removal is safe before a full writer/reader/native Windows regression.

## Source identity and safety

Never push the resulting local manifests to public GitHub: filenames, model identifiers and source paths can contain confidential information. It fails closed for conflicting destination checksums and refuses linked source/target paths. A partial copy on a disk error must be reviewed; manifest publication occurs only at the end.

`tests/test_canonical_esm_output_routing.py` checks dry-run behavior, safe copying, unchanged originals, repeated application, collision rejection and the new `03_ESM/RUNS` routing. Engineering native verification remains separate.

[REF `AGENTS.md` canonical folder policy; `components/inputs/output_layout.py`; `components/inputs/export_mirror.py`.]
