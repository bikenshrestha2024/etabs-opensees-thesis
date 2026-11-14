# 2026-11-14 ULS OpenSees modal audit — 40 modes, X/Y participation

**Evidence:** user-supplied screenshot `image(20261114-063356).png`; data transcribed below from visible GUI, not independently recomputed or confirmed by a raw modal CSV. **Result class: NUMERICALLY_COMPLETED_NOT_ETABS_EQUIVALENT.** Paper crosswalk: [uploaded PDF matrix](../../LITERATURE/UPLOADED_PDF_TO_ENGINEERING_GATES_20261114.md), PEER TBI 2017/06 U11, V&V U03/U09.

| GUI field | Observed |
|---|---|
| Selected state | ULS |
| Eigenmodes | 40 |
| UX cumulative effective modal mass | 91.245% (console: 91.24498698137265%) |
| UY cumulative effective modal mass | 90.775% (console: 90.77458703166896%) |
| Modes at/above 33 Hz | 0 reported |
| Eigensolver elapsed | 18.185 s (TIMING 18.564 s) |
| Modal batch wall time | 110.3 s reported in completion row |
| Rayleigh T X field | approximately 3.89851390 s |
| Rayleigh T Y field | approximately 5.59044098 s |
| Input source | ULS; project X Aw grouping 2 connected 12-m walls, Y 3 solid 6-m walls; source geometry vs original workbook provenance flagged in GUI |
| Fundamental X/Y modal modes | Explicit optional mode IDs blank in screenshot |

## Independent formulation/experiment context from newly uploaded U15

The newest upload `dvorkin1984(1).pdf` (U15/L048; Dvorkin & Bathe 1984, original *Engineering Computations* article, DOI 10.1108/eb023562) illustrates why a numerically successful eigen solve is a limited screen:

- Original article pp. 79–81 describes six rigid-body shell element modes and no spurious zero-energy modes for their own proposed formulation; the source also provides membrane/bending/shear/twist patch tests. It does not establish that the particular OpenSees `ShellMITC4` + wall/beam + rigid diaphragm assembled model has no artificial mechanism.
- Original p. 83 Table 4 gives simply-supported *single plate* non-dimensional frequency ratios `f_FEM/f_thin-plate`: **1.02**, **1.18**, **1.17** for the authors' specified (1,1), (1,3), (3,3) shapes. These are *not* targets for the user's 25-storey, asymmetric and reentrant high-rise.
- Compare OpenSees/ETABS modal shapes by **mass-weighted modal assurance criterion**:
  `MAC_M(phi_i,psi_j)=|phi_i^T M psi_j|^2/((phi_i^T M phi_i)(psi_j^T M psi_j))`, after mapping physically equivalent DOFs, reference geometry, masses and orientation. High MAC does not independently prove stiffness/load-path equivalence; coupled bending/torsion may legitimately mix modes.
- Compute first modal frequencies `f_i=sqrt(lambda_i)/(2*pi)`, periods `T_i=1/f_i`; preserve unit-consistent mass matrix and positive eigenvalue checks. Rayleigh static reference periods and NBC adopted code-action periods are **different data products** and should never occupy one ambiguous `T1` column.
- Current GUI screenshot shows `Rayleigh TX=3.89851390s`, `TY=5.59044098s` as **input/reference fields**, 40 solved modes and UX/UY mass sums **91.245/90.775%**. Without the actual 40-row eigenfile, it is impossible to know which modes are fundamental X/Y/torsion or whether their periods match ETABS.
- For 40-mode acceptance, examine *all* solver eigenvalues and full effective-mass distribution, plus first lateral and torsional shapes at each story. Do not only require percentage ≥90; review missing-mass correction, 33Hz cutoff and nearby modes under §7.3/7.4 in the project's verified NBC text.

**New reference:** [Dvorkin/Bathe figure–table crosswalk](../../LITERATURE/DVORKIN_BATHE_1984_SHELL_BENCHMARKS.md). Source-to-physical model applicability remains `REFERENCE_ONLY`. Neither the original paper nor the modal screenshot verifies the assembled frame/wall interface or native ETABS response.

## Correct reading of these results
- The modal audit reports numerical 90%-plus translational cumulative participation in X and Y, consistent with the GUI's cited NBC 105:2025 §7.3 screening. **This does not prove the correct number of modes for every response, nor lateral mode identification or model accuracy.** Obtain full eigenfrequency, mode shape and DOF participation workbook.
- The 3.8985-s and 5.5904-s numbers shown are labelled **Rayleigh T X/Y**, so they MUST NOT automatically be reported as the first two modal eigenperiods. Rayleigh reference periods also may differ from code-adopted design-action periods, modal periods, and original ETABS eigenperiods.
- Compare periods only for source-matched ULS model geometry, 76-source supports, actual effective stiffness, masses, floor diaphragms and the same gravity state. The earlier historical model's ~2.0-s periods are not a valid comparison until identity and calculation basis are established.
- OpenSees with asymmetric reentrant core may have coupling and modal order changes. Identify fundamental UX, UY and torsional character by shape and mass participation, not by assumed modes 1/2/3.
- Full 40-mode relative effective mass, residual eigenvalues, 33 Hz cut-off and conditioning are needed to verify the computation; 0 modes >=33 Hz does not establish no missing-mass correction for all analysis configurations.
- The modal run is a separate process; reuse only verified input provenance, not an assumed retained OpenSees domain.

## Small reproducible audit to run next
1. Save exact current EDB SHA, model-builder script SHA, runtime/solver version, ULS config and source-matching restraint table.
2. Export CSV per mode: mode index, eigenvalue, f Hz, period s, UX/UY/RZ effective mass, cumulative UX/UY, dominant mode character, mode-shape sign/orientation and any unstable modes.
3. Export ETABS eigenresults **from the same source and stiffness state** and calculate signed/nonnegative mass-weighted modal assurance criterion (MAC) with an explicit matched-DOF map; compare fundamental modes without relying on ordinal numbers alone.
4. Separate `Rayleigh_preliminary_TX/TY`, `ETABS_eigen_TX/TY`, `OpenSees_eigen_TX/TY` and `NBC_adopted_design_TX/TY` into distinct workbook columns with formula provenance and accepted state.
5. Confirm independent mass ledger, rigid-diaphragm master DOFs and rotational inertia for the reentrant asymmetric floor plan; report restrained versus total mass and residual modes.
6. If ETABS and OpenSees eigenfrequency mismatch persists, change **one** of boundary conditions, shell/beam member stiffness, wall effective EI, offsets or mass assignments per controlled experiment. Do not tune multiple model factors to achieve period coincidence.

## Evidence-based status
- 40-mode numerical solve: COMPLETED as reported in GUI.
- X and Y cumulative translational participation >90%: SCREENING_PASS as reported in GUI.
- ETABS/Opensees physical eigenfrequency/mode-shape agreement: NOT_VERIFIED.
- Rayleigh/empirical/NBC-adopted period reconciliation: NOT_VERIFIED.
- Foundation-reaction transfer and local wall nonlinear calibration: NOT_VERIFIED.
- NBC design acceptance: NOT_GRANTED.

**No numerical model was modified by this literature intake.**
