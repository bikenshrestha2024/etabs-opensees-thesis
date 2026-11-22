# Implementation plan — NBC105 Clause 5 Rayleigh routing & saved CSV integrity (2026-11-22)

**Scope:** Preserve existing ETABS→OpenSees physical model untouched. Improve only source/period provenance and numerical centralization. No claim of native model equivalence.

## Source requirements
- NBC 105:2025 §5.1.1: `2π√[Σ(Widi²)/(gΣ(Fidi))]`; `di` centre-of-mass elastic lateral motion with torsion suppressed.
- §5.1.2/§5.1.3: wall-index empirical period and `1.25` cap; `min(TR,1.25Temp)` as adopted design-action period.
- §5.2 Table 5-1: dead=1, storage live=.6, other live=.3, roof live=0.
- High-rise ULS ESM is comparison-only under §3.2.1; missing Vs30 for >40 m leaves subsoil unverified. ULS-only ETABS model must not be relabelled SLS.
- Confirm physical 32 foundation supports vs 44 wall mesh points. No arbitrary reaction correction, native ETABS geometry, solver or stiffness changes.

## TDD tasks
1. **RED**: Regression for matching diaphragm tags but stale/shifted storey heights, source metadata missing, and selected auto-ledger fallback.
2. **GREEN**: Use existing `verify_storey_coverage` + `verify_storey_elevations` from `components.modal.rayleigh_ledger_audit` before automatic CSV selection, not merely tag sets; retain manual fallback and explicit non-certification message. Native consistency still open.
3. **RED**: Static/behavior regression that live Rayleigh, ledger reconstruction, ESM period selection route via *canonical Clause 5* `rayleigh_period_s`, `adopted_period_s`, `seismic_weight_kN`, and direct Rayleigh runner enforces matching source ULS/SLS.
4. **GREEN**: Replace duplicate quotient and raw live-load formulas with shared canonical functions, retain all existing metadata fields and numerical parity. Reject cross-state run at startup.
5. **VERIFY**: Targeted tests, full GitHub CI, module catalog unchanged if no new components. Record all open engineering gates and eight-runner missing E− coverage as configured evidence, without silently claiming the complete ±5% envelope.
6. **FINISH**: PR review and merge to main only with seven CI workflows green.

## Open engineering gates
- Same-source native ETABS–OpenSees 32-support pointwise ΔRz 768.045 kN not resolved.
- Rayleigh exact native COM/3D mass and PDelta stiffness/mesh parity unknown.
- Current UI log has only E+ and E0 for each polarity in both axes (8 instead of full 12), not independently verified as a GUI defect.
- Source Vs30 unknown, ESM eligibility and ULS-only model separate SLS source not provided.

**Implementation boundary:** Do not rewrite older saved results or retroactively certify calculations. Use only current code + synthetic source-evidence tests. Keep private Windows source paths and native workbooks out of GitHub.
