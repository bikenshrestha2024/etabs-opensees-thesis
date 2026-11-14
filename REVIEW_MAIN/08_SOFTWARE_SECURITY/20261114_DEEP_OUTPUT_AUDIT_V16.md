# Deep all-stage code inspection V16 — executable source inventory and new integrity corrections

**Date:** 2026-11-14. **Scope:** Active GitHub repository + focused live-code semantic review.
**Assessment:** CORRECTED_SOURCE_LEVEL_DEFECTS_NOT_NATIVE_ETABS_EQUIVALENCE.
**Supersedes:** [V15 output audit](20261114_DEEP_OUTPUT_AUDIT_V15.md) for the newly identified defects; does not cancel the V15 migration policy.

## What was actually inspected

GitHub's complete recursive repository tree (non-truncated) reported **2,962 tracked files and 735 Python files**, including tests, archived helpers and other non-runtime sources. Do not confuse this number with active runtime code. The new source inventory parses the **324 active Python modules** (top-level launchers plus `components/` and `tools/`). CI's actual static run on the audited source revision identified:

| Observation | Value | Meaning |
|---|---:|---|
| Active Python files parsed | 324 | Source AST parsed without execution |
| Python parse errors | 0 | Syntax level only; not import/runtime or solver correctness |
| Potential write calls | 879 | Candidate calls, NOT 879 bugs |
| Literal references to legacy markers | 95 | Markers, including compatibility readers and documentation literals |
| Literal references to canonical markers | 96 | Markers, not verified writer adoption |

`tools/audit_live_output_writers.py` now provides a reproducible per-file and line-level inventory with exact file SHA256 and a prioritized list of legacy candidate modules. Run it locally against the checked-out repository to reproduce counts. CI retains JSON/CSV/README files as `etabs-opensees-static-writer-audit` artifact. This scan does **not** mean all 735 Python files received a semantic, per-line engineering review. Do not advertise it as such.

## Confirmed defects corrected

| ID | File(s) | Demonstrated flaw | V16 correction |
|---|---|---|---|
| V16-01 | `tools/audit_stage_output_migration.py` | V15 only checked a symlink on `RUNS`, but a symlink on its canonical parent `04_MODAL`, etc., could still cause scanning of an external run tree | Reject stage symlink before `RUNS` enumeration; report `SYMLINKED_STAGE_ROOT_REFUSED`; aux folders report link status |
| V16-02 | `components/inputs/folder_audit.py` | Audit could hash and compare through linked `01_ETABS_EXPORT/<category>` mirror directory/file | Mark `UNSAFE_EXPORT_MIRROR_LINK`, never read external mirror file |
| V16-03 | `components/inputs/folder_audit.py` | Report writer could follow symlinked manifest/report directories | Refuse linked destination before creating reports |
| V16-04 | `components/inputs/output_layout.py` | Stage index could count `REVIEW_SNAPSHOTS` symlink entries as legitimate local results and follow linked export-index destination | Refuse linked paths; preserve explicit `symlink_refused` diagnostic |
| V16-05 | `components/validation/gravity_node_comparison.py` | A NaN coordinate could appear as an unmatched support instead of invalid evidence; NaN support reactions could contaminate discrepancy totals/ranking | Require finite global XYZ and OpenSees Rz; reject missing/duplicate ETABS and duplicate OpenSees support IDs |
| V16-06 | `components/inputs/output_contract.py` | Excel formatter used `list(col)` for **entire columns** while sampling only 300 rows, plus double access to each row | Sample 300 rows with `iter_rows`, then style each data row once; preserve values, formulas, header and width bounds |
| V16-07 | `tools/audit_live_output_writers.py` | No reproducible independent active-code source writer inventory, despite many legacy and canonical outputs | New read-only AST inventory with optional structured per-run JSON/CSV/report, exact hashes, ranked review candidates, unit tests and CI artifact |

The improvements leave source models, authoritative completed Excel calculations, tracked references and historical solver results unmodified. They do not change seismic forces, material constitutive laws, crack factors or mass representations.

## Canonical produced artifacts

