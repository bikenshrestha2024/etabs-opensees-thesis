# ETABS split beam-force source importer

**Implementation:** components/validation/etabs_split_beam_forces.py

## Purpose
Read ETABS Element Forces - Beams force-station rows when the native full-table XLSX sheet reached the 1,048,576 row Microsoft Excel cap. Multiple smaller workbook exports can be independently SHA-256 fingerprinted, deduplicated and emitted as UTF-8 CSV without a workbook row limit.

## Inputs and output
- Input: one or more local original ETABS .xlsx files with exactly one worksheet containing Story, Unique Name, Output Case and Station columns.
- Case gate: 1. DL + LL, not seismic 0.3L preload or 1.5(DL+LL).
- CLI: python -m components.validation.etabs_split_beam_forces OUTPUT_DIR PART1.xlsx PART2.xlsx PART3.xlsx
- Output: ETABS_Beam_Forces_Consolidated.csv and ETABS_Beam_Forces_Manifest.json in a new or empty output directory.
- Both originals and extra source workbooks remain unchanged and **must not be committed publicly**.

## Engineering checks
1. Rows require source member unique ID and output station; identity includes story, combination and available step type/number.
2. Overlap duplicates are checked across every imported column; numeric differences are allowed only within 1e-6 absolute and 1e-9 relative tolerance. Conflicts fail rather than overwrite.
3. The importer checks the case and column schema across source parts, and refuses missing or linked input files.
4. A successful source import does **not** prove ETABS table coverage where other station rows were never exported, source-model hash identity, original output-axis compatibility, rigid offsets or OpenSees joint reactions.
5. No model geometry, gravity load, stiffness, mesh, original file or solver response is modified.

## Validation
Run python -m unittest tests.test_etabs_split_beam_forces. Tests cover deduplication, conflicts, case mismatch, immutable source/output behavior. Native comparison still requires corresponding OpenSees beam forces mapped through the source frame unique-ID/segment connectivity, local axes, output stations and end-offset treatment.

Related root-cause review: REVIEW_MAIN/01_GRAVITY/20261116_CONSOLIDATED_ROOT_CAUSE_AND_BEAM_FORCE_AUDIT.md.
## 2026-11-22: multiple workbooks + multiple worksheets, beyond Excel row limit

The importer now handles **all** worksheets matching the ETABS
`Story / Unique Name / Output Case / Station` beam-force table signature,
not exactly one table per workbook. Select all separate
`Beam Forces Element 1/2/3` files, or a workbook containing three
beam-force sheets. Other unrelated ETABS tables are ignored.

The source workbook rows are streamed via read-only openpyxl, and a
temporary on-disk SQLite key/value index checks overlapping stations.
Memory is not proportional to total beam-force station count. The final
`02_RESULTS/ETABS_Beam_Forces_Consolidated.csv` is not subject to Excel's
1,048,576-row-per-sheet limit; do not re-import it to a single Excel sheet
and assume missing rows are an ETABS problem.

Every row carries story, member unique name, case, station and optional
step identity. Conflicting repeated rows stop the import before result
publication. Identical overlapping rows are counted and deduplicated.
Per-workbook source SHA256 and per-sheet row counts appear in the JSON
manifest. This is ETABS station-source evidence only and does not establish
joint reaction equivalence or completion of unexported stations.

For convenience the Gravity GUI has two options:
- `Select ALL ETABS Excel files together`: Windows Ctrl/Shift selection
  of one analyzed `Analysis Export`, optional `Assignment Export`, and
  all separate `Beam Forces Element` parts.
- `Select ALL ETABS Element Forces - Beams Excel parts`: chooses just the
  beam-force workbooks, with Ctrl/Shift selection.

The analyzed full-table input remains a **single authoritative analyzed
export**, e.g. `Analysis Export ULS 3 storey latest_compressed.xlsx`.
The assignment workbook and beam parts are separate input roles. A beam-only
workbook cannot be used as the analyzed joint-reaction source.


## Native ETABS unit row (2026-11-28)

Native station-force exports have a third row with explicit table units.
The shared streaming reader now skips only the exact native station and
force-unit signature immediately following the headers (m, kN, kN-m).
This is not a result and must not trip the case gate. Blank identity fields
on other rows remain invalid. Other or incomplete unit signatures are not
silently converted. The strict `1. DL + LL` single-case consolidator remains
strict: an all-case export must not be passed to it as an already-selected
gravity case. The separate beam/slab load-path diagnostic may select exact
cases explicitly; the all-sheet audit mode preserves every exported case.
Neither a source row-limit boundary nor a partial import establishes complete
station coverage or native equivalence.


## Explicit case projection for all-case beam split sources

The strict default still rejects any other case. For a native all-case
export, an explicit CLI selection is available:

```powershell
python -m components.validation.etabs_split_beam_forces NEW_PRIVATE_OUTPUT "Beam Forces Element 1.xlsx" "Beam Forces Element 2.xlsx" "Beam Forces Element 3.xlsx" --select-exact-case "1. DL + LL"
```

The corresponding API is `consolidate(paths, destination, case="1. DL + LL",
select_exact_case=True)`. Exact literal equality (not case folding) determines
selection. Source bytes are checked before and after reading. The manifest
distinguishes selected `source_rows` / `rows_read` from all streamed
`scanned_source_rows` / `rows_scanned`, reports excluded cases per source,
keeps sheets with zero selected rows and flags sheets reaching the native
Excel data-row limit. No selected rows means no publication. The original
gravity GUI remains strict; the CLI projection is an opt-in source-only
diagnostic, not a native solve. Excluded cases are not lost from their source
workbooks; use the all-sheet private audit for all-case evidence. The
station-overlap tolerance and legacy CSV identity are unchanged, and the
complete multi-file selection still requires separate coverage validation.
