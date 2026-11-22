# Per-module ZIP ownership and NLTHA 21-gate evidence plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Put every new module review ZIP into its own source-run's `07_EXPORT_ZIP`, preserve all existing evidence/readers, and make the 21 production NLTHA requirements auditable without falsely approving the model.

**Architecture:** A single `components/inputs/review_zip_paths.py` resolver owns ZIP destinations, with source writers preserving independently saved result directories and existing manifests. The readiness editor validates evidence references and parameters at save time. A separate complete evidence closure ledger differentiates source candidates, solver checks, absent calibration and human approvals.

**Tech Stack:** Python 3.12, pathlib, zipfile, Tk, offline synthetic pytest/unittest, GitHub CI.

**Spec:** `docs/architecture/20261122_CANONICAL_REVIEW_ZIP_ROUTING.md` and `REVIEW_MAIN/06_NONLINEAR_TH/20261122_21_BLOCKERS_CLOSURE_PLAN.md`.

## Global constraints

- 32 actual physical foundation supports, 44 shear-wall mesh points; no fabricated fixities or missing wall-edge MPC.
- Full gravity comparison `GRAVITY_1.0D_1.0L` separate from NBC 105 Table 5-1 seismic mass.
- 2×12 m X walls with actual openings; no old 6 m X-wall period workbook as a validated current input.
- Local ETABS EDB, waveforms and private reports not committed; historical archive bytes never moved/deleted or uploaded automatically.
- No automatic `approved_for_nltha`, `nonlinear_parameters_reviewed` or `checks[key]` changes; source model acceptance remains open.

## Implementation tasks and acceptance

- [x] Read first contracts, identify active writers and inspect uploaded MRSM ZIP, numerical case status and material config.
- [x] TDD: write focused failing tests of exact canonical ZIP paths for MRSM/organized/history and fallback.
- [x] Centralize ZIP ownership and migrate ESM, MRSM, LTHA/NLTHA, gravity, model mesh and native exported ZIP outputs.
- [x] Preserve explicit `07_EXPORT_ZIP/Gravity_Evidence_Upload` namespace and update source layout tests.
- [x] TDD: reject auto-filled `AVAILABLE FOR REVIEW` placeholders and missing reviewed parameters at readiness save.
- [x] Document each of 21 current blockers, evidence status, actual closure conditions and peer-reviewed references.
- [ ] Verify final-head **entire** Linux + Windows CI, regression ZIP hash/reopen and exact source-review attestation.
- [ ] After green source CI, merge PR #158 into main and inspect merged head.
- [ ] **Native owner-side follow-up:** rerun actual 25-storey M0/Kobe/ULS XY+YX full record and compare native 32-support reactions; do not mark complete without full-duration evidence.

## Review focus

1. Named existing Gravity_Evidence_Upload must remain nested under seventh stage and never be flattened.
2. Multiple ZIP exports must not silently overwrite older compressed evidence or reinclude nested ZIPs.
3. Source-verified reviewed checklist evidence must not be inferred from a discovered elastic result.
4. A failure during ZIP compression cannot turn an incomplete analysis into successful solver status.
5. Windows path/case contracts, long paths and symlinked output directories must remain fail-closed.

**Engineering status:** Native ETABS/OpenSees source equivalence, specimen-calibrated nonlinear RC and first complete NLTHA record unverified.
