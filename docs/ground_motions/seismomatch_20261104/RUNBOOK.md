# Matched ground-motion verification — complete operating procedure

**Purpose:** reproducibly verify eight earthquake pairs (16 original PEER/KATNP AT2 files and 16 SeismoMatch matched exports) for the asymmetric high-rise NLTHA research program. The system preserves source waveforms, checks numerical provenance and records outstanding NBC 105:2025 design evidence. It must not create claims of earthquake/motion code compliance when primary scaling-session data are unavailable.

**Research code edition:** NBC 105:2025, §§4.1.1–4.1.2, 9.3.1, 9.3.2.1–9.3.2.4 and 9.3.3. Government PDF: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf.

## 00 — Repository and environment

- Use Python 3.12 (e.g. the project's existing conda-forge Spyder environment).
- All source-integrity utilities use **Python standard library only**. Do not install a third-party parser or upload earthquake time-series files.
- Execute from the repository root, or execute the scripts by filename using the same Python interpreter.
- Clone/pull main; **keep the 16 original `.AT2` and 16 matched `.txt` files in private local folders**, not the public GitHub repository. Never rewrite files merely to make a checksum pass.
- Default source registers are versioned under `docs/ground_motions/seismomatch_20261104`.

## 01 — Matched-file verification

```powershell
python tools/verify_matched_waveforms.py --matched-dir "D:/Thesis/Records/Matched" --output "D:/Thesis/Results/Matched_Source_Integrity.json" --markdown "D:/Thesis/Results/Matched_Source_Integrity.md"
```

The program checks:

1. Exactly 16 expected source filenames, non-duplicated event/component keys, and safe relative filenames.
2. The source `Time Series matched accelerogram` SeismoMatch export header, `Time Step: … s` and `Time(sec) Acc(g)` columns.
3. No missing, nonfinite, malformed or silently dropped numeric time/acceleration rows.
4. Declared dt, monotonically sampled times, start time, absolute PGA and raw-source **SHA-256** of every file.
5. Eight explicit A/B pairs with consistent dt, and independently consistent end-time status.
6. JSON + optional Markdown evidence without altering a single source byte.

**Exit codes:** `0` all 16 sources verified and eight pairs share end time; `2` missing/modified source or parsing errors; `3` all 16 sources verified but at least one pair needs timing-policy review. The study's Loma Prieta pair is expected to return **3** until a documented end-of-record policy is accepted; this is **not** a corrupt source hash. You can still inspect the complete report. There is no automatic zero padding, resampling or shortening.

## 02 — Original-vs-matched lineage verification

```powershell
python tools/verify_original_matched_pairs.py --original-dir "D:/Thesis/Records/Original" --matched-dir "D:/Thesis/Records/Matched" --output "D:/Thesis/Results/Original_Matched_Lineage.json"
```

For each original PEER/KATNP `.AT2` file, the program independently checks the `ACCELERATION TIME SERIES IN UNITS OF G` header, `NPTS`, `DT`, all numeric acceleration ordinates, source SHA256, PGA and declared sample count. It then joins each original A/B event-component identity with the corresponding matched register to tabulate original vs matched duration and PGA. Original and matched records are **read-only**.

**Source-specific engineering reviews:**
- Gorkha originals have 120-second waveform span while the matched outputs last 322.94s; investigate SeismoMatch project/resampling/export version.
- Loma Prieta matched A/B differ by 0.005s; preserve originals and choose/document a paired end-of-record analysis policy before solver use.
- Northridge matched record dt=0.020s; integration at dt=0.005s is a separate solver setting and requires the modal bound.
- Never infer SeismoMatch's original amplitude scale from matched PGA / original PGA; time-domain wavelet matching changes shape.
- Matching summaries are **conditional** 5%-damped target diagnostics, not a formal NBC spectral-fit pass.

## 03 — Site target and period interval

Use **actual, reviewed** project parameters and the published Soil C spectral shape:

```
C(T) = C_h(T) Z I
target_ULS(T) = C(T) / Omega_u
T_fit = [Tn90, sqrt(R_mu) T1]
```

Figure 4-2 and Eq. 4.1(2) apply to the spectral shape, whereas §9.3.2.2 specifies the normalization used in NLTHA. Verify your target file has the *correct units and amplitude*; a conditional plateau of 0.625g implies `Z*I/Omega_u=0.25` if `alpha=2.5`, but does not prove adopted `Z,I,Omega_u`.

If `R_mu=3.5`, an upper limit of 6s covers the modal band only for `T1<=6/sqrt(3.5) ≈ 3.207s`. Use actual latest ULS and SLS model periods; earlier 3.622s would imply about 6.78s. If >6s, document the interpretation of the standard's figure/end range and your extension approach instead of claiming compliance without evidence.

## 04 — SeismoMatch scale-factor and pair rule

**SeismoMatch output records are already matched.** For original component A and B:

- Reproduce X and Y independent initial spectral factors from the actual SeismoMatch session and review §9.3.2.2(c) **0.33–3.0**.
- §9.3.2.2(d): adopt `min(factor_A, factor_B)` for **both** horizontal components; verify the matching procedure used that common value.
- Store actual SeismoMatch **session, target ordinates, scale-factor logs, matching method, and source SHA** in private project evidence.
- Do not use postmatching PGA ratio as the factor, and do not apply matching a second time inside OpenSees.

## 05 — OpenSeesPy source and acceleration unit mapping

For raw `Acc(g)` ordinates from **already matched** files and a **kN–m–s** nonlinear structural model:

```python
from openseespy import opensees as ops
assert source_records_already_scaled is True
additional_spectral_scale = 1.0
unit_conversion = 9.80665  # g -> m/s^2, not a new spectrum scale

ops.timeSeries("Path", tsA, "-dt", dtA, "-values", *values_A_in_g,
               "-factor", unit_conversion)
ops.timeSeries("Path", tsB, "-dt", dtB, "-values", *values_B_in_g,
               "-factor", unit_conversion)
ops.pattern("UniformExcitation", pattern_A, 1, "-accel", tsA)  # X
ops.pattern("UniformExcitation", pattern_B, 2, "-accel", tsB)  # Y
# YX: build a SEPARATE fresh model; B->DOF 1, A->DOF 2.
```

The OpenSees `Path` factor converts acceleration units. `UniformExcitation` produces response **relative to the support**. Both horizontal components must act simultaneously in XY and YX, not as a succession of X-only/Y-only static analyses. Follow [NBC XY/YX full command guide](../../programs/33_NBC105_XY_YX_VERTICAL_AND_SCALE_GUIDE.md).

## 06 — NLTHA and time-step evidence

Do not run production 25-storey NLTHA solely because the matched source file passes SHA. Check:

- Exact ETABS geometry, diaphragms, actual reinforcement, walls/openings, gravity and mass.
- Concrete/steel/FSAM specimen calibration, FVD/BRB device tests and energy signs.
- Numerical stability in ZERO, X, Y and XY, including the unresolved X-direction first-step wall failure.
- `dt_analysis <= min(dt_record, T1_x/100, T1_y/100, Tn90_x, Tn90_y, 0.01s)` where applicable from reviewed modal evidence.
- Only accepted full-duration XY and YX transients count as complete. Preserve snapshots, solver input hashes and rejection records.
- The response aggregation under §9.3.3 has an exactly-seven-pair textual ambiguity that needs documented interpretation before a normative claim.

## 07 — Output schema and status glossary

| JSON key | Meaning |
|---|---|
| `records[].sha256` | Computed SHA256 of each EXACT matched export |
| `records[].samples` | Observed numerical acceleration sample count |
| `records[].dt_s` | Header dt in seconds; checked against all sample times |
| `records[].end_time_s` | Last source time in seconds, not assumed `N*dt` |
| `records[].max_abs_acceleration_g` | Absolute peak from source values in g |
| `pairs[].same_sampling_interval` | Both components have same sample dt |
| `pairs[].same_end_time` | Both components end at the same recorded time |
| `source_integrity_status` | `MATCH` / `FAIL` against source registry |
| `pair_synchronization_status` | `SYNCHRONIZED` / `REVIEW_REQUIRED` |
| `pair_synchronization_review_count` | Number of event pairs needing end-time/dt policy review |
| `status` | `SOURCE_AND_PAIR_INTEGRITY_PASSED`, `SOURCE_INTEGRITY_PASSED_PAIR_REVIEW_REQUIRED` or `SOURCE_DISCREPANCIES` |
| `nbc105_scale_factor_033_to_3_verified` | Always `false` until the **original** SeismoMatch scale-factor source is separately established |
| `nbc105_common_lower_factor_verified` | Always `false` without session/source proof |
| `independent_target_spectrum_pass` | Always `false` until the reviewed source target and genuine spectral fit are proven |

For the original-vs-matched lineage JSON, `waveforms[].duration_change_s` describes physical waveform span change; `original_failures` counts original SHA/header/NPTS/PGA problems and is separate from pair-synchronization warnings.

## 08 — Test and CI procedure

```powershell
python tests/verify_matched_waveform_register.py
python tests/verify_original_matched_pairs.py
python tests/verify_seismomatch_audit.py
```

CI executes synthetic controlled records with truncation, wrong units, malformed data, unsafe manifest paths, original NPTS mismatch and Loma-like end-time disagreement. **Synthetic tests are software tests only.** For a real complete suite rerun both verifiers on source files locally, review resulting JSON/Markdown and retain fingerprints with each M0–M6 analysis input.

## Sources and result register

- [Actual 16-file matched metadata and conditional PSA audit](README.md)
- [Matched file SHA register](matched_component_register.csv)
- [Original file SHA register](original_component_register.csv)
- [Previous detailed six-component preliminary audit](../../00_SEISMOMATCH_MATCHED_RECORDS_AUDIT_20261104.md) — superseded
- OpenSees `Path`: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/timeseries/pathTimeSeries.html
- OpenSees `UniformExcitation`: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html
