# MRSM numerical evidence validation V10 — 2026-11-14

**Issue (P0, software evidence):** The initial MRSM six-case gate checked that `MRSM_Results_V132.json` existed, held six direction/eccentricity case keys, had a nonempty list of storeys and recorded a 64-character model identifier. It **did not verify whether saved story drift was finite, nonnegative or present**, and a string of any 64 characters was accepted as a purported model SHA. The Python JSON reader accepts non-standard NaN tokens by default; a truncated or nonfinite solver export could therefore be labelled `COMPLETE_SAVED_CASES_ONLY`.

**Correction:** `validate_mrsm_case_output` now checks that the six-case container and each result are dictionaries, every saved story is an object with a present, numeric, finite, nonnegative design drift, and any provided height, displacement, shear and elastic drift is finite. Source model SHA is required to be exactly 64 hexadecimal characters. Any invalid case raises ValueError, causing the caller to mark its run `INCOMPLETE`, rather than `COMPLETED_SOLVER_ONLY`.

**Verification:** `tests/test_mrsm_canonical_output_v4.py` now includes NaN, missing drift and invalid hexadecimal model-ID cases. These unit tests use synthetic files and do not validate a native OpenSees eigen/CQC solution.

**Native acceptance still open:** Complete ULS and SLS MRSM must independently match selected ETABS source model, wall stiffness, mass, support restraints and signed eccentricity. Confirm absolute/base shear force scaling, interstorey displacement not multiplied by force-only scaling, actual 6-DOF support reactions and model cache state. Source EDB, original Excel workbook and historical responses are unchanged.
