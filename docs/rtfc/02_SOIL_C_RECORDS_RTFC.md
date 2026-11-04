# RTFC — Verify Soil C target and already-matched earthquakes

## ROLE
Seismic hazard/ground-motion analyst implementing NBC 105:2025 §9.3.2 with OpenSeesPy.

## TASK
Audit the actual Soil C workbook target and all 16 source `Matched_*.txt` waveforms from eight orthogonal earthquake pairs; map to two simultaneous orientations XY and YX; check source SHA256, time steps, valid acceleration units, fitting-period requirements and source scaling provenance.

## FORMAT
Return an event-by-component table with event, A/B, dt, duration, PGA, SHA, source units, computed 5%-damped PSA fit diagnostic, discrepancies, blocking caveats and runnable preflight command. Document the exact `ops.timeSeries('Path',...)` / `ops.pattern('UniformExcitation',...)` commands.

## CONSTRAINTS
Soil Type **C** is the thesis primary case, not D. Adopt original target `Z=0.35,I=1.0,R_mu=3.5,Omega_u=1.4` only with workbook provenance. Already-matched Acc(g) sources require extra spectral factor **1.0**, Path unit factor **9.80665** for m/s². Do not use PGA ratios to infer original 0.33–3 SeismoMatch scale factors. The actual 0.05–6s matched period range needs comparison with `[Tn90,sqrt(R_mu)*T1]` from verified current modes. Explicit Gorkha 120s→322.94s and Loma 0.005s mismatch issues. Missing session logs = unverified, never pass.
