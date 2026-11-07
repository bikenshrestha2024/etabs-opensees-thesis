# exploratory_options.py — implementation guide

**Source:** [components/ui/exploratory_options.py](../../../../components/ui/exploratory_options.py)
**Workstream:** 06 Isolated nonlinear probes. Added on branch `improve/damping-energy-viz` (2026-11-07).

## What it does

It validates the settings in the exploratory window's **Diagnostics, damping and case identity** panel and turns them into RunConfig keys for `building_exploratory.run`. Before this, these settings could only be set by editing `RunConfig.json`:

| Panel control | RunConfig key | Rule |
|---|---|---|
| Excitation XY / X / Y / ZERO | `diagnostic_excitation` | X, Y and ZERO are diagnostic probes ([V168 guide](../../../../V168_FIRST_STEP_DIAGNOSTICS.md)) |
| Damping: Rayleigh / ZERO / mass-only | `diagnostic_zero_damping`, `diagnostic_mass_damping` | ZERO and mass-only are diagnostic |
| Inherent ratio + "allow above 2.5%" | `inherent_damping_ratio`, `inherent_damping_five_percent` | (0, 0.025] by default; up to 0.05 only with the box ticked |
| Damping reference modes | `damping_reference_modes` | two distinct 1-based modes ≤ 20; blank = exploratory first/last-mode fit |
| Record energy balance + tolerance | `energy_balance`, `energy_balance_tolerance` | tolerance fraction in (0, 1) |
| Variant | `variant_id` | UNASSIGNED or M0–M6 |
| (from the Earthquake list) | `pair_id` | mapped to the Soil-C event name (Kobe, Chi-Chi, …) |

To repeat the documented first-step failure, choose **Excitation X**, **ZERO damping** and a **0.1 s** trial.

## References

V168 first-step diagnostic guide; PEER TBI 2017 / LATBSDC 2020 (2.5% inherent damping); NBC 105:2025 §8.1.1 as cited in the repo (5% cap); Uang & Bertero (1990) (energy). Tag convention: [REF_TAG_CONVENTION.md](../../../../docs/REF_TAG_CONVENTION.md).

## Verification

Test: `tests/verify_exploratory_options.py` (option rules, Soil-C event mapping, panel build under a display). This is not a structural validation.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../../docs/00_THESIS_ACCEPTANCE_GATES.md)
