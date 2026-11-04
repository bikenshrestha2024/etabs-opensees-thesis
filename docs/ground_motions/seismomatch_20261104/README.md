# Eight horizontal earthquake pairs: original vs SeismoMatch matched — audited 2026-11-04

**Status: RECORD_STRUCTURE_AUDITED / CONDITIONAL_SPECTRAL_SHAPE_SUPPORT.**
**Not established: NBC 105:2025 spectral fitting approval, original SeismoMatch amplitude-scale eligibility, common lower-of-two initial scaling, or M0–M6 full-duration NLTHA validation.**

This report supersedes the earlier [six-X-file preliminary audit](../../00_SEISMOMATCH_MATCHED_RECORDS_AUDIT_20261104.md). All 16 original PEER/KATNP files **and all 16 final matched exports** were available to the completed audit. The original acceleration time histories are **not committed**. The register [`matched_component_register.csv`](matched_component_register.csv) records original matched filename and its byte-exact SHA256, sampling interval, end time, PGA, and conditional residuals. Users can verify local copies without posting potentially licensed PEER waveforms.

## Source inputs and method

- 8 earthquake pairs × 2 recorded horizontal components: **Gorkha, Landers, Northridge, Kobe, Kocaeli, Chi-Chi, Hector Mine, Loma Prieta**.
- The matched files explicitly label **`Time Series matched accelerogram`** and **`Acc(g)`**. Their numeric time and acceleration columns were parsed and checked for finite data and uniform time increments.
- All original PEER AT2 declared `NPTS` counts agreed with the observed original sample counts. Both matched files of each event have matching sampling intervals.
- Independent 5%-damped pseudo acceleration spectra were computed using Newmark average-acceleration (`gamma=0.5, beta=0.25`) on 120 log-distributed periods from **0.05–6.0 seconds**, no posthoc baseline alteration.
- **Conditional soil-C target only:** `Ta=0.1s, Tc=1.0s, Td=4.0s, alpha=2.5`, with **0.625g assumed plateau**. This is consistent with `Z*I/Omega_u=0.25`; the actual model's complete target normalization was **not independently established**. The computed residuals are not an NBC acceptance tolerance.
- Mean across the 16 individual component mean absolute relative pseudo-spectral errors = **3.06%**; component means range **2.05%–4.75%**. Worst individual period residual was **56.96%**, Gorkha component B. A low mean is not a uniform-frequency tolerance guarantee.
- Any acceleration files sent to OpenSees are already matched: import raw recorded **`g`** values using `ops.timeSeries("Path", ..., "-factor", 9.80665)` in a kN–m–s model, with `scale=1.0` additional spectral multiplier. Execute each pair in BOTH **XY and YX** simultaneously bidirectional support-motion cases.

## Reproduced per-event result

| Event | Matched peak A/B (g) | dt (s) | duration A/B (s) | Conditional mean PSA error A/B (%) |
|---|---|---:|---|---|
| Gorkha | 0.29540 / 0.36868 | 0.005 | 322.940 / 322.940 | 4.02 / 2.87 |
| Landers | 0.32585 / 0.35264 | 0.005 | 48.115 / 48.115 | 2.32 / 2.27 |
| Northridge | 0.37937 / 0.41844 | 0.020 | 39.960 / 39.960 | 2.72 / 4.29 |
| Kobe | 0.26518 / 0.28105 | 0.010 | 40.940 / 40.940 | 2.05 / 2.84 |
| Kocaeli | 0.34635 / 0.32502 | 0.005 | 29.990 / 29.990 | 2.88 / 4.75 |
| Chi-Chi | 0.37654 / 0.34578 | 0.005 | 89.990 / 89.990 | 3.17 / 2.14 |
| Hector Mine | 0.34469 / 0.33687 | 0.010 | 45.290 / 45.290 | 2.12 / 3.87 |
| Loma Prieta | 0.29403 / 0.33996 | 0.005 | 39.975 / 39.980 | 4.12 / 2.55 |

## Explicit anomalies and next actions

1. **Gorkha matched export duration:** original 6001 × 0.020s samples (120s); matched 64589 × 0.005s samples (322.94s). This is NOT ordinary trivial resampling. Require the saved SeismoMatch project, export history and processing explanation before design use.
2. **Loma Prieta paired end times:** matched A has **7996** points and B **7997**, a difference of 0.005s. Use an explicit end-of-record common domain policy, retaining hashes (zero-extension after a measured end is an option for engineering review; do not silently truncate/pad).
3. **Other sample counts:** 14 of 16 matched files end exactly one original time step earlier; inspect exporting conventions and do not fabricate a final acceleration sample. Gorkha is the duration exception.
4. **Initial SeismoMatch scale factors NOT AVAILABLE:** Do not interpret `matched_PGA / original_PGA` as the initial SeismoMatch scaling factor; spectral wavelets change waveform shape. NBC 105:2025 §9.3.2.2(c) individual 0.33–3 and §9.3.2.2(d) lower-of-two pair factor must be independently checked from SeismoMatch session/log.
5. **Fitting period 0.05–6s:** the actual `[Tn90, sqrt(R_mu) * T1]` interval must be recomputed for BOTH axes from the current model. For `R_mu=3.5` the upper bound reaches 6 seconds at `T1≈3.207s`. A working `T1=3.622s` implies `≈6.776s`, exceeding fitted 6 seconds. Preserve the NBC Figure 4-2/§9.3.2.2 issue for reviewed interpretation.
6. **Target normalization:** confirm actual `Z`, `I`, `Omega_u`, full `C_h(T)` and spectral ordinates before certifying design-level matching.
7. **Numerical integration step:** distinguish record sample interval from OpenSees analysis step, and enforce NBC 105:2025 §9.3.2.4 using both modal axes.
8. **Scientific scope:** this is *input record screening*, not acceptance of actual frame reinforcement, FSAM wall model, damper devices, gravity/mass, or the previously failing X-direction nonlinear wall step.

## Code traceability and usage

- See [`tools/verify_matched_waveforms.py`](../../tools/verify_matched_waveforms.py) to verify all 16 matched source hashes, PGA, dt, duration and pair consistency locally. It runs with only Python standard library, does not change inputs, and can emit a JSON result.
- Source register: [`matched_component_register.csv`](matched_component_register.csv); no accelerogram samples are included in this public repository.
- Existing `components/nonlinear_time_history/seismomatch_audit.py` screens matched imports and period-window coverage; `nbc105_horizontal_input.py` documents the two Path patterns and scale one. Waveforms and SeismoMatch session files should remain local/private.
- NBC source: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf, clauses 4.1 and 9.3.2.
