# tools/analyze_run_log.py — source guide

**What:** parses a runner log from the preliminary linear LTHA setup check (bracket tags `[WORKLOAD]`, `[SCOPE]`, `[START]`, `[LINEAR TRIAL]`, `[CASE TIMING]`, `[OK]`, `[SOLVER BASELINE]`, `[EIGEN COMPLETE]`) into per-case stage timings, steps, dt and peak drifts, then projects full-record solve time.

**When:** after a preliminary or partial LTHA run, to decide whether a full run is affordable before launching it.

**Why:** the 0.5 s truncated diagnostic is cheap, but the full records are much longer (in the V115 fixture the shortest is 29.99 s, Kocaeli, and the longest 322.94 s, Gorkha); the log alone does not show the cost of running them.

**How:** Python standard library only. Reads the log as UTF-8 with `errors="replace"`, accepts LF or CRLF, joins `[LINEAR TRIAL]` (`full_record=<n>s`) to `[CASE TIMING]` by case name, not by order. Projection: `measured_native_s_per_step` = sum of `native_transient_solve` over cases / sum of steps; full-record steps = `ceil(full_record_s / dt_s)`. Basis wording: linear baseline, no factor reuse, lower bound for nonlinear. Only a `[CASE TIMING]` line whose status is `completed` counts as a completed case; any other status (for example `failed`) is recorded in `failed_cases` with its status and is listed separately in the JSON and Markdown, never in the completed count or the projection. A non-numeric stage value is skipped, not an error. The 0.5 s truncation wording is printed only when the log's `[LINEAR TRIAL]` lines say the trial was truncated, and uses the logged `analyzed=` value. The projection covers only the completed cases that have a full-record duration; the findings state how many of the declared cases are excluded (4 of 16 in the V115 fixture). Nonlinear runner logs are not parsed for steps, dt or drifts (their `[OK]` line differs). Output is deterministic (sorted keys, LF, no timestamps) and carries the status `SOLVER_OR_LOG_EVIDENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`.

**Where:** source `tools/analyze_run_log.py`; tests `tests/test_analyze_run_log.py`; fixture `tests/fixtures/ltha_v115_prelim_log_excerpt.txt`; first findings `docs/validation/run_findings/LTHA_V115_PRELIM_20261120.{md,json}`. CLI: `python tools/analyze_run_log.py LOG --out-dir docs/validation/run_findings --stem NAME`.

**Which:** log text only. It opens no model, imports no solver and does not touch any EDB.

**Who:** software maintainer owns the tool; the thesis author owns any reading of the numbers.

## Recommendations from the V115 preliminary findings

- Decouple model rebuild per case. Each case spends about 85 to 110 s rebuilding the model and gravity state before it solves, repeated for every XY/YX case.
- Consider factorisation reuse (the existing `-factorOnce` path) only after `elastic_constant_tangent_verified` is true and the time step is constant.
- Nonlinear runs cannot reuse the factorisation, because the tangent changes. Treat the projected hours as a lower bound for them.
