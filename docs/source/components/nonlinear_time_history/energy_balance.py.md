# energy_balance.py — implementation guide

**Source:** [components/nonlinear_time_history/energy_balance.py](../../../../components/nonlinear_time_history/energy_balance.py)
**Workstream:** 06 Recorders. Added on branch `improve/damping-energy-viz` (2026-11-07).

## What it does

`EnergyBalanceRecorder` integrates the relative-motion energy equation over each accepted step (trapezoidal rule): input energy `-Σ m v a_g`, kinetic energy, Rayleigh energy (`aM Σ m v²` plus element `rayleighForces · v`), structural strain + hysteretic energy (`eleForce · Δu`, structural elements), device energy (excluded elements) and the work of constant gravity `P_g · (u − u0)`. `P_g` is recovered from element resisting forces at the converged gravity state. Outputs `Energy_Balance.csv` and `Energy_Balance.json` with PASS/FAIL against `energy_balance_tolerance` (default 0.05 of the peak input energy).

Enabled in `building_exploratory.py` by `energy_balance: true`. It is opt-in because it loops over every element in Python at every accepted substep. Recoverable strain energy is not separated from dissipated hysteretic energy.

## References

Uang & Bertero (1990) Earthquake Eng. Struct. Dyn. 19(1):77-90; Christopoulos & Filiatrault (2006), IUSS Press. Tag convention: [REF_TAG_CONVENTION.md](../../../../docs/REF_TAG_CONVENTION.md).

## Verification

Test: `tests/verify_damping_regions.py`. Passing tests establish solver behaviour on small test models or synthetic data. They do **not** establish convergence, calibration or NBC acceptance of the thesis building.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../../docs/00_THESIS_ACCEPTANCE_GATES.md)
