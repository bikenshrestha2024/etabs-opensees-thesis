# Audit beam-force shards

**Source:** `tools/audit_beam_force_shards.py`. Uses [`components/validation/etabs_beam_force_shards.py`](../../../components/validation/etabs_beam_force_shards.py).

```powershell
python tools/audit_beam_force_shards.py `
  --beam-files Beam_Forces_Element_1.xlsx Beam_Forces_Element_2.xlsx Beam_Forces_Element_3.xlsx `
  --frame-workbook ANALYSIS_LOT_2.xlsx `
  --output ETABS_BEAM_FORCE_SHARDS_AUDIT.json
```

Workbooks are opened read-only (`reset_dimensions`) and streamed; a run over the three real shards takes a few minutes. The report holds file names, SHA-256 and aggregates only, never rows or local paths, and refuses to overwrite. Exit status 0 means the shards form one complete, consistent table; 1 means errors were found.
