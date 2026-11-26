# clause_07_missing_mass.py — source documentation

**Python source:** [components/nbc105/clause_07_missing_mass.py](../../../../components/nbc105/clause_07_missing_mass.py)
**Git baseline content SHA:** NEW (added 2026-11-26)
**Subsystem:** NBC 105:2025 clause modules (7.3)
**Priority:** P1 — arithmetic only; model-data integration open

## Responsibilities and contracts
Printed 7.3 (p. 41): the modal combination uses only modes with natural frequency less than 33 Hz; modes above 33 Hz are included by "the missing mass correction procedure following established principles of structural dynamics". The print gives no formula, so the module implements the established residual-rigid-mass (zero period acceleration, ZPA) procedure on given modal data: `split_modes_by_cutoff` (f < 33 Hz combined; 33 Hz itself is unassigned and goes to the missing-mass side), `residual_mass_percent`, `residual_story_weights` (w_j (1 - sum G_i phi_ji)), `residual_static_forces` (ZPA coefficient x residual weight), `missing_mass_correction_inputs` (one direction, cross-check against the modal percentages), `combine_modal_and_residual` (SRSS, an established choice that the print does not state) and `missing_mass_gate` (the gate production uses).

## Integration point (open)
The eigen solver must give the storey mode-shape coefficients and effective masses of the included modes per direction, and the MRSM engine must add the residual story forces (and the ZPA coefficient from Eq. 7.1(1) at T = 1/33 s) to the combined modal forces. `components/modal/analysis.py` now records `missing_mass_gate` per direction; `components/response_spectrum/model_analysis.py` calls the gate and still refuses to export when a returned mode is at or above 33 Hz, now naming the exact missing inputs.

## Source, inputs, units
Weights in kN (any consistent unit), mode shapes dimensionless, frequencies in Hz, ZPA coefficient dimensionless.

## Outputs and failure conditions
ValueError for non-finite or inconsistent input; gate statuses `NOT_REQUIRED_ALL_MASS_COVERED`, `NOT_REQUIRED_NO_MODE_AT_OR_ABOVE_33_HZ`, `CORRECTION_INPUTS_SUPPLIED`, `BLOCKED_CORRECTION_INPUTS_MISSING`. Tests: `tests/test_nbc105_followup_missing_mass.py` (hand case with Eq. 7.1(2) identity, complete orthogonal mode set leaves zero residual).

## Research and standards
NBC 105:2025 clause 7.3; residual-mass method per standard structural-dynamics practice (not a printed formula). No native OpenSees run.
