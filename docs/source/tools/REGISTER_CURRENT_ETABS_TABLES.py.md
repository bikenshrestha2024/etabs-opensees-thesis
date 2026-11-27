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

## Import first-lot reference results

```powershell
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-reference "D:\ETABS\Analysis Export ULS 3 storey latest_compressed FIRST LOT.xlsx" --reference-output "..\first_lot_reference"
```

Use a new local output directory outside the Git checkout. The command writes
`FIRST_LOT_REFERENCE.private.json` with normalized rows and workbook provenance.
To export rows for specific cases, repeat the exact ETABS name with
`--reference-case "EQX" --reference-case "RSX P Delta"`. Case filtering preserves
the workbook-wide case counts and leaves tables without a case column available.
Exit 2 means the import could not publish a reference. The source workbook is
read-only. The reference mode is independent of the multi-lot audit and the
full-table registration used by solver workflows.

See the [reference data and unit contract](../components/inputs/etabs_table_bundle.py.md#import-first-lot-reference-results).
