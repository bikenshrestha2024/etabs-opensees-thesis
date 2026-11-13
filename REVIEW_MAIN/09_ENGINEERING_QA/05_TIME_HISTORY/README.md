# 05 — Gravity-to-time-history OpenSees transition

**Q. What is the recommended sequence?** In each fresh analysis domain: validated geometric transformations and 3D materials, incremental NBC §5.2 gravity and convergence, check for unintended static EL patterns, `ops.loadConst('-time',0.0)`, `ops.wipeAnalysis()`, new damping/integrator/recorders and new Path/UniformExcitation pairs, then bounded diagnostics and complete XY/YX histories.

**Q. What must not happen?** Do not freeze gravity before convergence; do not invoke `ops.wipe()` when preserving state; do not freeze an unreviewed signed lateral static pattern and additionally drive full ground acceleration; do not call a diagnostic short run a complete code-accepted time history.

**When/where:** Before each LTH/NLTHA case at case boundary; preserve source hash, end of gravity, time-zero active patterns and initial support reactions in the isolated case manifest.

[Adopted review](../../07_TIME_HISTORY/20261113_NBC_GRAVITY_PRELOAD_TO_EQ_TRANSIENT_DECISION.md) · [Detailed signed EL Q&A](../02_PDELTA_INITIAL_STATES/01_SIGNED_EL_VS_GRAVITY_START.md) · [Q&A home](../README.md)

**Status:** existing runner already uses loadConst; native complete-history acceptance still open.
