> **Latest full-pair evidence:** [2026-11-12 Kobe XY/YX completed 8,188 steps in 4 h 32 m 44 s](20261112_KOBE_FULL_PAIR_TIMING_DRIFT_AND_PERIOD_AUDIT.md). ULS drift screen is preliminary; directional T1 needs modal provenance review; solver time dominates. Prior half-finished screenshots do not describe the finalized batch.

# Linear time-history review
**RV-LTH-001:** P0 OPEN_HIGH — short diagnostics versus full records
**RV-LTH-002:** P1 OPEN_HIGH — damping and periods, source states

Observed GUI: NBC adopted X=2.0385674 s, Y=1.9219798 s (shown in ESM), but separate LTH T1 fields blank in previous screenshots. Damping calibration period 1=2.38391394 s, period 2=0.1392422 s; selected viscous damping=5%. These three concept types must remain separately labeled. Source EDB, stiffness modifiers and 3D mass must match the actual LTH run; 'Linear' must mean elastic physical material and compatible PDelta state, not just `algorithm('Linear')` on fiber nonlinear elements.

User's 0.5-s trials for Hector Mine XY/YX and Loma Prieta XY/YX were finite diagnostic runs, **not** the 39.98–45.29-s full-record results. Long-duration results require full motion, original paired component synchronization and unit conversion g×9.80665 in m/s² with no duplicate spectral multiplier.

**Review outputs:** full vs used duration, dt, nsteps, source A/B SHA, X/Y motion swap, eigen/target Rayleigh damping bands, all base/storey shears, corner drift histories, peak/residual displacement and relative/absolute accelerations with units; completed vs truncated flags; side-by-side ETABS LTH comparison only for matching run assumptions. Stop option, GUI scrolling and source-safe per-run ZIP evidence should be Windows-tested.
