> **SUPERSEDED EVIDENCE STATUS (2026-11-12 20:30 +05:45):** This report represents an earlier partial log only. The complete XY/YX pair was subsequently supplied, verified and reviewed in [the full-pair audit](../05_LINEAR_TH/20261112_KOBE_FULL_PAIR_TIMING_DRIFT_AND_PERIOD_AUDIT.md). The incomplete-YX assertion below is historically accurate only for the earlier snapshot, NOT the final run.

# 2026-11-12 — Legacy linear time history not finished, Kobe paired 3D

**Run identity:** `LTH_ULS_Trial_20261112_155716_817601`
**Evidence:** user-supplied `Pasted text(20261112-131440).txt` (1,992 lines) and screenshot `image(20261112-131449).png`.
**Evidence status:** log ends while second orientation was RUNNING. Later completion, interruption and any machine-side state are **unknown**. Do not infer a failed transient solver or code acceptance.

## Recorded facts, not projections

| Item | XY | YX |
|---|---|---|
| Motion pair | RSN1120_KOBE_TAK000 | RSN1120_KOBE_TAK000 |
| Requested steps | 4,094 | 4,094 |
| Integration dt | 0.01 s | 0.01 s |
| Status from log | **[OK]** / CASE TIMING completed | **RUNNING**, no [OK] |
| Recorded accepted steps | 4,094 | at least 1,365 in uploaded log; screenshot shows 1,376 |
| Physical record time | ~40.94 s | screenshot 13.760 s |
| Case wall time | 8,040.212 s | screenshot ~2,904 s so far |
| Transient with recording (XY) | 7,916.905 s | no complete case timing |
| Peak drifts (XY only, provisional) | X 0.00566023; Y 0.0077874 | unavailable |

XY gravity/model 94.995 s, damping eigenanalysis 25.742 s, response exports 1.778 s.
Model at startup: 11,097 nodes, 14,262 elements, 37,776 linear equations; 20 eigenmodes.
Gravity: 20 steps, 286,419.758231 kN applied = reaction, equilibrium error 5.83e-12%, 76 source support nodes.
The supplied run is marked `PRELIMINARY setup check` and is not a completed NBC paired-history comparison.
The XY maximum value 0.0077874 exceeds the **SLS** numerical screen of 0.006, but this run is **ULS**; DO NOT misapply the SLS threshold. XY maximum is below the numerical ULS screen 0.025; it is not global engineering/code acceptance until full suite, torsion/edge drift, force, and other gates pass.
The screenshot displays **XY completed, YX running**, not a completed 2/2 batch.

## Most significant performance bottleneck

Approximately **98.5%** of the XY case time was transient integration and response recording (7916.905/8040.212), not eigenanalysis or gravity.
Old logs do not isolate native matrix factorization vs `ops.reactions()` and Python recorder costs. Do not claim either is the sole bottleneck.

At observed ~0.5 accepted steps/s, sustained time was ~2 seconds/step; only an identical controlled benchmark can determine an actual speed improvement.
No production transient results are changed by this report.

## Code improvements committed to main

- Reuse of constant-matrix factorization remains separately opt-in with `linear_factor_once_experimental`, gated by explicitly verified constant effective tangent and a constant integration step. It MUST remain off for nonlinear analyses and time-varying tangent/damping.
- New opt-in `linear_vectorized_reactions_experimental` calls documented `nodeReaction(nodeTag)` once per support to obtain all six reaction DOFs; baseline still queries six scalar DOFs. Intended effect: 76 calls rather than 456 per sample for 76 fixed six-DOF supports, excluding `reactions()`, with the same signed six resultants.
- Vector optimization is **OFF** by default. Compare original and optimized histories sample-by-sample before using for engineering acceptance.
- Deterministic mocked reaction-equivalence tests are in `tests/test_linear_reaction_vectorization.py`; these do not replace a native 37,776-equation OpenSees benchmark.

### Recommended minimum verification

1. Preserve the old full XY output and partial YX evidence. **No restart-from-time=13.760s** is promised: CSV does not contain complete internal OpenSees domain state (stress, plasticity, integration history, Rayleigh state, etc.). A restarted case begins from a fresh rebuilt domain unless a tested native checkpoint system exists.
2. Verify the selected model is truly elastic before factor-once; the `algorithm('Linear')` keyword does not linearize nonlinear materials.
3. Run identical brief Kobe XY (then YX) diagnostics with both optimizations OFF, vector recorder ON only, factorOnce ON only, and both ON only if elastic matrix criteria pass. Save four distinct output directories and complete file hashes.
4. Compare every six support reaction resultant, base shears, roof/floor Ux/Uy/Rz, floor acceleration, and all interstory drifts with tolerances agreed in advance. Check drift extrema and signed base shear.
5. Compare `native_transient_solve`, `recording_seconds`, total elapsed, peak RAM and sustained steps/s (separately). If recorder changes cause disagreement, revert to baseline without erasing evidence.
6. Full XY and YX records, gravity, modal participation/Tn90, torsion and edge demands, code-record aggregation, ULS/SLS and ETABS independent checks remain gates.

## Sources
- OpenSeesPy nodeReaction documentation: https://openseespydoc.readthedocs.io/en/stable/src/nodeReaction.html
- OpenSees Linear algorithm and factorOnce caveat: https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/algorithm/LinearAlgorithm.html
- Chopra & McKenna (online 2015; issue 2016), DOi https://doi.org/10.1002/eqe.2622 — spurious Rayleigh damping in nonlinear RHA; private uploaded copy is indexed as L035.

**Engineering judgment:** No full linear suite acceptance or net speedup is claimed from the partial YX screenshot or offline tests.
