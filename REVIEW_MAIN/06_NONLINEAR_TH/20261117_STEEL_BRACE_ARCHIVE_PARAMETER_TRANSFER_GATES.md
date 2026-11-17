# Literature-to-model transfer gate — Uriz (2008), Karamanci–Lignos (2014), Wilson–Morrison HSS archive

**Date:** 2026-11-17. **Review state:** SOURCE READ / ARCHIVE NUMERIC-INTEGRITY AUDITED / PROPOSED EXPERIMENTS ONLY. **NOT** engineering acceptance, **NOT** source-model equivalence, **NOT** nonlinear wall convergence and **NOT** evidence of completed M0–M6 NLTHA.

Detailed citations, ZIP contents, per-family schema, research equations, conditional validity ranges and source findings: [LITERATURE/2026-11-17_STEEL_BRACE_URIZ_KARAMANCI_HSS_DATASET_REVIEW.md](../../LITERATURE/2026-11-17_STEEL_BRACE_URIZ_KARAMANCI_HSS_DATASET_REVIEW.md).

## Independent source bundle and all-member investigation

**Original archive ZIP SHA-256:** `087fb4647344d07833f542475c71cb0c4d64b1f62b59cb44435cc1ad5cc99d46`. All 97 ZIP entries inventoried, 67 real files opened/read or parsed: 55 full specimen CSVs containing **1,145,745 numeric observations**, 4 geometry drawings, 4 specimen protocol PDFs (51 plot pages), 1 eight-page constitutive-model PDF, `CM.f90` (647 lines), README and BB measured-thickness note. All nine embedded PDFs opened and their available vectors/figures inspected; full 55-CSV parsing does not validate every lab value against instruments or verify all figure content as independent physics.

**CSV data-integrity results:** all five declared schemas match, no missing/nonfinite/nonnumeric cells, no invalid ramp indices and no empty specimen files. Quality exceptions, originals unchanged:

1. **DATA-QC-001 / BB measured thickness:** `experimental/docs/measurements/BB.txt` references a missing `BB/4x4x516-NHT/spec03` but the archived specimen under that designation is `spec02.csv`. Another record already assigns 0.2927 in to `spec02`; the conflicting 0.293 in cannot be uniquely attributed to a measured specimen. Do not silently relabel or substitute an average. Obtain actual specimen lab book.
2. **DATA-QC-002 / MC-C clock reversals:** `experimental/data/MC-C/4x4x14-NHT/SRC31.csv` has 3 decreasing `t(s)` entries at original source data lines **18210–18212** (within ramp 20), `1174.38→729.396→105.824→0.191426 s`. Strain-rate, cycle/dwell-time and energy-versus-time calculations on this span **BLOCKED** until original acquisition metadata reconcile it. Do not overwrite original `etrue`, `strue(ksi)` or timestamps.
3. **DATA-QC-003 / Fortran log helper:** `numerical/CM.f90`, `delete_empty_log`, uses local `line_count` without explicit initialization before increment. This is a probable portable-code defect, but the README's Intel `/Qinit=zero` option could mask it for that compiler. The issue is a **logging helper**, not confirmed failure of the UMAT stress update. Independently compile/test source in Abaqus 2024/ifx/MKL before changing authors' original implementation.
4. **DATA-QC-004 / Original source scope:** Wilson–Morrison specimens are *as-received cold-formed 4–5 in HSS*, nominal wall/corner coupon response and conventional buckling specimens, **not** source-calibrated 350×350×16 mm building outriggers, proprietary BRBs, physical FVDs, RC Fe500 rebars or core shear-wall materials. The J2 Abaqus UMAT is not an OpenSees plugin.

## Thesis's existing baseline vs available evidence

The active paper-backed project note `docs/OUTRIGGER_MATERIAL_SENSITIVITY_AND_VALIDATION.md` states **ordinary steel outrigger = corotational axial truss + Steel01**, Fy=345 MPa, b=0.01 unless a separate source-controlled sensitivity changes it. This is an axial-only tension/compression idealization, **not** a model of brace Euler/flexural buckling, strain localization, wall local buckling, low-cycle-fatigue fracture or gusset rotational slip. Do not claim the existing truss validated by Uriz.

Uriz et al. **2008** supports an *optional* corotational **force-based fiber beam-column** model (two inelastic elements, 0.05–0.1% midspan camber, three integration points) for studied compact conventional braces' **global hysteresis**. Critical local strain, fracture and noncompact local wall buckling require further independent refinement/modeling. Its original published numerical results do not fix RC wall 110280.

