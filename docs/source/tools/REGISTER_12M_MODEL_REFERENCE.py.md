# Register model-aligned 12 m workbook on your own PC

**Source:** `tools/REGISTER_12M_MODEL_REFERENCE.py`.

Use *after* the rebuilt model's source geometry gate has passed and the original ETABS EDB file is present:

```powershell
python tools/REGISTER_12M_MODEL_REFERENCE.py --rebuild-dir "D:\Thesis Opensees\ETABS 11-21-2026\1\02_MODEL\REBUILDS\VERIFIED_CLEAR_BEAM\<timestamp>" --current-workbook "D:\Thesis\Inputs\NBC105_2025_95m_12m_MODEL_ALIGNED_V10_7.xlsx" --state ULS
```

No Excel workbook or EDB bytes are changed, copied into GitHub or uploaded. A successful registration prints workbook and EDB SHA256, records the exact private local path in that rebuilt source's `00_SOURCE_MANIFEST`, and permits the ESM input reader to import recognized NBC Calculator and/or SCALING SUMMARY sheets on the *same* ULS/SLS source.

The workbook must be genuine OOXML and (when `SCALING SUMMARY` exists) B4 must identify an on-disk EDB byte-identical to the current project source; otherwise the process fails closed. Do not override this failure with a similarly named historical workbook. Verify the workbook's formulas and values independently even after registering.
