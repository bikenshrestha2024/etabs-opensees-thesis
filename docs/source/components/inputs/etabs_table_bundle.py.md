# ETABS current analysis and beam-force table provenance

**Source:** `components/inputs/etabs_table_bundle.py`.

The user's current ETABS analysis tables and three separate `Beam Forces Element` workbooks are registered **by exact local path and SHA-256** under the original source EDB's `01_ETABS_EXPORT/00_MANIFEST/PROJECT_SOURCES.private.json`. The registration is on-PC only: no workbook is uploaded to GitHub, renamed, moved or edited. Source model EDB SHA is required. The registry includes sheet-name inventories, file sizes and source-path provenance for each role. Files with the same paths assigned to different roles or identical beam-force workbook contents are rejected.

The role `etabs_full_table` is available through the existing `registered_project_source` resolver, including when the active model is a nested `02_MODEL/REBUILDS/VERIFIED_CLEAR_BEAM` version. `etabs_assignment` is registered only when the chosen source has the required eight ETABS material/frame/offset/loads sheets; otherwise it must be supplied separately. Beam force roles are inventoried but not consumed as solver results without independent element-ID, load-case, coordinate-axis and unit checks.

**This is file registration, not physical ETABS/OpenSees agreement.** Spreadsheet contents, shell properties, wall connectivity, loads, floor weights, end offsets, support reactions, and NLTHA remain separate engineering gates.

## Split analysis-export all-sheet audit

The existing registration tool has a separate read-only audit mode for any number of explicitly selected analysis lots. It uses openpyxl read_only, resets advertised worksheet dimensions, scans every populated cell including hidden sheets, counts nonempty rows and typed cells, records formula/error counts, hashes typed contents with cell coordinates and verifies the input ZIP hash before and after the scan. The first three populated rows (up to 40 cells each) help identify headers and units; evidence-family names are discovery hints only. Repeated sheet titles and identical cell-content fingerprints are reported without deleting or merging rows. A failed lot or sheet remains an explicit incomplete result; remaining files are still scanned. Nonworksheet tabs are reported separately. Private JSON output stays local. The audit does not replace the source-bound single-workbook registration or silently feed partial data to gravity, MRSM, ESM or NLTHA. Source EDB/case identity, native analytical connectivity, result schemas, units, completeness and engineering equivalence require separate evidence.

## Import ETABS analysis reference results

`read_analysis_reference()` reads explicitly selected workbooks with a common
schema. The first-lot tables contain story, member, energy and response-spectrum
results. The second-lot tables contain joint coordinates, object and element
connectivity, modal periods and frequencies, participation factors, mass and
load participation ratios, and direction factors. The third lot adds joint
reactions, drifts, displacements, velocities and accelerations. The fourth lot
adds integrated wall reactions, shell stresses and strains, group nonlinear
energy, frame and shell joint forces, and column and brace station forces.
Program Control metadata is recorded for the workbook that provides it.
The numeric parser uses the units declared in each table.

`ETABS_ANALYSIS_REFERENCE_V1` uses the worksheet-owner index's file identities.
A table's `file_index` is the zero-based position in `files`. The table has ordered
`columns` and matching row arrays that start with the original 1-based
worksheet row number. `source_units` and `units` describe numeric fields.
The importer converts mm, mm/sec and mm/sec² to m, m/s and m/s²,
and MPa to kN/m². Percentages become dimensionless fractions, and mm/mm
strains keep their values as dimensionless ratios. Reported forces, moments,
energies, participation factors, and modal mass/stiffness retain their
declared kN-based units.
Mode numbers are integers and ETABS joint IDs are preserved as strings.

The importer detects repeated workbook paths and hashes, overlapping supported
tables, and duplicate keys in results. Exact repeated records in the frame
worksheet share one retained row, with every repeat listed in
`duplicate_worksheet_rows`. Edges that reuse an element name and differ in
ordered endpoints or other fields retain their own rows. `source_row_count`
counts all populated rows, and `unique_row_count` counts distinct rows
before filtering. Cases, steps, signs, directions and force locations are
preserved. Relative and absolute responses, joint and design reactions, and
distinct shell faces or element stations keep their worksheet identities even
when values match. Formulas are never evaluated.

### SQLite storage for larger imports

