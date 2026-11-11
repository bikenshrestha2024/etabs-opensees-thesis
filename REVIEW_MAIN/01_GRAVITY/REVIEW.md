# Gravity engineering review
**RV-GRV-001 Support-reaction equivalence** — P0 OPEN_BLOCKER
**RV-GRV-002 Load and weight equivalence** — P0 OPEN_HIGH
**RV-GRV-003 32/76/97-node sensitivity and visualization** — P1 INVESTIGATE

## Observed evidence
- 32-support OpenSees `1.0D+1.0L` result: downward applied 311367.31387955 kN; recovered Rz 311367.3138800 kN, internal equilibrium ~1.87e-14%. This proves **equilibrium of this assembled OpenSees load**, not agreement with ETABS load or distribution.
- Separate MRSM gravity preload uses 286419.758231 kN with 76 support nodes and D+0.3L, excluding roof live. Do not compare against 1.0D+1.0L.
- Native ETABS: 76 originally restrained locations but only 32 reported reaction-bearing locations for the selected case; 44 with zero ETABS Rz reportedly have nonzero OpenSees reactions. Wall mesh constraints and support-point mapping need native investigation.
- Earlier gross-beam case (repository engineering gates) ETABS 311367.314 kN vs OpenSees 320019.758 kN (~8652.444 kN). Do not treat this historical mismatch as the current 311367.314-kN re-export.
- GUI comparison action produced error `'rz_32_kN'`; likely an absent field/key or inconsistent schema, not evidence of a structural failure.

## Professional engineering hypotheses (not yet proven)
1. Support local/global DOF and shell mesh node restraints not mapped identically, including ETABS auto mesh and reaction aggregation.
2. Different rigid end offsets, frame clear-length assumptions, and slab/beam/column/wall self-weight overlap or omissions.
3. Distinct imposed load-pattern self-weight multipliers or live-load cases.
4. Reactions from different object-versus-analysis joint grouping and equalDOF/rigid-diaphragm constraints.
5. Different effective axial/bending stiffness redistributing joint reactions even where total vertical force matches.

## Mandatory native tests
A. Record exact load combination, ETABS dead/live patterns and self-weight, analysis step; export ALL joint reactions at **all** 76 source restraints (zero included), at 32 observed active reaction points and 97 mesh-supported sensitivity nodes separately.
B. Compare total FX FY FZ MX MY MZ, common origin and signs and total load ledger for each **same** case.
C. Mapping join by original joint IDs and xyz tolerance, not unreviewed renumbering; classify original 32 vs remaining 44; count constraint DOFs, master/slave relationships.
D. Repeat 32/76/97 OpenSees cases with identical source loads and distinct solve results; report max vertical displacement, reaction at each source location, sum and RMSE/MAE (do not invent absent cases).
E. Plot reactions on common plan, Rz support bar charts, vertical settlement and member forces with comparable scales. Record schema failures separately.

**Gate:** support reaction correspondence and physical load transfer must be verified before seismic design comparison. Differences must never be hidden by changing applied loads to force equilibrium.
