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
