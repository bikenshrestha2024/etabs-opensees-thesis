# Register current native ETABS tables locally

**Source:** `tools/REGISTER_CURRENT_ETABS_TABLES.py`.

Run from the updated repository with actual local copies of the uploaded workbooks:

```powershell
python tools/REGISTER_CURRENT_ETABS_TABLES.py --export-root "D:\Thesis Opensees\ETABS 11-21-2026\1" --analysis "D:\MySource\Analysis Export ULS 3 storey latest_compressed.xlsx" --beam-1 "D:\MySource\Beam Forces Element 1 latest.xlsx" --beam-2 "D:\MySource\Beam Forces Element 2 latest.xlsx" --beam-3 "D:\MySource\Beam Forces Element 3 latest.xlsx"
```

The program checks source EDB availability, workbook format and sheet inventories, separates the three beam-force records and writes just a small manifest inside `01_ETABS_EXPORT/00_MANIFEST`. If the analysis workbook also contains every mandatory native frame-assignment and offset worksheet, it can serve as `etabs_assignment`; otherwise pass `--native-assignment` with the original complete ETABS workbook.

It does **not** infer that any of these workbooks match a revised 12 m shear-wall model merely from filenames. Verify actual source ETABS EDB provenance and row-level wall/element mappings separately; do not use the manifest as engineering validation.

## Multi-file beam-force picker (2026-11-22)

The registered beam force evidence is not limited to three parts. Select all
`Element Forces - Beams` Excel workbooks (any positive number) at once:

```powershell
python tools/REGISTER_CURRENT_ETABS_TABLES.py --export-root "D:\\Thesis Opensees\\ETABS 11-22-2026" --analysis "D:\\ETABS Source\\Analysis Export.xlsx" --select-beams
```

For noninteractive automation use `--beam-files FILE1.xlsx FILE2.xlsx ...`.
The legacy `--beam-1/2/3` flags still work when all three are supplied.
Every chosen path must be unique, its bytes must differ from other beam parts,
and its SHA-256 is stored in the private canonical source registry. Replacing
the selection removes stale earlier beam-part roles. This is inventory only;
combine and verify stations with `components.validation.etabs_split_beam_forces`.
Never interpret selected beam parts as a passed gravity-reaction comparison.

## Audit multiple analysis lots without registration

For split analysis exports, scan every worksheet locally without needing ETABS or selecting beam files:

```powershell
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-files "Analysis Export ULS 3 storey latest_compressed FIRST LOT.xlsx" "Analysis Export ULS 3 storey latest_compressed SECOND LOT.xlsx" --audit-output "ETABS_Analysis_Lots_Audit.private.json"
```

Use the full local input paths if the files are not in the current directory. Use a new private JSON filename each run. Progress prints before each sheet. The report contains per-sheet row/cell counts, candidate families, header previews, duplicate titles/content and read failures. Exit 0 means the selected worksheets were scanned, not validated; exit 2 means incomplete scanning. Keep the report private (it may contain project data). This mode does not register or combine lots into solver inputs; existing registration flags remain unchanged.

## Import ETABS analysis reference results

```powershell
$firstLot = "D:\ETABS\Analysis Export ULS 3 storey latest_compressed FIRST LOT.xlsx"
$secondLot = "D:\ETABS\Analysis Export ULS 3 storey latest_compressed SECOND LOT.xlsx"
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-reference $firstLot $secondLot --reference-output "..\etabs_analysis_reference"
```

Use a new local output directory outside the Git checkout. The command writes
`ETABS_ANALYSIS_REFERENCE.private.json` with normalized rows and separate provenance
for each workbook. Either workbook can also be selected on its own. A single
first-lot selection continues to write `FIRST_LOT_REFERENCE.private.json`
with its original schema.

To export rows for specific cases, repeat the exact ETABS name with
`--reference-case "EQX" --reference-case "Modal Ritz"`. Case filtering preserves
source coverage counts and keeps tables without a case column. The import
stops before publication if it detects a duplicate workbook, an overlapping
supported table, malformed data, or conflicting modal periods. Exit 2
means the import could not publish a reference.

For all four lots, use the same command with SQLite storage so worksheet rows
are streamed to a private database.

