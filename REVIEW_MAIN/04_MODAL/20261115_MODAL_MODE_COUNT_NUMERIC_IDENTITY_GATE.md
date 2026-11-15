# 2026-11-15 modal / MRSM eigenmode count identity gate

**Baseline:** `d37685aaf0f2e74e4e4113436260805ba9fb1670`  
**Scope:** `components/shared/eigen_solver.py`, `components/modal/analysis.py`, `components/response_spectrum/model_analysis.py`.  
**Status:** CONFIRMED SOURCE-LEVEL NUMERICAL INPUT TRUNCATION; native model and code compliance NOT VERIFIED.

## Observed source defect

Both the public modal audit `run_nbc105_modal_audit` and the shared OpenSees `solve_eigen` originally called `int(nmodes)` or `int(modes)`, silently accepting `2.9 -> 2` and `True -> 1`. The MRSM caller pre-truncated its configured `nmodes` with `int(config.get('nmodes', 40))`, so a downstream validation alone would not have repaired the full path. The optional manually selected fundamental mode similarly truncated fractional identifiers. These conversions could change the number of eigenpairs and which adopted-modal period is reported while obscuring the invalid input.

**Engineering concern:** the number and identity of modes govern the NBC 105:2025 §7.3 participating-mass and spectrum-response evidence, but a software check does not establish code compliance or adequate mass participation.

## Coordinated repair

Add one reusable `validated_mode_count` to the existing shared eigensolver, requiring positive exact integer (plain decimal string, integer, or mathematically integral real), explicitly rejecting booleans and nonfinite/fractional values. Validate public modal count and manually selected X/Y fundamental mode before starting eigenanalysis. MRSM checks the count before model assembly and passes the exact validated integer; shared `solve_eigen` also checks direct independent callers. Preserve valid existing 40-mode and 20-mode requests. Reject nonfinite/negative modal-frequency threshold and boolean participation target; these are scalar input gates, not changes to mass, EI, damping or OpenSees solver behavior.

## Regression and engineering acceptance

- Deterministic headless `tests/test_modal_mode_count_contract.py` covers positive/fractional/boolean/nonfinite/large integer identity and caller integration.
- Existing `tests/verify_modal_solver_and_paths.py` retains native-to-PythonSparse solver fallback contract; optional SciPy/native run separately.
- CI: `.github/workflows/integrated-repository-audit.yml` runs the new tests.
- **NOT DONE:** native 25-storey ULS/SLS modal solver, ETABS mode-shape matching, mass/stiffness reconciliation, 33 Hz high-frequency follow-up, 90% X/Y participation acceptance, response-spectrum CQC and NBC §7.5 scaling.
- Preserve source ETABS EDB/Excel and all historical outputs. Do not reinterpret stored results after this change; regenerate case-specific modal evidence with matching source SHA.

This confirms one source input-contract problem across three callers. It is not full semantic review of all active source modules.
