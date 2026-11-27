# ETABS current analysis and beam-force table provenance

**Source:** `components/inputs/etabs_table_bundle.py`.

The user's current ETABS analysis tables and three separate `Beam Forces Element` workbooks are registered **by exact local path and SHA-256** under the original source EDB's `01_ETABS_EXPORT/00_MANIFEST/PROJECT_SOURCES.private.json`. The registration is on-PC only: no workbook is uploaded to GitHub, renamed, moved or edited. Source model EDB SHA is required. The registry includes sheet-name inventories, file sizes and source-path provenance for each role. Files with the same paths assigned to different roles or identical beam-force workbook contents are rejected.

The role `etabs_full_table` is available through the existing `registered_project_source` resolver, including when the active model is a nested `02_MODEL/REBUILDS/VERIFIED_CLEAR_BEAM` version. `etabs_assignment` is registered only when the chosen source has the required eight ETABS material/frame/offset/loads sheets; otherwise it must be supplied separately. Beam force roles are inventoried but not consumed as solver results without independent element-ID, load-case, coordinate-axis and unit checks.

**This is file registration, not physical ETABS/OpenSees agreement.** Spreadsheet contents, shell properties, wall connectivity, loads, floor weights, end offsets, support reactions, and NLTHA remain separate engineering gates.

## Split analysis-export all-sheet audit

The existing registration tool has a separate read-only audit mode for any number of explicitly selected analysis lots. It uses openpyxl read_only, resets advertised worksheet dimensions, scans every populated cell including hidden sheets, counts nonempty rows and typed cells, records formula/error counts, hashes typed contents with cell coordinates and verifies the input ZIP hash before and after the scan. The first three populated rows (up to 40 cells each) help identify headers and units; evidence-family names are discovery hints only. Repeated sheet titles and identical cell-content fingerprints are reported without deleting or merging rows. A failed lot or sheet remains an explicit incomplete result; remaining files are still scanned. Nonworksheet tabs are reported separately. Private JSON output stays local. The audit does not replace the source-bound single-workbook registration or silently feed partial data to gravity, MRSM, ESM or NLTHA. Source EDB/case identity, native analytical connectivity, result schemas, units, completeness and engineering equivalence require separate evidence. The uploaded actual workbooks could not be read in the assistant environment; test evidence is synthetic only.

## Import first-lot reference results

`read_first_lot_reference()` reads one explicitly selected workbook. The schema
covers Program Control metadata, tributary area and live-load reduction,
energy components, story stiffness, max/average drift and displacement, story
forces, drifts and accelerations, spandrel and pier forces, and response
spectrum modal information. It validates the ETABS table titles, column names,
and source units in the third worksheet row. Program Control's displayed units
are provenance metadata. ETABS may display different units there.

The `ETABS_FIRST_LOT_REFERENCE_V1` JSON includes the workbook SHA-256, ETABS
version, encountered stories and cases, per-case counts, and missing or
unrecognized worksheet names. Each result table has ordered `columns` and
matching row arrays starting with the original 1-based worksheet row number.
`source_units` and `units` describe numeric measure columns. Length and
translational acceleration in mm and mm/sec² are divided by 1000. Forces
remain in kN, moments and reported energies in kN-m, periods in seconds, and
ratios are dimensionless. Rotational accelerations remain in rad/s².

Cases, envelope types, numbered steps, signs, directions, force components, and
top/bottom or left/right locations retain their source meaning. Rows with
duplicate result keys, unrecognized units in supported columns, or malformed
values stop publication. The workbook digest must remain stable across the
read. Formula content is never evaluated. Case counts and story lists cover
the source table even when the export filters rows to particular cases.

Workbook coverage does not establish the complete native ETABS result set.
The reference carries an unset EDB hash and unverified engineering status.
A numerical comparison still requires matching EDB and case definitions,
compatible result steps, locations and response conventions, and the matching
OpenSees run. The workbook contains reported ETABS results and supplies no
model or solver input through this import.

[Command-line usage](../../tools/REGISTER_CURRENT_ETABS_TABLES.py.md#import-first-lot-reference-results)
