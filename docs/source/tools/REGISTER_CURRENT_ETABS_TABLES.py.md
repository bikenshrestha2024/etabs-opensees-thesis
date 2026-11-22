# Register current native ETABS tables locally

**Source:** `tools/REGISTER_CURRENT_ETABS_TABLES.py`.

Run from the updated repository with actual local copies of the uploaded workbooks:

```powershell
python tools/REGISTER_CURRENT_ETABS_TABLES.py --export-root "D:\Thesis Opensees\ETABS 11-21-2026\1" --analysis "D:\MySource\Analysis Export ULS 3 storey latest_compressed.xlsx" --beam-1 "D:\MySource\Beam Forces Element 1 latest.xlsx" --beam-2 "D:\MySource\Beam Forces Element 2 latest.xlsx" --beam-3 "D:\MySource\Beam Forces Element 3 latest.xlsx"
```

The program checks source EDB availability, workbook format and sheet inventories, separates the three beam-force records and writes just a small manifest inside `01_ETABS_EXPORT/00_MANIFEST`. If the analysis workbook also contains every mandatory native frame-assignment and offset worksheet, it can serve as `etabs_assignment`; otherwise pass `--native-assignment` with the original complete ETABS workbook.

It does **not** infer that any of these workbooks match a revised 12 m shear-wall model merely from filenames. Verify actual source ETABS EDB provenance and row-level wall/element mappings separately; do not use the manifest as engineering validation.
