# components/inputs/opensees_nbc_sync.py

**Purpose:** read-only NBC 105:2025 source-input synchronization with OpenSees-exported geometry/hashed directional Rayleigh results primary, source-matched Excel secondary, and read-only existing-ETABS OAPI geometry fallback.

**Main launcher:** [22_NBC105_INPUT_SYNC.py](../../../../22_NBC105_INPUT_SYNC.py)  
**Runbook:** [22_NBC105_OPENSEES_FIRST_INPUT_SYNC.md](../../../programs/22_NBC105_OPENSEES_FIRST_INPUT_SYNC.md)

## Main functions

- `_source_snapshot(export_dir,state)`: requires one matching ULS/SLS assembled JSON and story CSV, runs existing source-aware `import_project_inputs`; returns wall Aw candidates and explicit uniform/nonuniform/conflict status. No NBC design certification.
- `read_etabs_wall_profile(export_dir,sap=None)`: opt-in ETABS API geometry cross-check. Requires matching active source EDB. Only Get* methods and temporary unit changes; never Save/OpenFile/RunAnalysis, never modifies earthquake load/response-spectrum factors.
- `export_sync_report(report,output_dir,template=None)`: writes a fresh JSON source evidence file and new XLSX with a dedicated audited wall geometry tab. Original template and its calculator/scaling sheets are unchanged.
- `synchronize(...)`: orchestration and review status.
- `main(argv)`: argparse CLI.

## Input validation and acceptance

The user-provided 2026-11-06 OpenSees export may contain partial-height wall openings; if first-storey slice signatures differ, `aw_candidate_m2` remains null and a human must reconcile wall piers/openings before engineering use. Completed historical ETABS scaling workbook values are NOT reused across EDB identities without proof.

OpenSees Rayleigh evidence is only populated when the earlier model/weight/state hash screen succeeds. A current gravity PASS alone is insufficient.

## Regression checks

`tests/verify_opensees_first_nbc_sync.py`: uniform OpenSees source, nonuniform opening, original Excel copy preservation, output collision, mock ETABS read-only calls/restored units, wrong EDB rejection.

Native ETABS 23 and actual project model data are not exercised by GitHub CI.