```powershell
$thirdLot = "D:\ETABS\Analysis Export ULS 3 storey latest_compressed THIRD LOT.xlsx"
$fourthLot = "D:\ETABS\Analysis Export ULS 3 storey latest_compressed FOURTH LOT.xlsx"
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-reference $firstLot $secondLot $thirdLot $fourthLot --reference-storage sqlite --reference-output "..\etabs_four_lot_reference"
```

Three or more input files select SQLite by default. For a shorter selection that
contains the third or fourth lot, specify `--reference-storage sqlite`. The
output contains `ETABS_ANALYSIS_REFERENCE.private.json` and
`ETABS_ANALYSIS_ROWS.private.sqlite3`. Keep both files local. The JSON records
the database hash, the original workbook hashes, table units, and coverage
before exact-case filtering. The database contains the retained values and
the original worksheet row numbers for any exact repeats.

The command opens the workbooks read-only and produces a local reference for
comparison. The multi-lot audit and full-table solver registration use their
own commands.

[Reference data and unit contract](../components/inputs/etabs_table_bundle.py.md#import-etabs-analysis-reference-results)

## Index complementary analysis lots without merging

```powershell
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-files "FIRST LOT.xlsx" "SECOND LOT.xlsx" "THIRD LOT.xlsx" --table-index-output "ETABS_Analysis_Catalog.private.json"
```

Use the exact local file paths. This mode writes the worksheet owners and workbook
hashes. The source-selection module's `resolve_analysis_table` requires one
unambiguous owner. Reference import shares this index scan and also validates
the known first- and second-lot worksheet values. Use each mode in its own
invocation. The index reports source files for review and leaves solver
registration to the EDB-bound workflow.

## Combined analysis and beam reference publication

Use the six complementary analysis files and three native beam workbooks in explicit, separate arrays:

```powershell
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-reference $lots --reference-beams $beams --reference-storage sqlite --reference-output "..\\NINE_SOURCE_REFERENCE"
```

The combined mode preserves the existing analysis-table owner checks and uses the existing exact native all-case beam consolidator, rather than pretending that beam shards are disjoint analysis worksheets. No case filtering is permitted in this mode. Repeated source bytes and mixed source roles are rejected. Source hashes are rechecked before publishing the staged directory. The combined private index links and hashes the analysis manifest and beam manifest; the latter contains the CSV digest and final output path. Outputs are reference-only and do not register as a source EDB or solver input. A failure before publication leaves no new reference directory. Keep all generated reference data local. Native model and engineering acceptance remain separate.


### Verify a combined reference

```powershell
python tools/REGISTER_CURRENT_ETABS_TABLES.py --inspect-combined-reference "path\to\ETABS_COMBINED_REFERENCE.private.json" --audit-output "coverage.private.json"
```

For legacy indexes without beam paths, also supply `--beam-files` with the exact original beam files. Source and derived bytes, ownership and row counts are checked. Output coverage is reference-only, not native acceptance.


### Optional assembled-input mass comparison

Append `--assembled-mass-model PATH_TO_ASSEMBLED_MODEL_JSON` to `--inspect-combined-reference`. The inspector checks reference units and hashes the exact model JSON, then uses the canonical mass operator for the floor comparison. It writes residuals only; source identity, native mass matrix and code acceptance remain unverified.


### Original-object reference mass diagnostic

With `--inspect-combined-reference` and `--assembled-mass-model`, add all three of `--mass-source-connectivity`, `--mass-source-config` and `--etabs-reference-g`. Select the actual original connectivity and exact configuration associated with the assembled model. The configuration hash must match the model; the inspector records the connectivity and model hashes and checks original identities/coordinates and refined source mass replay. Reference gravity is an explicit comparison assumption, not an NBC constant change. The report is private and does not install new solver masses.


### Saved modal shape comparison

Use `--inspect-combined-reference INDEX --modal-shapes-csv CSV --etabs-modal-case "Modal Ritz" --audit-output NEW.private.json`. The inspector checks normalized units and hashes the selected saved shape CSV. Complete reference floor identity and common master coordinates are mandatory; saved shape and reference model identity remains unverified. The reference metric is not a native mass matrix.
