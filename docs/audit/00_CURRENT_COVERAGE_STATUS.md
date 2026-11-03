# 00 — Full repository coverage status

Baseline audit reference: 0ab5080d1cb1de52f68f3d369411a35ddf5d7f33 on 2026-11-03, before the inventory refresh commit.

- Tracked files enumerated: 1721
- Active Python components: 84
- Source guides physically present for active components: 84
- Targeted in-depth source reviews: 9
- Files classified as historical evidence: 989
- Other results/datasets: 137

The complete updated per-file ledger is [00_ALL_FILES_AUDIT.tsv](00_ALL_FILES_AUDIT.tsv). Each row has path, exact Git blob hash, priority, review depth, guide status and recommended action. The inventory does not imply full file-level source correction or execution of all tests.

## Meaning of review classifications

- TARGETED_IMPLEMENTATION_REVIEW: inspected specific source behaviors and created a detailed technical guide; **not** numerical verification.
- STATIC_SCREENING: active code previously inspected for structural risks and common exception/path markers.
- CODE_REVIEW_PENDING_EXECUTION: tests/CI exist but their execution outcome has not been independently verified.
- INVENTORY_ONLY: classified from paths, metadata and known archive context, without line-by-line examination.

## Functional changes actually implemented in this improvement pass

FVD/BRB parameter finiteness guards; nonlinear FVD Cd mm-to-m coefficient conversion; signed FVD history audit; BRB cumulative plastic-demand helper; added non-native regression tests; corrected trace diagnostic CLI text; scientific citation register and coding instructions; comments inserted into critical nonlinear sources.

## Open engineering blockers

Full building X-only first-step failure remains unresolved; actual ETABS reinforcement and FSAM wall boundary details not source-verified; native OpenSeesPy full-record execution unavailable here; full M0–M6 performance comparison pending; per-device experimental calibrations pending.

## Engineering change rule

Do not automatically rewrite all archived scientific files or prepend generic citations to unrelated code. Preserve reproducibility and scope physical modifications behind tests. Continue in targeted commits with source-specific validation.
