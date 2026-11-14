# Uniform output review V6 — all modules

**Date:** 2026-11-14. **Implementation scope:** shared read-only case contract, standard JSON/Excel stage overview, cross-module discrepancy screening. **Not a numerical solver/model correction.**

## Common folder and output schema

The existing shared stage registry remains authoritative: `01_ETABS_EXPORT`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`. Auxiliary stages `02_MODEL`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES` remain separate. A producer using the common contract writes `RUNS/<STATE>/<CASE>/<UNIQUE_RUN_ID>` with eight standard `00_INPUT_SOURCE`…`07_EXPORT_ZIP` subfolders; legacy formats remain readable without moving files.

## New concrete implementation

- `components/inputs/output_contract.py::inspect_case_manifest` is a read-only source of per-run manifest validation for all modules. It verifies stage, state, case and run ID against actual paths; declared units, SHA digest syntax and standard subfolder presence; and identifies missing or invalid manifests. A file's presence/solver completion is never treated as ETABS equivalence.
- `tools/audit_stage_output_migration.py::audit_stage_migration` now uses this same routine for all seven methods and includes the auxiliary folders. It reports invalid case contract counts, status counts and source fingerprint availability. The audit does not change the source or create directories.
- `--write` produces both a JSON and an Excel workbook in the canonical `09_SOFTWARE_DIAGNOSTICS/MIGRATION_AUDITS` folder. Excel has the common navy header, filters, frozen row and five tabs: **Stage summary**, **Case registry**, **Missing or inconsistent**, **Auxiliary folders**, **Read first**. It records navigation, solver evidence and explicit unverified status, never inventing engineering responses.
- Regression tests: `tests/test_uniform_stage_inventory_v6.py`, the previous `tests/test_stage_output_migration_audit.py`, and the shared output-contract and project-layout suites.

## Operator command (run on the local Windows selected source case)

```powershell
git switch main
git pull --ff-only origin main
python tools/audit_stage_output_migration.py "D:\\Thesis Opensees\\ETABS 11-14-2026\\3" --write
```

**Do not commit** the generated local case inventory: it contains project paths and source identity metadata.

## Remaining native engineering and integration items

1. The exact ETABS/OpenSees 32/76/97 support sets, individual 6-DOF reactions, load ledger and diaphragm–wall–slab–beam equilibrium are unverified. Source-supported correction must precede structural acceptance.
2. MESH_04/08/16 must run three genuinely independent solver models with recovered force/reaction comparison; mesh workbook generation alone is not convergence validation.
3. ESM's full multi-script output writer and its multiple readers need a coordinated canonical migration; its newly added saved-output integrity gate protects against false success but does not complete routing.
4. Gravity and independent ETABS comparator writers require source-matched native Windows smoke tests before moving legacy paths.
5. ULS/SLS slab stiffness, P-Delta initialization, pinned conventional-outrigger/belt/cap connections and nonlinear RC wall/FVD/BRB calibration require native physical verification.
6. Full application GUI consistency and all local Excel/ZIP export buttons must be exercised in Windows. A Python CI pass does not certify user interface or engineering results.

**No EDB/Excel source, original ground motion, working solver file, foundation support or element material was changed.**
