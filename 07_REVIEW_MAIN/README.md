> **New Kobe linear-history evidence:** [full XY/YX pair review, drift and modal provenance](../REVIEW_MAIN/05_LINEAR_TH/20261112_KOBE_FULL_PAIR_TIMING_DRIFT_AND_PERIOD_AUDIT.md). Both cases completed; performance and engineering acceptance remain distinct.

# 07 — Thesis engineering review and discrepancy control

**Canonical numbered navigation:** `07_REVIEW_MAIN/`.  
**Authoritative historical issue records:** [`REVIEW_MAIN/`](../REVIEW_MAIN/README.md).

This numbered folder is the **front door** to the thesis review backbone. Existing review files remain in `REVIEW_MAIN/` for compatibility with source links, scripts, output manifests, saved local paths and historical evidence. This is a deliberate **navigation alias, not a duplicate review store**, and it does not claim that structural validation has passed.

## Current review case directory

| ID | Workstream | Issue register | Decision focus |
|---|---|---|---|
| 00 | Original source and input identity | [Input provenance](../REVIEW_MAIN/00_INPUT_PROVENANCE/REVIEW.md) | EDB/workbook and source SHA, LFS identity |
| 01 | Gravity | [Gravity](../REVIEW_MAIN/01_GRAVITY/REVIEW.md) | 32/76/97 support checks and load transfer |
| 02 | Equivalent static method | [ESM](../REVIEW_MAIN/02_ESM/REVIEW.md) | Source Aw/T1 workbook and seismic force |
| 03 | Modal | [Modal](../REVIEW_MAIN/03_MODAL/REVIEW.md) | T1 X/Y, mass and source stiffness |
| 04 | Modal response spectrum | [MRSM](../REVIEW_MAIN/04_MRSM/REVIEW.md) | CQC, force/drift, ETABS equivalence |
| 05 | Linear time history | [LTH](../REVIEW_MAIN/05_LINEAR_TH/REVIEW.md) | Paired XY/YX completion, damping and speed |
| 06 | Nonlinear time history | [NLTHA](../REVIEW_MAIN/06_NONLINEAR_TH/REVIEW.md) | First-step core-wall failure and materials |
| 07 | ETABS/OpenSees cross-model evidence | [Comparison](../REVIEW_MAIN/07_ETABS_OPENSEES/REVIEW.md) | Matched physical source and demand |
| 08 | Software/security | [Software/security](../REVIEW_MAIN/08_SOFTWARE_SECURITY/REVIEW.md) | GUI, logs, ZIP export and protection |
| TH | Cross-cutting time-history research | [History reviews](../REVIEW_MAIN/07_TIME_HISTORY/20261112_KOBE_LINEAR_PARTIAL_BATCH_AND_PERFORMANCE_REVIEW.md) | Performance and full-height bay verification |
| 90 | Standard issue record | [Issue template](../REVIEW_MAIN/90_TEMPLATES/ISSUE_TEMPLATE.md) | Reproducible discrepancy closure |

The nested `07_TIME_HISTORY` folder predates this navigation layer and overlaps with 05/06 topics. Preserve its original reports and cross-link them; do not merge/move them without reviewing links and citations.

## How review supports the thesis

**What:** maintain an evidence-backed record of each model discrepancy, uncertainty, decision and independent verification.

**When:** after every source change, failed computation, disagreement with ETABS, sensitivity exception or proposed acceptance decision; before advancing to full M0–M6 runs.

**Why:** a successful import, gravity equilibrium, solver return code or one history orientation must not be mistaken for a validated nonlinear high-rise model.

**How:** create an issue using [the existing template](../REVIEW_MAIN/90_TEMPLATES/ISSUE_TEMPLATE.md), capture source-model version/SHA, original numerical results and full log, precise engineering hypothesis, testable correction, independently recovered comparison and review status. Keep private binaries in local evidence outputs, not the public repository.

**Where:** begin here, follow links to the authoritative `REVIEW_MAIN/<case>/` file; model-bound private evidence remains under the user's existing local analysis output root. Do not relocate files purely to change numbering.

**Which:** source EDB, original NBC 105 calculation workbook and exact cells/SHA, ETABS comparison, calibrated material model, matched waveform identities, XY/YX case/state and code clause/DOI.

**Who:** the researcher gathers reproducible evidence; an independent qualified structural/earthquake reviewer judges physical adequacy; the software maintainer preserves code/regression provenance. Unknown actual signatories must remain unassigned.

## Priority blockers

1. NLTHA first-step X-direction RCC core-wall failure and wall-region/material provenance.
2. Independent ETABS/OpenSees gravity, mass, section and support comparison.
3. Full paired XY/YX record completion and linear/transient performance equivalence.
4. Source-verified FVD/BRB and wall calibration, ground-motion provenance and NBC clause acceptance.
5. Only then assess planned M0–M6 full-duration research matrix and sensitivity results.

See [P0–P2 thesis workboard](../docs/review/20261112_THESIS_DELIVERY_WORKBOARD.md), [engineering gates](../engineering/rules/ENGINEERING_GATES.md) and [thesis knowledge base](../KNOWLEDGE_BASE/README.md).

## Rename policy

- **Now:** `07_REVIEW_MAIN` is the numbered navigation entry; existing `REVIEW_MAIN` is the authoritative storage directory.
- **Later, only if warranted:** a true move of 40+ entries requires finding all import/callers, Markdown links, scripts, output readers, archival and local Windows paths, plus source SHA and CI test evidence. Do not delete the original directory before a compatibility migration has been validated.
- This directory does **not** duplicate issue files; all edits to review cases should continue in the original authoritative location.
