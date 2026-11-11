# Review case: RV-<STAGE>-NNN
**Severity:** P0/P1/P2
**Status:** OPEN_BLOCKER / OPEN_HIGH / INVESTIGATE / CLOSED_VERIFIED
**Reviewed on:** YYYY-MM-DD
**Reviewer:** TBD

## 00 Issue and problem statement
Exact observed symptom, analysis state, baseline, expected response; never assert a cause without evidence.

## 01 Source/input manifest
EDB SHA256, Excel SHA256 and source cells, Git SHA, ETABS version, OpenSeesPy version, OS, run time, source/model export, units (kN–m–s), state ULS/SLS, case and gravity combination, support set.

## 02 Native ETABS
Run evidence, joint/area/frame IDs, constraint configuration, reactions, spectra, modal shape, storey data, verified unit and sign; paths and SHA. Do not commit sensitive original data.

## 03 OpenSees
Model build SHA, element/node map, solver settings, statuses, outputs, log, native test case and accepted step.

## 04 Comparison tables
Metric | Case | Location | ETABS | OpenSees | Unit | Delta | Difference (%) | Evidence | Status.
Missing case must say MISSING, not 0.

## 05 Plots
Comparable axes, units, common level coordinates; modal shape, story shear/displacement/drift, joint reactions. State explicit CQC versus signed history distinction.

## 06 Engineering judgement
Separate OBSERVED, HYPOTHESIS, TEST, CONFIRMED CAUSE, IMPLICATION; list governing NBC 105:2025 and IS 13920:2016 clauses as actually applicable, exact source/edition and assumptions; state whether safe to use for thesis.

## 07 Corrective actions
Small reversible code/model fixes with before/after source hash; native input preserved.

## 08 Tests and acceptance
Software tests, native ETABS and OpenSees reruns, numeric/physical validation and review signature as separate flags: SOURCE_CHECKED, NUMERICALLY_CONVERGED, ETABS_OPENSEES_MATCHED, EXPERIMENT_VALIDATED, CODE_ACCEPTED.

## 09 Signoff and decision
OPEN / NOT FOR DESIGN / CONDITIONALLY_REVIEWED / CLOSED_VERIFIED with reviewer/date and supporting hashes.

## 10 Private evidence
Store locally, exclude from public Git; provide redacted ZIP only when approved.
