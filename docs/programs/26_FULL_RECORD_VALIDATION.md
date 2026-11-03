# Stage 05 — full earthquake history evidence gate

Every exploratory case now writes Accepted_History_Completion_Gate.json after the transient. It checks all accepted time samples and numeric response channels for finite values, strictly increasing time, zero start and exact requested finish. The case remains EXPLORATORY even after a complete earthquake. Failure to reach the requested time raises a ValueError and cannot be presented as a completed run.

For Kobe and each other PEER pair, run full XY and YX with source units and scaling audited; repeat with a halved integration step using identical model/motion input hashes. The compare_time_step_results helper provides relative differences but does not assume an acceptance tolerance. Keep every failed/cancelled run and its source hash. The native wall X-only first-step failure remains unresolved.

NBC105:2025 clause 9.3.2.1 requires at least three orthogonal motion pairs for torsionally sensitive 3D assessment. No code pass is inferred from a full-duration integration alone.
