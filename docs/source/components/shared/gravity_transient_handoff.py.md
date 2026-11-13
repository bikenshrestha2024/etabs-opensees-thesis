# gravity_transient_handoff.py — source and validation guide

**Source:** [components/shared/gravity_transient_handoff.py](../../../../components/shared/gravity_transient_handoff.py) · **Classification:** NBC 105:2025 §5.2 physical gravity to §8/§9.3 ground-motion handoff · **Status:** optional helper, NOT wired into production; model builder does not yet publish verified preload convergence.

## Purpose and expected usage
`freeze_verified_gravity(ops, case=..., builder_gravity_converged=...)` freezes *already converged* gravity load patterns by `ops.loadConst('-time',0.0)`. It does not create the model, choose load factors, impose gravity, replace geometric transformations, remove static earthquake actions, or configure transient analysis. Provide `builder_gravity_converged=True` only when source-matched native convergence evidence exists. Existing legacy runners retain their previous directly-called `loadConst`; this helper is a future fail-closed integration point.

## Source and engineering acceptance
- NBC 105:2025 §§5.2, 8.1.1.2–8.1.1.3, 9.3.1.2–9.3.1.3.
- IS 16700:2023 §7.2(d) defines compulsory separate signed X±/Y± initial EQ P-Delta cases, not a perpetual static seismic bias during ground-motion histories.
- OpenSees [loadConst](https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/loadConst.html), [wipeAnalysis](https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/wipeAnalysis.html).
- [P0 source and initial-state review](../../../../REVIEW_MAIN/00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md).
- [Adopted NLTHA handoff procedure](../../../../REVIEW_MAIN/07_TIME_HISTORY/20261113_NBC_GRAVITY_PRELOAD_TO_EQ_TRANSIENT_DECISION.md).

## Data and units
Input: OpenSeesPy live domain, nonempty node tags, finite domain time in seconds, separately verified gravity-success flag. Output: dict case/time/status/provenance (not a numerical acceptance certificate). On failure: raises and does not call loadConst where prechecks fail. No load modification other than freezing existing load patterns and resetting pseudo-time.

## Test and limits
Mock tests: `tests/test_gravity_transient_handoff.py`. Native proof still required: matched ETABS/OpenSees load patterns, support reactions, individual joints, gravity shortening, nonlinear P-Delta treatment, ZERO/X/Y/XY fresh models and complete time histories. This file's existence or CI success is not engineering validation.

[Module guide index](../../00_SOURCE_GUIDE_INDEX.md)
