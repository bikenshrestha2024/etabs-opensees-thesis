# Saved 3D viewer refresh — source-safe presentation updates

**Module:** `components/ui/saved_view_refresh.py`

## Purpose

Refresh viewer controls and load legends in the four existing ETABS source-view HTML files **without launching CSI ETABS, constructing ShellMITC4 cells, rerunning OpenSees, or modifying model data**.

CLI:

```powershell
python -m components.ui.saved_view_refresh "D:\Thesis Opensees\ETABS 11-16-2026\4"
```

GUI: Import → **Refresh saved 3D view controls (no ETABS/model assembly)**.

### Page-specific behavior

- Structural overview and connectivity viewers: preserve the full shared Prefix → Storey → Element inspector (B/C/BR/CO/BT/CT/FVD/BRB plus shear walls/floors), exact ETABS and OpenSees ID mapping, and existing filters. No structural page layout is forcibly collapsed.
- 3D load and floor-plan load viewers: shared element inspector collapsed at startup, with keyboard-accessible **Show element inspector / exact IDs** toggle. Detailed exact ID lookup is still available; the load controls remain visible.
- Load views show the highest numbered exported storey initially. **All storeys** remains explicitly available in the existing dropdown.
- Use a compact custom legend with one token per distinct load pattern instead of Plotly's repeated per-storey entries. Original graph traces, hover records, UDL values and source element IDs are untouched.

### Safety and provenance

- The offline refresher requires the original source connectivity JSON and a successful complete-export report with zero assembly errors. It refuses missing required HTML, linked HTML, linked evidence files and incomplete conversion reports.
- Backs up **all four original HTML files** before changing them, under `09_SOFTWARE_DIAGNOSTICS/VIEW_REFRESH_BACKUP/<UTC timestamp>/`. Records original and new SHA256 and source/report hashes.
- Uses same-directory temporary files and `os.replace` for per-file atomic updates, with rollback of already-modified files after errors.
- Repeated refresh is idempotent; no duplicate script or toolbar is added.
- The original FE assembled JSON, ETABS source audit CSV/JSON, model config, member IDs, loads, support mappings and validation reports are not edited.
- It does **not** reconstruct Plotly geometry from the raw source export, so old per-object heavy HTML still retains its original trace counts; to obtain the new trace batching, generate views with a new conversion or a dedicated future source-figure regeneration pass. This limitation is shown transparently in GUI/logs.

### New full conversions

`components/model/id_audit.py` applies the same UI controls automatically after its source-verified ID selector insertion. No additional ETABS API queries are added, and the exporter still performs its existing analysis assembly only once.

### Tests

`python -m unittest tests.test_saved_view_refresh -v` verifies page scope, exact IDs, collapse/default selector, custom legend insertion, source byte identity, backup manifest, idempotency, missing-view failure and incomplete-export rejection.

Reference: `REVIEW_MAIN/08_SOFTWARE_SECURITY/20261116_VISUALIZATION_COMPACTION_AND_ASSEMBLY_PROFILING.md`.