Supply `row_database` to `read_analysis_reference()` or select SQLite from the
CLI. The manifest has schema `ETABS_ANALYSIS_SQLITE_REFERENCE_V1`.
Each table has a `table_id` that refers to `reference_tables`.
`reference_rows` has `worksheet_row`, `case_name` and `values_json`.
The value array follows the manifest's `columns` after its first
`worksheet_row` entry. `source_row_aliases` points each repeated worksheet row
to its retained position. Exact repeated records within an individual
third- or fourth-lot worksheet share one stored row. Identity uses the
source cell values before scaling. Distinct records retain their own
positions. Blank numeric cells in these worksheets remain null and
are counted per column in `blank_measure_counts`. The manifest records the
stored count after filtering and the database SHA-256.

```sql
SELECT r.worksheet_row, r.values_json
FROM reference_rows AS r
JOIN reference_tables AS t USING (table_id)
WHERE t.worksheet = 'Joint Reactions' AND r.case_name = ?
ORDER BY r.worksheet_row;
```

Checks use all loaded rows before any case filter. Reported periods are
compared using exact modal case names and mode numbers. Disagreement stops
publication. Missing modal keys and unresolved joint references appear in
`checks` when the corresponding baseline table is available. These checks
are confined to the available workbook tables. The source EDB hash remains
unset and the engineering status is unverified. A numerical comparison still
requires matching native EDB and case definitions, compatible response
conventions, and the corresponding OpenSees run.

`read_first_lot_reference()` and the original single-first-lot CLI usage
keep the `ETABS_FIRST_LOT_REFERENCE_V1` layout.

[Command-line usage](../../tools/REGISTER_CURRENT_ETABS_TABLES.py.md#import-etabs-analysis-reference-results)

### Source display diagnostics

The three story drift/displacement tables now include additive
`source_display_diagnostics` metadata with counts and original worksheet row
numbers, computed over all unique source rows **before** case filtering in
both JSON and SQLite storage. A zero reported average is flagged as unresolved
at the reported precision, not a physical zero or a code finding. The `1/0`
reciprocal text is flagged separately, including the subset with nonzero
numeric drift. Raw ratio, drift, text, case and step are unchanged. The flags
are not a pass/fail result for NBC torsion. The governing floor-end check
remains [the torsion checker](../validation/torsion_check.py.md), requiring
compatible opposite-end displacement results under centered loading; the
ETABS maximum/average tables are not that maximum/minimum criterion.

### Cumulative modal and drift-coordinate reference diagnostics

For split-lot imports, `checks.modal_mass_reference` summarizes the reported
modal mass fractions by exact modal case and each of the six DOFs. The mode
list, continuity from mode one, source cumulative final fraction, sum of
rounded contributions, maximum cumulative residual, decreasing and out-of-range
source rows, and first reported crossing of 90% are preserved. These are
reported source diagnostics, not a new NBC requirement for every DOF, a
verified native modal mass matrix, or a selected time-history scaling period.
No rounding of the source fractions or approval flags occurs.

When both joint and story-drift tables exist, `checks.story_drift_joint_reference`
checks each drift controlling point by the exact story and object label,
then by all three coordinates (absolute per-axis tolerance 0.001 m). Distinct
outcomes are unique, ambiguous, missing label and coordinate mismatch; all
exception source worksheet rows are retained. The tolerance is a reference
comparison choice, not a native mesh-merging tolerance. Neither matching
coordinates nor modal mass can establish native restraints or ETABS/OpenSees
physical equivalence. Both checks execute before exact case filtering for JSON
and SQLite; original values, earlier FIRST LOT display diagnostics and
engineering acceptance boundaries are unchanged.

### Joint response and static reaction reference diagnostics

When joint topology and joint-level response tables coexist, the importer checks
all unique source rows before case filtering against the exact exported element
ID, story and object label. Missing labels, unknown IDs and mismatches are counted
separately; unresolved IDs and up to 100 example worksheet rows per exception type
are retained. These checks do not infer restraints or diaphragm constraints.

The Joint Reactions table also produces per-case/type/step reference summaries
for linear static unstepped cases and explicit step-by-step cases only. Modal,
response-spectrum, combination and time-history envelopes are excluded from
force summation. Repeated joint IDs within a group and incomplete six-component
vectors block its sums and zero/nonzero classification; no row is silently
corrected or removed. Only the three global forces are summed; joint moments
require a common origin and compatible force transformation. Source zero/nonzero
reaction sets do not define physical supports. The user's 32 physical supports
plus 44 mesh points and full 1D+1L gravity benchmark remain unchanged. A matching
native model, load case and analysis state are still required before using the
reference for solver acceptance. All data and row-level diagnostics stay private.
