# GUI and transient performance / accuracy

## Readiness dashboard — implemented 2026-11-12

**When:** project selection and Refresh evidence. **Why:** hashing numerous evidence files on Tk's main thread can block clicks/scroll. **How:** a daemon worker performs the existing `audit()` without any Tk calls; a 100-ms Tk poll applies results. A monotonically increasing request ID discards stale results if another project/model was selected. **Where:** `components/model/readiness_dashboard_gui.py`. **Who:** UI maintainer verifies non-blocking Tk behavior; structural reviewer remains responsible for signoff.

**Data correctness:** the audit now caches each evidence SHA-256 **only within the current audit**, eliminating repeated reads for evidence reused across categories; each subsequent refresh recomputes hashes. Source paths, result status and reviewer signoff have not been relaxed.

**Feedback:** progress text while scanning; export is rejected while no complete report exists; failures name the problem. Existing relative outputs remain unchanged.

**Limitations:** this improves dashboard responsiveness, **not** the native OpenSees solve rate. A real Windows/Tk UI test and large project stress benchmark remain pending. File SHA snapshots can still change on disk during reading: don't edit model/evidence while preparing signed results.

## Linear and nonlinear solver performance — research gate

Keep fixed model/record SHA and identical dt for A/B performance comparisons. Distinguish:
- model/gravity building and eigen calculation;
- `ops.analyze(1, dt)` native transient time;
- `ops.reactions()`, node sampling and CSV recording time;
- GUI log append/time, export/plot time and total wall clock.

Old Kobe evidence: XY finished approximately 8,040 s, YX incomplete in supplied screenshot, 37,776 equations, ~0.5 steps/s. The currently committed factorOnce and vector-reaction options are opt-in experiments, **not** verified general speedups.

An elastic model assumption must be physically verified before `Linear -factorOnce` is enabled. A nonlinear or changing-tangent model requires a suitable native algorithm and valid damping/integration scheme. Never reduce integration duration or required output points merely to claim performance.

## UI consistency policy

All analysis modules should eventually expose scroll, copy full log, ZIP export, stop/cancel child process, stage and full-record status, immutable file manifest, exact run path and troubleshooting entry point. Each change needs GUI regression plus real Windows test; do not replace stable controls wholesale.

**Refresh backpressure:** The dashboard uses **one background audit worker per window** rather than a thread per Refresh click. Rapid project/model changes are coalesced; stale reports never overwrite newer selections. The worker exits after window destruction.
