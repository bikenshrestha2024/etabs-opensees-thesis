# Engineering acceptance checkpoint — 2026-11-19

**Scope:** current observed `main` SHA `e800203a565f4090b91e38a80300ad0b9b83f2bb`; this is a **checkpoint** and new CI enhancement, not blanket engineering approval. Source-tracked file count from the untruncated Git tree is **3,201** (3,743 entries including directories), not the earlier historical 3,188-file count. Root level has 173 tracked files. No private source data were copied to GitHub.

## Independent status table

| Gate | Status on baseline | Evidence / remaining condition |
| --- | --- | --- |
| Tracked-tree inventory | PASSED, metadata only | Git tree was untruncated, 3,201 tracked blobs; old baseline figures cannot be reused as current |
| Active Python syntax/imports | CI PASSED (scoped static audit) | Exact-main source-discovery/compilation runs passed; no claim all runtime imports execute on Windows |
| Targeted regression | CI PASSED | Six latest exact-head workflow runs succeeded; they do not imply native ETABS/OpenSees runs |
| Entire codebase semantic review | OPEN | Latest prior discovery reported 4,802 all-category AST symbols; only 16 source-attested selected functions; review candidates and active subsets are distinct denominators |
| ETABS–OpenSees physical equivalence | OPEN | Source 32-restraint best local maximum absolute nodal Rz discrepancy = 756.511 kN, from 3,041.266 kN original; require actual native six-component support/cut reconciliation with common model |
| Nonlinear X-wall first-step | OPEN | Element 110280 remains a blocked model/solver qualification task; isolated ZERO/X/Y, material and shell benchmark plus full integration evidence required |
| M0–M6 NLTHA | OPEN | 112 configurations × 2 XY/YX = 224 demanded native full-history cases; static manifest checks are not execution |
| Rayleigh numerical retained DOF | CODE FIX DOCUMENTED; NATIVE CI PROPOSED | One-step X/Y Rayleigh period correction and same-domain eigen comparison documented; `tests/test_rayleigh_retained_dof.py` otherwise silently skips the native test if solver absent |
| Native Rayleigh continuous integration | PENDING WORKFLOW EXECUTION | New workflow `native-rayleigh-regression.yml` pins OpenSeesPy 3.8.0.0, checks import and fails on skipped solver tests. This is a **small benchmark**, not full-building certification. |

## Required gates to close the four unverified scientific areas

**S2 — complete semantic coverage.** Maintain a source-SHA-scoped register per active function/method with reviewers, lines inspected, callers/callees, side effects, source assumptions, test, case label and `REVIEWED` vs `NOT_REVIEWED`. Continue until no eligible active symbols remain unreviewed. Archives require provenance rather than fictitious line-by-line engineering review. Never infer completion from 0 syntax errors.

**S6-G — native gravity.** Fix one ETABS export/model/workbook SHA and ULS/SLS load state. Audit all 32 physical supports and 44/21 additional wall-base nodes separately; compare all six reaction components with source transforms and wall-base force/moment cuts. Match shell-edge constraint interpolation, cross-sectional modifiers, end offsets and load paths. Report worst-point errors with signed deltas and zero-sum check. Require target tolerance under a documented justified engineering criterion; do not merely minimize a scalar.

**S6-N — nonlinear wall.** Produce deterministic single-element, panel and one-bay native OpenSees probes, followed by the complete model preserving interface actions. Capture first invalid element/material/DOF/channel and committed/attempted timestamps; verify gravity preload, constitutive arguments and consistent recorder/constraint graph. Re-run the original current model after a proven material/geometric resolution.

**S6-M — complete NLTHA.** For all 224 cases: require exact model+matched waveform source-byte SHA revalidation, validated input units, pair/orientation/limit-state mapping, finite ordered accepted-state CSV, requested and actual end-time agreement, completion gate, timestep sensitivity, drift/displacement/base shear/device demands, and review of the input hazard/site/Vs30. No claim of experimental calibration from literature-only material values.

## Distinguish evidence types

`STATIC_OK` ≠ `SOURCE_SEMANTICALLY_REVIEWED` ≠ `NATIVE_OPEN_SEES_BENCHMARK_PASS` ≠ `ETABS_PHYSICAL_EQUIVALENCE` ≠ `NLTHA_FULL_BUILDING_ACCEPTED` ≠ `NBC_DESIGN_APPROVED`.

**Native limitations:** GitHub Actions hosted Linux runners do not provide the user's original proprietary ETABS model, licensed ETABS OAPI, Windows Spyder GUI, or private matched waveforms. A full scientific gate requires private local execution and human review of archived evidence. Do not upload source EDB, proprietary workbook or accelerograms to this public repository. Keep provenance hashes and redacted metadata only.

**Associated issue:** #75, full active-source semantic review and native acceptance. **Primary reports:** `docs/validation/20261118_32_SUPPORT_GRAVITY_CONVERSION.md`, `docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md`, `REVIEW_MAIN/08_SOFTWARE_SECURITY/20261119_CODEX_UPDATE_CI_AND_ENGINEERING_EVIDENCE_REVIEW.md`.