Karamanci and Lignos **2014** uses a *different* fatigue-aware SCBF calibration family, including two force-based elements or an alternate eight-segment displacement-based model with five integration points, specimen-derived Coffin–Manson parameters and deteriorating gusset/frame behavior. Its rectangular HSS `epsilon_0` equation is limited to `27<=kL/r<=85`, `4.2<=w/t<=30.4`, `223<=Fy<=532 MPa`, with R²=0.493. It is **not** authorization to transplant fatigue constants to the user's 350×350×16 section or to a BRB. It finds that conventional initial-stiffness Rayleigh damping in degraded conventional braces can create fictitious damping force and misleading near-collapse behavior. **Isolate physical FVD device work from intrinsic Rayleigh damping** rather than changing solver damping blindly.

## Measurable follow-up experiments and exact acceptance evidence

| Gate | Experiment | Closure evidence | State |
|---|---|---|---|
| BRACE-G0 | Original archive/source SHA, specimen IDs, all 55 CSV schemas, length and numeric QA | Audited totals above and private SHA ledger; retain two source exceptions | **PASS numeric inventory; warnings** |
| BRACE-G1 | Original source SHS drawing, actual geometric flat width/corner radii, steel grade/coupons, end gusset/buckling effective length and local axes | Source EDB and source-material certificate matched; CSV units checked | **OPEN** |
| BRACE-G2 | MC-W versus MC-C coupon hysteresis and specimen BB cyclic loop under original protocol | Independent initial E/Y/strain fit and specimen-displacement/force loop error, strain history, source geometry and robustness | **OPEN** |
| BRACE-G3 | Conventional fiber brace: 2/4/8 elements, 3/5/7 integration points, 0.05/0.1% midspan camber; end-connection and fiber refinement | Stable global force–displacement/energy, compressive instability, critical curvature/strain and mesh/step sensitivity; no silent baseline replacement | **OPEN** |
| BRACE-G4 | Optional fatigue/fracture: correct 2014 valid sample, low-cycle strain history, rainflow/Coffin–Manson and wall-local-buckling caveat | Predicted fracture vs independent conventional brace experiment; not a BRB certificate | **OPEN** |
| BRACE-G5 | Structural region Rayleigh energy vs FVD work vs brace hysteretic work; kN/m/s units, C and alpha; verify no spurious damping/negative stiffness contributions | Exact model-device force/velocity/work, damping coefficient and end supports | **OPEN** |
| BRACE-G6 | Prior mandatory native high-rise engineering parity: 32/76/97 supports, full six-component wall cuts, element 110280, first-step ZERO/X/Y/XY | Original ETABS model, mapped analytical joints, connected one-bay wall/brace, full finite accepted histories and replicated result files | **OPEN** |
| BRACE-G7 | Preserve original **M0–M6** options, plus separately named alternative steel-brace physics; execute **224** required XY/YX orientation histories | Full accepted time histories, source SHA, model/device identity, dt sensitivity, energy accounting and independently reviewed response | **OPEN** |

**Project default preservation:** Don't change `Steel01`, existing SHS area, brace solver type, FVD C/alpha, BRB, governing record suite, connection stiffness, supported wall mesh, original M0–M6 geometries, or original source exports merely because the published studies use different models. Additional member/UMAT transfer is an optional separately labeled research implementation with a strict before/after comparison and rollback.

## Suggested output organization for future native work

```
REVIEW_MAIN/06_NONLINEAR_TH/
  20261117_STEEL_BRACE_ARCHIVE_PARAMETER_TRANSFER_GATES.md   # present evidence
  BRACE_SPECIMEN_QA/                     # future local, non-public CSV-derived QA
  BRACE_MATERIAL_COUPON/                 # future MC-W and MC-C fit/test outputs
  BRACE_BUCKLING_BB/                     # future conventional HSS BB benchmark
  BRACE_FATIGUE_AND_GUSSETS/             # future experimental and model comparisons
  BRACE_DAMPING_ENERGY/                  # future structural/FVD energy split
  BRACE_BUILDING_TRANSFER/               # future alternative M0–M6 controlled tests
```

**Documentation scope:** The original user's ZIP and publisher PDFs are retained outside public GitHub; only these authored interpretations are committed. The dataset's README explicitly states CC BY 4.0 for the *dataset*, which does not automatically change the copyright of ASCE articles. The user receives a separate local ZIP containing **all 67 file hashes, all 55 specimen QA rows, a reproducible audit script and a detailed report**.

**Acceptance statement:** Literature and numeric archive **REVIEWED**; instrument/lab provenance and Fortran compile **NOT VERIFIED**; steel coupon/brace component model calibration **NOT RUN**; ETABS–OpenSees local gravity equivalence **NOT VERIFIED**; X-wall first-step divergence **UNRESOLVED**; 224-run M0–M6 thesis NLTHA **NOT VERIFIED**. Do not close issue #75 based on this paper review.
