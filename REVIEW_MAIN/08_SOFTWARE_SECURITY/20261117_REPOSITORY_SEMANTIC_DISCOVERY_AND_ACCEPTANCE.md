# 2026-11-17 — Consolidated repository semantic discovery and strict CI review

## Evidence and scope (do not claim completed engineering review)

**Base:** `main` commit `c2bc828e5b34fc04698ea005a8fdc9b3e72db8c9`. The full GitHub recursive tree `fe96a3db824fe43f2fbdf35ebed8478e48d6b2c9` was not truncated: **3,149 tracked blob files**, **786 Python files**, **1,268 Markdown files**, 3,685 tree entries including directories.

**Authoritative machine-readable audit:** `tools/audit_repository_integrated.py --repo . --output audit/integrated --fail-on-static-blockers` — NOT a second independent or competing scanner. The existing `.github/workflows/integrated-repository-audit.yml` generates categorized artifacts:

```text
audit/integrated/
  00_OVERVIEW/integrated_audit.json
  01_TRACKED_FILES/tracked_file_register.csv
  02_DEPENDENCIES/import_graph.json
  03_FINDINGS/consolidated_findings.json
  04_ACCEPTANCE/acceptance_gates.json
  05_OUTPUT_WRITERS/writer_summary.json
  06_SECURITY/secret_scan_summary.json
  07_ARCHIVE_PROVENANCE/exact_blob_duplicates.json
  08_SEMANTIC_REVIEW/function_review_register.csv
  09_FACADE_COMPATIBILITY/facade_source_context.csv
```

The integrated audit builds precise immutable tracked Git object identities, classifies archives and duplicate blobs, checks active Python syntax, extracts cross-module and import-cycle edges, inventories source writers, generates qualified function/method `NOT_REVIEWED` units and tracks root `exec(compile(...))` compatibility facades. Passing static gates **never** changes that function register to manually reviewed or asserts ETABS/OpenSees gravity equivalence.

## Discovery by source role

| Area | Baseline tree entries (including directories) | Handling |
|---|---:|---|
| `docs/` | 1,066 | reference/provenance and documentation-to-source checks |
| `Saved_Project_V156/` | 566 | preserved snapshots, immutable Git object identity, no active runtime substitution |
| `tests/` | 230 | source integrity, executable regression suites, native-only tests explicitly separated |
| `components/` | 200 | priority detailed engineering, source/reader/writer/GUI and dependency review |
| `Worked_Example_V132/` | 168 | benchmark provenance, not proof of project material calibration |
| `REVIEW_MAIN/` | 166 | discrepancy cases and acceptance register, authoritative issue ownership |
| `excel/` | 147 | formula/workbook and output evidence provenance |
| `archive/` | 122 | preserved history, no unreviewed moves |
| `Research_Components/` | 120 | research benchmark provenance, not automatically imported |
| `Verification_V159/` | 96 | preserved verification evidence with source scope |

No mass renaming, deleting, moving archived snapshots or rewriting private ETABS cases is permitted. Canonical local run roots remain `01_ETABS_EXPORT`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY` plus existing provenance/diagnostic folders; change producers and all consumers together only after compatibility proof.

## Confirmed defects and corrections in this review branch

| ID | Priority | Proof | Correction / scope |
|---|---|---|---|
| CI-001 | P1 | GitHub Actions reported success even though the unit-test command printed `FAILED (failures=1)` and a later command returned zero | Repository compilation workflow now aggregates each command's exit status and fails the entire job if **any** command fails; dedicated propagation test |
| CI-002 | P2 | `tests/test_assembled_mesh_view.py` asserted literal `4×4` while Plotly writes equivalent JSON-escaped Unicode | Compare serialized JSON title, no changes to FE mesh |
| CI-003 | P2 | `tests/test_source_view_compaction.py` compared list to tuple for identical triangle indices | Normalize representation, no changes to rendered geometry |
| CI-004 | P2 | `tests/test_repository_layout.py` wrote literal `\\xff\\xfe` escape text rather than invalid UTF-8 bytes | Explicit bytes fixture to test actual malformed-file refusal |
| CI-005 | P2 | `test_main_launcher_workflow_layout.py` fixed total count at 41 and failed after legitimate four new GUI actions | Preserve original callback-by-name assertions while allowing separately tested additions |
| DEP-001 | P1 | Integrated graph treats even constant-string `importlib.import_module()`/`__import__()` as opaque dynamic imports | Record *statically known* local edges, including deferred callbacks and unresolved local targets; no module is executed |

The new dependency enhancement belongs to `tools/audit_repository_integrated.py`, not a parallel audit implementation. The original 2026-11-15 [engineering review epic #75](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/75) remains the authority on full semantic/native acceptance. Existing `docs/review/ledger/`, `engineering/agent_edits/` and `audit/integrated/` paths remain in use.

## Advisory findings / priority review queue

A preliminary branch-only AST cross-check of 348 runtime Python and 225 test modules found 1,038 local dependency references with zero compile errors and zero unresolved imports after namespace correction, and 147 advisory patterns (71 dynamic execution, 76 pass-only exception handlers). That duplicate scanner was **removed** to prevent conflicting inventories; these figures are a preliminary cross-check, not authoritative final integrated-audit results.

Manual inspection of source searches shows many `exec(compile(...))` occurrences are repository-root compatibility facades loading known local component source paths; their `__file__` context is already specifically inventoried by the integrated audit. Other exception handlers are deliberate ETABS cleanup, optional imports or GUI parsing fallbacks. None may be called an exploit or engineering defect without specific source/caller evidence. Highest dependency fan-in identified in cross-check: `components/inputs/project_workbooks.py`, `components/inputs/output_contract.py`, `components/inputs/output_layout.py` and the numbered compatibility facades. Their source-identity and output-contract correctness remains high priority.

## Acceptance gates

- **G0 Inventory:** reconcile exact Git tracked-file counts and blob hashes with the fully enumerated tree; document archived duplicates, no bulk moves.
- **G1 Static/dependencies:** active Python parsing, imported local targets and facade source compatibility; newly added literal dynamic target cases tested. No unapproved native code execution.
- **G2 Software integration:** every command's failure must propagate; original launcher callbacks preserved, GUI/source/reader/writer/ZIP contracts, source SHA and finite result gates pass existing CI. Green CI is NOT native engineering acceptance.
- **G3 ETABS vs OpenSees gravity:** native six-DOF source restraint/analysis-mesh mapping at 32/76/97 nodes, wall-base force/moment cuts, correct loads and source-to-target element mapping; **UNVERIFIED**.
- **G4 NBC 105:2025 / dynamics:** adopted source Aw and periods; NBC ULS/SLS coefficients, ESM/MRSM, modal, P-Delta initial state, LTHA and complete NLTHA, X-wall 110280 first-step and calibration of FVD/BRB; **UNVERIFIED**.
- **G5 Security/public provenance:** preserve original EDB/XLSX, site datasets and unredacted logs outside public repository; scan tracked sources and Git history separately.
- **G6 Merge:** reviewed diff, precise PR-head CI success, unchanged structural source physics, unresolved function-level and native tests recorded.

## What remains OPEN

This audit improves systematic discovery, the integrated dependency graph and reliability of CI tests. **It does not mean all 3,149 files or every generated function-level review unit has been manually read and semantically accepted.** The existing function review register correctly starts each unit at `NOT_REVIEWED`; never bulk-promote to accepted. Production physics, source EDB and numerical solver are not modified in this audit branch. Native Windows ETABS v23 / OpenSeesPy comparisons and all thesis engineering acceptance tests remain open under issue #75.
