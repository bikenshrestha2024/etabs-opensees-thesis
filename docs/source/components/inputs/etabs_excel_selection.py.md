# ETABS Excel source selection — role and provenance

[REF components/inputs/etabs_excel_selection.py]

This module classifies **user-selected local** ETABS Excel workbooks without
modifying files, changing ETABS model settings, inventing output data or
requesting source upload. The roles are:

- `analysis`: one completed analyzed `Analysis Export` workbook, normally
  `Analysis Export ULS 3 storey latest_compressed.xlsx`. The GUI's original
  full-table picker supports a genuine Joint Reactions CSV separately.
- `assignment`: optional original `Assignment Export` workbook (geometry,
  materials, frame section definitions, end offsets). A beam-force export
  cannot stand in for material/section assignment.
- `beam`: all `Beam Forces Element 1/2/3` workbook parts, or an Excel
  workbook with several `Element Forces - Beams` worksheets. Files are
  sorted by filename and their original bytes are never modified.

The GUI can now select all sources with **one Ctrl/Shift multi-select dialog**.
It rejects more than one analyzed export in the same selection instead of
silently choosing between regular and compressed versions. A beam-only
workbook is rejected when used as the full-table source. Role classification
is a **convenience** based on names and sheet inventories; downstream source
EDB SHA-256 and numerical evidence checks remain independent.

`tests/test_etabs_excel_source_selection.py` verifies disambiguation,
multiple selection, the presence of three split workbook parts, and GUI
wiring. Exported sheets can exceed Excel's one-million-row limit across all
parts; the matching beam-force consolidation is performed by
`components.validation.etabs_split_beam_forces` into CSV using a temporary
disk-backed SQLite index.

**Not certified:** source ETABS gravity case matching, complete export,
32/76/97 nodal reaction equivalence or NBC engineering approval.

## No Ctrl-click needed: folder auto-discovery

The Gravity GUI also offers **Auto-find Beam 1/2/3 in folder**. Select the
folder containing the numbered `Beam Forces Element N` workbooks. The
selector identifies consecutive part numbers, sorts them numerically,
rejects gaps and duplicate claims for one number, and asks you to confirm
the exact filenames. It does not inspect or modify the source workbook
contents until the explicit Validate + register + consolidate operation.
For workbook exports containing three beam-force worksheets inside a single
file, use the multi-file dialog instead of the numbered-folder helper.

## Partial analysis lots — gravity picker guard (2026-11-27)

The offline gravity reaction reader requires exactly one worksheet named Joint Reactions (case-insensitive, stripped). The gravity picker now checks the same condition before assigning an XLSX/XLSM source. A CSV remains subject to the downstream header/case checks. Analysis result and topology lots are valid local audit inputs, but their story-section forces are not joint reactions. Use the existing multi-lot audit command for these inputs; do not register them as an authoritative gravity reference. This does not change the single-workbook registration API, physical support mapping or solver inputs.

## Multi-lot worksheet-owner catalog (2026-11-27)

The new opt-in `build_analysis_table_catalog(paths)` indexes explicitly selected local workbook worksheet names and SHA-256 values. `resolve_analysis_table(catalog, name)` returns the unique original workbook and exact worksheet title, verifying its bytes and worksheet identity again. Repeated titles are ambiguous (not merged); identical workbook bytes, missing names and modified files fail closed. The existing full-table picker and registration API are unchanged. The catalog is a **reference routing index**, not a merged model, complete table-content scan or same-EDB certificate. Readers must still validate units, schema, case/step, and the source identity after streaming results. Keep the private index out of public commits.

The first- and second-lot reference parser supplies an `inspect_workbook`
callback to the catalog. This lets it read the known worksheet rows from the
same open, read-only workbook before the catalog verifies the source hash again.


### Complementary split selection

The default single-analysis classifier remains strict. Gravity opts into `split_analysis=True`: distinct worksheet owners are allowed, overlap except Program Control is rejected, and the unique Joint Reactions owner is routed to the existing gravity field. The full `analysis_files` selection remains available for the combined importer. Selection alone cannot establish EDB identity.
