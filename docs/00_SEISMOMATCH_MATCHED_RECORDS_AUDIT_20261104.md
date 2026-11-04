# SeismoMatch ground-motion double verification — 2026-11-04

**Status:** PARTIALLY VERIFIED / SOURCE SCALE FACTORS AND EIGHT COMPLETE XY PAIRS NOT AVAILABLE TO THIS AUDIT.

This review uses the official NBC 105:2025 PDF and six actual X-direction `Matched_*.txt` source files present in the user's attached Library. The numeric time-series values were read independently (not merely from the filename), and mean sample increments and absolute peak acceleration were computed. No underlying acceleration file bytes were uploaded into GitHub; only the name and non-sensitive numerical checks below are recorded. The user's thesis draft `MSc_Thesis_Report_FINAL_COMPLETED(1).docx` Table 9.1 is the reference for the published/report PGA comparison.

## NBC 105:2025 source

- §4.1.1 / Eq. 4.1(1): `C(T) = Ch(T) Z I`.
- §4.1.2, Figure 4-2 / Eq. 4.1(2): `Ch(T)` for nonlinear time-history spectral target. Soil C: alpha=2.5, Ta=.1 s, Tc=1.0 s, Td=4.0 s.
- §9.3.2.2(a): target `C(T)/Omega_u`; spectral shape alone is not the entire design target.
- §9.3.2.2(b): fit `[Tn90, sqrt(R_mu)*T1]`.
- §9.3.2.2(c): factors between 0.33 and 3.0; reject outside.
- §9.3.2.2(d): separately obtain both component factors and use **lower for the two-component pair**. A wavelet-matched export does not contain these original factors.
- §9.3.2.3(c): actual paired cases XY and YX. Single X files are insufficient to verify complete 3D suite.
- §9.3.2.4: integration dt <= record digitization dt, T1/100, Tn90 and 0.01s.

Authoritative source: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf .

## Six inspected matched component files

All six start with `Time Series matched accelerogram` and label the ordinate `Acc(g)`. The SeismoMatch time-domain output is therefore **already processed**; apply only `9.80665` as the conversion from g to m/s² at OpenSees Path input with additional `scale=1.0`.

| Earthquake X-file | Sample step (s) | End time (s) | Maximum abs acceleration in stored file (g) | Thesis Appendix 9.1 final X PGA (g) | Agreement |
|---|---:|---:|---:|---:|---|
| Gorkha `Matched_KATNP.HNE.NQ.01_a_EW_PEER_Gorkha.txt` | 0.005 | 322.940 | 0.29540 | 0.158 | **MISMATCH; may be a different matching/correction version** |
| Landers `Matched_RSN879_LANDERS_LCN260.txt` | 0.005 | 48.115 | 0.32585 | 0.326 | Matches rounding |
| Northridge `Matched_RSN1086_NORTHR_SYL090.txt` | 0.020 | 39.960 | 0.37937 | 0.379 | Matches rounding |
| Kobe `Matched_RSN1120_KOBE_TAK000.txt` | 0.010 | 40.940 | 0.26518 | 0.265 | Matches rounding |
| Kocaeli `Matched_RSN1165_KOCAELI_IZT090.txt` | 0.005 | 29.990 | 0.34635 | 0.346 | Matches rounding |
| Chi-Chi `Matched_RSN1505_CHICHI_TCU068-E.txt` | 0.005 | 89.990 | 0.37654 | 0.377 | Matches rounding |

**Do not calculate SeismoMatch original scale factor as PGA matched / PGA original.** SeismoMatch wavelets modify acceleration history and the original pair fit factor must be recovered from the actual exported session/report and original/spectrally fitted cases.

**Missing data:** No matched Y-direction file, no Hector Mine/Loma Prieta matched file, and no SeismoMatch per-record original X/Y scale-factor report were available in this verification. Therefore **NOT VERIFIED**: all eight complete pairs, every original factor in 0.33–3, and the common lower-factor pair application. The thesis separately reports X/Y mean spectral misfit and the 0.625g target, but those summaries do not establish the original scale-factor logs.

## Is 0.05 to 6.0 seconds adequate?

For `R_mu=3.5` from the current report, `Tupper=sqrt(3.5)*T1`; `Tupper<=6` only when `T1<=3.2071349` seconds. If actual `T1=3.622s`, then the upper period is approximately 6.776s, outside the fitted range. Verify current ULS modal `T1_X/T1_Y` and `Tn90_X/Tn90_Y` separately and report both required windows. Figure 4-2 and Eq.4.1(2) themselves display a 6-second upper bound, creating a need for explicit engineering interpretation before a claimed 6.78-s code fit.

The reported 0.625g spectral plateau is consistent with `Ch_peak=2.5` only for `Z*I/Omega_u=0.25`. A documented example is Z=.35, I=1, Omega_u=1.4; this is NOT proof of the adopted site Z and importance.

## Required data for final verification

1. Original **SeismoMatch project/session report** with both X/Y original component scale factors for every event, wavelet matching/processing settings and actual target spectrum ordinate file.
2. Source unmodified X/Y accelerograms and the final matched X/Y records (all eight near/far-field pairs), with units, time interval, duration, provenance.
3. Current 3D modal table with T1_X, T1_Y, the modes completing 90% translational participation in both directions, and record source hashes.
4. Compare actual matched 5%-damped acceleration response spectra against the target `Ch(T) Z I / Omega_u` over the required interval, document residual and acceptance criterion.
5. Resolve Gorkha stored X record PGA discrepancy with the thesis appendix and verify consistent raw/final records and station identification.

## Program changes arising from the audit

- `components/nonlinear_time_history/seismomatch_audit.py`: detects matched input headers, records file SHA and rejects additional `scale!=1`. `screen_fitting_window` tests whether the selected modal interval is covered.
- `components/nonlinear_time_history/building_exploratory.py`: uses `SeismoMatch_Source_Provenance.json` to record source state, and `source_records_already_scaled=true, scale=1.0` for matched sources without duplicate amplitude factor. The source `Acc(g)` is still converted to m/s².
- `components/nonlinear_time_history/nbc105_horizontal_input.py`: permits already matched files at scale1, blocks secondary scaling.
- `tests/verify_seismomatch_audit.py`: solver-free provenance and fitting-period checks.

**This is a source/format and arithmetic audit, not a completed NBC spectral-fit certification or native full-duration NLTHA.**
