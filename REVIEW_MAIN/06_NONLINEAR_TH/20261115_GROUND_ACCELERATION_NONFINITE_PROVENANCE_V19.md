# V19 NLTHA ground-acceleration reconstruction integrity — 2026-11-15

**Status:** SOURCE_AND_REGRESSION_PATCH_COMMITTED; NATIVE_SOLVER_EQUIVALENCE_NOT_VERIFIED.
**Scope actually inspected:** `components/nonlinear_time_history/ground_acceleration.py`, `tests/verify_nltha_ground_acceleration.py`, `components/nonlinear_time_history/full_record_gate.py`, `components/nonlinear_time_history/nbc105_2025_audit.py`, `components/nonlinear_time_history/energy_balance.py`, `components/response_spectrum/nbc_pair_spectrum_audit.py`, `components/response_spectrum/site_spectrum_and_scaling.py`, `components/gravity/source_load_reconciliation.py`, `components/gravity/validation_scorecard.py`, `components/shared/gravity_transient_handoff.py`. The last eight were source scans and function/guard inspections, **not** exhaustive semantic reviews.

## Confirmed V19-01: nonfinite support acceleration could reach relative-to-absolute floor response

Before the correction, `_sample_path` returned the interpolation of sampled ordinates without rejecting NaN or Infinity in the two relevant samples. It then multiplied by the `g`-to-m/s² and additional spectral factors. `relative_to_absolute_floor_acceleration` added floor-relative and ground values without a finite-result check. In each path nonfinite values could be emitted as if physically meaningful.

**Corrective implementation**
- Check bracketing Path ordinates at each accessed time in O(1), preserving linear interpolation and the existing zero-beyond-record convention.
- Refuse nonfinite relative and ground input acceleration values.
- Refuse arithmetic overflow after conversion/scaling and after absolute-acceleration reconstruction.
- Preserve the current XY/YX orientation and X/Y/ZERO diagnostic excitation semantics, positive spectral factor validation and one-time acceleration-unit conversion.
- No source accelerogram, full record, ETABS or OpenSees model data was changed.

**Tests:** `tests/verify_nltha_ground_acceleration.py` now exercises NaN, +Infinity, -Infinity and finite-input arithmetic overflow. Existing tests check XY/YX swapping, interpolated values, unit conversion, record-end behavior, zero probe and the relative/absolute distinction.

**Limitations:** This is a numerical rejection guard, not proof that OpenSees' actual Path interpolation, record origin, source timestamps, dt, units or native recorder output match the Python helper. The helper screens only accessed ordinates: the full source waveform must be checked independently during import. Does not address multi-support excitation or vertical DOF 3.

## Other open NLTHA model-physics questions

- The first-step X-wall element nonfinite local-force failure still requires native element-level confinement/reinforcement/constitutive checks and a fresh-domain transient comparison.
- The current physical model must be checked for true source sections, wall opening discretization, beam/column hinge or fiber assignment, device units and model provenance.
- A full-record accepted-state screen is not calibrated material response; static P-Delta initial cases and source-matched XY/YX time histories require independent evidence.
- `full_record_gate.py` evaluates time and numerical completeness, but its local JSON write path is not a substitute for the central case-run package; integrate writer and reader paths only after Windows regression.
- New canonical run outputs should own `00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP` under `07_NONLINEAR_TIME_HISTORY/RUNS/<state>/<case>/<run-id>`. Existing legacy producers are not automatically migrated.

## Reproduction / acceptance evidence

```powershell
python tests/verify_nltha_ground_acceleration.py
python tests/verify_full_record_gate.py
python tests/verify_nbc105_2025_nltha.py
python -m unittest tests.test_unified_output_contract -v
```

Check GitHub Actions **NLTHA Python quality checks** for the commit containing the new test; the first commit in this batch has not been claimed as a completed native Windows run. Then compare ground input and absolute/relative floor acceleration with time-matched OpenSees recorder traces on the real source case; keep the original acceleration pair SHA and converted m/s² units in the case manifest.

**Engineering status:** NOT_VERIFIED — original models and source records remain untouched.