```text
<ETABS_EXPORT_CASE>/
├── 00_SOURCE_MANIFEST/
├── 01_ETABS_EXPORT/
│   ├── 00_MANIFEST/
│   ├── 01_SOURCE/
│   ├── 02_MAPPING/
│   ├── 03_LOADS/
│   ├── 04_VISUALIZATION/
│   ├── 05_AUDITS/
│   ├── 06_CONFIG/
│   ├── 07_LOGS/
│   ├── 08_PROCESSING/
│   └── 09_REVIEW/
├── 02_MODEL/
├── 02_GRAVITY/
├── 03_ESM/
├── 04_MODAL/
├── 05_MRSM/
├── 06_LINEAR_TIME_HISTORY/
├── 07_NONLINEAR_TIME_HISTORY/
├── 08_ETABS_COMPARISONS/
├── 09_SOFTWARE_DIAGNOSTICS/
│   ├── DISK_AUDITS/RUNS/<UTC>/{JSON,CSV,REPORT}/
│   ├── MIGRATION_AUDITS/RUNS/<UTC>/{JSON,EXCEL}/
│   └── WRITER_AUDITS/RUNS/<UTC>/{JSON,CSV,REPORT}/
├── 90_UPLOAD_PACKAGES/
├── REVIEW_MAIN/
└── OpenSees_Analysis_Results/  # historical compatibility: not deleted
```

New solver producers using the central output contract own one case-specific
`<STAGE>/RUNS/<STATE>/<CASE_ID>/<RUN_ID>/` with numbered
`00_INPUT_SOURCE, 01_LOGS, 02_RESULTS, 03_EXCEL, 04_FIGURES,
05_COMPARISONS, 06_REVIEW, 07_EXPORT_ZIP`. Existing gravity, ESM, MRSM,
modal, LTHA and NLTHA modules must still be verified independently for
complete writer/reader migration. The AST ledger prioritizes that work,
but does not move files.

## Engineering acceptance gates that remain open

1. Native ETABS versus OpenSees **32/76/97 support** comparison: same model identity, actual support DOFs, global-force axes and six reaction components; no nonfinite/duplicate IDs; distinguish numerical equilibrium from exact per-foundation agreement. CSI Analysis Reference explains joint local axes and restraint/link reaction contributions: https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf
2. **MESH_04/08/16** independent ShellMITC4 slab–beam–wall gravity load-path solve: physical thickness, source-mapped in-plane/plate stiffness, source load count, wall/beam offsets, load transfer, reactions and recovered shell/frame forces; compare mesh-convergence trends. OpenSees command documentation: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/ShellMITC4.html
3. Brace/end My/Mz release and zero torsion equivalence; ordinary SHS versus axial-only brace/device; conventional outrigger, belt truss and cap truss local-axis and joint-constraint equivalence before applying BRB/FVD overrides.
4. ESM applicability, project-specific NBC 105:2025 `Aw` from original workbook, independently adopted X/Y periods; ULS/SLS stiffness, diaphragm mass and inertia, MRSM forces vs displacement scaling and drift.
5. The project-adopted IS 16700 §7.2(d) initial signed P-Delta case gate, kept separate from NBC 105 combinations; never carry static EQ and dynamic input together without audited state transfer.
6. Native NLTHA first-step X-wall failure, FSAM parameter and project-rebar evidence, nonlinear element stress resultants, damping/device data and complete matched accelerogram XY/YX analysis.
7. Windows GUI focus/scroll/copy/export/stop responsiveness and publication links; verify with ETABS on a private EDB copy and matching source Excel hashes.

## Verify locally

```powershell
python tools/audit_live_output_writers.py --repo .
python tools/audit_live_output_writers.py --repo . --export "D:\Thesis Opensees\ETABS 11-14-2026\3" --write
python -m unittest tests.test_deep_output_inventory_v16 tests.test_folder_audit tests.test_output_layout tests.test_stage_output_migration_audit -v
python tests/verify_gravity_node_comparison.py
python -m unittest tests.test_unified_output_contract -v
```

The review ledger is not a substitute for a full semantic-code audit. To claim
"all modules reviewed", every active source file requires a dated reviewer,
actual source SHA, specific inspected lines, caller and consumer verification,
numerical impact assessment, tests and native evidence. Future revisions
must not convert **NOT_VERIFIED** into **PASS** based solely on a complete folder.
