# Native ETABS comparison discovery and LTHA field validation — implementation plan

> Required: superpowers systematic-debugging, test-driven-development, executing-plans and verification-before-completion.

**Goal:** Fix blank native ETABS comparison source discovery without fabricating ETABS responses, and fix LTHA float('') / ULS-SLS mismatch. Preserve 32 physical foundations versus 44 shear-wall mesh points.
**Architecture:** Existing validation/etabs_direct_api.py is the read-only CSI COM adapter; etabs_comparison.py remains the GUI and source-identity boundary. An independent raw ETABS API base-reaction observer shows actual source case names and numbers without falsely asserting comparable spectral basis. Reviewed mapping remains required for pass/fail. LTHA gains one pure field validator called before creating a run.
**Evidence:** Attached 68/140/140 ZIP files contain no native ETABS response set, only a blank comparison template. The MRSM result JSON contains six ULS X/Y E0,Eplus,Eminus cases and no support/mass execution identity; its log records 76 source restraints and gross wall stiffness. LTHA UI selected SLS while project source is ULS; numeric period text boxes are blank but runner calls float(value) unguarded.
**Preflight:** AGENTS.md, engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md, .agents/skills/etabs-opensees-read-first/SKILL.md, both subsystem docs and code-purpose matrix read. Base main 519ed64e130c396a194a0a4fb1ae39010c5d3fbf. Native EDB SHA and Windows ETABS live session unavailable.

## Task 1 — LTHA named field and state preflight
- [ ] RED: test blanks identify exactly Rayleigh period 1/2, T1/Tn; no generic float empty-string exception.
- [ ] RED: reject SLS GUI against source ULS before parsing fields; paired 3D needs Y periods, X-only does not.
- [ ] GREEN: pure parser validates finite positive periods, 5% maximum damping, integer modes, optional short trial and correct state; GUI calls parser before run.

## Task 2 — read-only live ETABS response discovery
- [ ] RED: fake COM proves original EDB identity, actual case names, returned raw FX/FY/base data, and setup/unit restoration; refuse other file and COM errors.
- [ ] GREEN: read-only API raw observations stored with file SHA and case labels, shown as native preview; never automatically apply CQC scaled basis to unreviewed raw shear.
- [ ] GREEN: existing reviewed mapping continues to populate ETABS value, differences and comparisons without manual normalized CSV for genuine compatible cases.

## Task 3 — MRSM source support/mass identity
- [ ] RED: matching model data SHA without support/mass execution flags cannot be treated as verified 32-support equivalent.
- [ ] GREEN: MRSM result persists actual support_case/mass_policy/evidence; comparison retains historical OpenSees response but blocks equivalence PASS for missing/mismatched execution identity.

## Acceptance
- [ ] Focused tests plus full Github CI; real ETABS 23 native extraction, source shell-edge/MPC equivalence and local reactions remain NOT VERIFIED until Windows run.
- [ ] No actual user EDB/worksheet/ZIP uploaded to public repo; only source code and non-sensitive derived observations.