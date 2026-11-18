# 18 November 2026 — Fail-closed full-record durations and accepted timestep bounds

**Issue:** NLTHA-HISTORY-DURATION-AND-DT-01. **Scope:** software result-evidence integrity; **not** structural solver completion or physically validated response.

## Source-backed defect

`components/nonlinear_time_history/full_record_gate.py::verify_accepted_history` previously used `float(record_end_s)` and `float(requested_end_s)` without rejecting boolean inputs. In Python, `float(True)==1.0`: an otherwise finite, monotonically increasing accepted-state recorder ending at `t=1.0 s` could be labeled `FULL_DURATION_NUMERIC_SCREEN` when source duration or requested duration was the boolean `True`, not a physical duration. Nonnumeric/missing inputs could leak inconsistent TypeError/ValueError instead of a consistent invalid-record-duration error.

`compare_time_step_results` validated each positive `min_accepted_step_s` and `max_accepted_step_s` and required the fine *maximum* to be below the coarse maximum, but did not check **within-run** `min<=max`. Thus a logically impossible coarse or fine timestep summary could enter the convergence comparison.

## RED before implementation

[Integrated GitHub Actions run 44294738562](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44294738562) on test-only commit `461e340cc4d6ab530056cdff96bde58cc3d8ad50` executed the pre-existing focused suite with new `tests.verify_full_record_gate.GateTests.test_full_record_rejects_boolean_or_malformed_durations` and `test_timestep_rejects_inverted_step_bounds`. It recorded failures on `True`, nonnumeric and `None` record/requested durations, and allowed a coarse `min_accepted_step_s=.02` with `max_accepted_step_s=.01`. These tests deliberately prove unsafe historical behavior; **red CI is not a passed engineering gate**.

## Narrow correction

- Reject boolean `record_end_s` and `requested_end_s` before float coercion. Missing, malformed and overflowing duration values now fail with `ValueError("Invalid record duration ...")`; finite positive numerical durations are still required.
- For each coarse and fine full-duration screen, fail if `min_accepted_step_s > max_accepted_step_s`. The original model/record hashes, limit state, XY/YX orientation, damping/excitation identity, variant and event identity, finite demand metrics, accepted time history and strictly finer maximum-step requirement are preserved.
- No ETABS/OpenSees source model, mass, device, RC wall law, ground motion, time integration defaults or generated engineering results were changed.
- Both already source-inspected functions were reattested to exact amended `full_record_gate.py` Git blob `b1cb87eae0f26454d760b861890f356257624e62` in the canonical `docs/review/ledger/semantic_review_attestations.csv`. Source attestations remain `SOURCE_INSPECTED_TESTED_NOT_NATIVE_VERIFIED`.
- **GREEN criterion:** New test cases and unchanged focused tests, NLTHA quality, integrated audit, source discovery and privacy checks must all pass at the exact PR head before merging. Attach CI links to pull request once green.

## Structural qualification remains independently blocked

The archive contains no original **current** native ETABS EDB or source-matched complete eight-pair ground motions to execute the project here. A `FULL_DURATION_NUMERIC_SCREEN` status indicates finite recorder samples and a complete *claimed time range*, **not** source-proven complete transient solver execution, independently calibrated nonlinear wall/brace/FVD materials or ETABS-equivalent physical load paths.

- G02: 32/76/97 support-set physical equivalence **NOT VERIFIED**. Existing 1.0D+1.0L global FZ agrees at approximately `311367.313600` ETABS versus `311367.313880 kN` OpenSees, but 44 wall-connected nodes in OS76 attract approximately `104463.013534 kN`; their ETABS point-object FZ source ledger reports zero. Need *analytical-joint* six-component resultants, connections, cuts and source EDB before interpreting the discrepancy.
- G05: original wall tag 110280 (and 112778) produced post-failure nonfinite local force following Kobe-X first transient step. Need preserved failed/accepted states, actual wall source map, independent material coupon/panel and connected-bay ZERO/X/Y/XY native trials; postfailure force nonfiniteness is **not** proof of initiating wall constitutive failure.
- G07/G09: 7 variants × 8 paired events × 2 states × XY/YX = **224 physically accepted full-duration native histories** **NOT VERIFIED**. A numerical duration gate is necessary but cannot itself produce the histories.
- Full software semantic completion: prior ~4424 AST candidate scopes; existing source-inspected ledger is a narrow, intentionally unclosed subset. Static CI is not an exhaustive source-level review.

**Acceptance decision:** Confirmed input-integrity defect fixed only if exact-head regression/CI pass. Native physical/model and thesis acceptance remain **OPEN**.
