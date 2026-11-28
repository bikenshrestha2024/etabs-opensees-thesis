# Audit ETABS analysis lots for consistency

**Source:** `tools/audit_etabs_lot_consistency.py`. Uses [`components/validation/etabs_lot_consistency.py`](../../../components/validation/etabs_lot_consistency.py).

```powershell
python tools/audit_etabs_lot_consistency.py `
  --analysis-files LOT1.xlsx LOT2.xlsx LOT3.xlsx LOT4.xlsx LOT5.xlsx LOT6.xlsx `
  --duplicate-check-files LOT4_part_1.xlsx LOT4_part_2.xlsx LOT4_part_3.xlsx `
  --output ETABS_LOT_CONSISTENCY_AUDIT.json
```

* `--analysis-files`: the distinct lots ingested as ONE reference. Never pass a combined lot together with its parts: `read_analysis_reference` rejects a table that two workbooks both carry.
* `--duplicate-check-files`: workbooks scanned only for the all-sheet overlap audit, so a combined lot that repeats its parts is reported.
* The run scans every populated cell twice (all-sheet audit, then reference ingest; roughly 20 minutes for the six-lot export on two cores) and refuses to overwrite an existing report.
* The report keeps file names, SHA-256, worksheet inventories and aggregate diagnostics; it writes no local path and no model rows. Review it before publishing: it contains model-derived aggregates.
* Source workbooks are opened read-only and are never moved or uploaded.
