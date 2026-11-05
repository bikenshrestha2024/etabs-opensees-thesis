# verify_esm_output_safety.py — independently scoped software regression

This script runs seven synthetic, deterministic, solver-free regression checks for the ESM GUI output-path and limit-state evidence metadata at commit after 2026-11-05.

**Inputs:** Temporary Python and non-Python synthetic model paths, empty path cases and artificial ULS/SLS Rayleigh periods (seconds). No private ETABS EDB or real spectrum inputs.

**Expected behavior:** `validated_pdelta_sidecar_path` returns no legacy sidecar for an empty/unknown/non-.py model path; an explicitly existing .py model retains the original sidecar filename and directory. `state_rayleigh_provenance` emits state-specific X/Y values and preserves missing evidence as missing rather than copying another limit state.

**Source and engineering limitations:** `components/equivalent_static/calculation_and_gui.py`; NBC 105:2025 §5.1. These tests protect provenance and output placement only. They do not verify actual stiffness, mass, structural wall effective area, or the safety of an external model's output folder. User must review which model script is selected and independent ULS/SLS Rayleigh analyses.

**Command:** `python tests/verify_esm_output_safety.py` from project root; CI should also execute. Failed tests must block merging.
