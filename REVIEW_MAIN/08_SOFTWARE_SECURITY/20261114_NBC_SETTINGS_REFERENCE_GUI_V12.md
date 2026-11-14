# NBC 105:2025 analysis settings / V135 output path review — 2026-11-14

**Status:** GUI/reference and report-location correction implemented; Windows-native section/force/deflection verification **NOT COMPLETE**.

**Evidence reviewed:** User-supplied screenshots: the all-in-one "NBC 105:2025 Load Combinations, Stiffness Modifiers, Mass Source" window and a V135 design-check report located under the historical `OpenSees_Analysis_Results/Design_Checks_V135` (local time around 16:03, 2026-11-14); user-supplied settings audit JSON; project-adopted formula/assumption text. Official NBC 105:2025 DUDBC PDF pages 19–20 (§§3.4–3.6), pages 28–30 (§§5.1–5.2) independently checked. Also inspected current source `application.py`, `analysis_basis.py`, `legacy_code_basis.py`, `design_checks.py` and `settings_audit.py`.

## Concrete changes

- Replaced the giant 5-column mixed-semantics settings Treeview with a **six-tab** read-only reference/existing-model viewer: project adoption, NBC code, mass-source/pattern matching, current settings audit, mechanics/solver and runtime/output diagnostics.
- The **compulsory** conventional slab `0.25/0.35 Ig` and signed P-Delta `1.2 DL+0.5 IL±1.5 EL/WL` are labelled IS 16700 project adoptions (not NBC 105 provisions), dynamically sourced from `analysis_basis`; the reader checks selected export's saved slab factors for discrepancies but never declares they are physically applied.
- NBC Table 3-1 values and §3.6 loads are separated from mass fractions, IS supplements, solver algorithms and numerical mechanics. Neither flat-slab factor nor nonlinear fiber cracking is inferred for conventional RC slab.
- Selected export config/model SHA256 and actual loaded code path are displayed, making a stale local runtime easier to diagnose.
- V135's `run` selects the owning export root even when the user browses into a nested result stage. Its GUI explicitly shows `__file__`, new `09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135` output and historical-location diagnostic rather than implying all historical files have been moved.
- An explicit user action exports a timestamped local, common-style JSON+XLSX reference under `09_SOFTWARE_DIAGNOSTICS/ANALYSIS_SETTINGS`; no source EDB/Excel modified.

## Interpretation of legacy V135 screenshot

Screenshot alone cannot distinguish a **historical** legacy report from a **currently running stale launcher**. The new read-only diagnostic compares actual presence/timestamps of canonical and legacy V135 report JSONs, and labels the evidence rather than deleting/moving files. A freshly written legacy report is a strong reason to inspect the active launcher and source module path. Do not duplicate the entire runtime or conceal old file identities.

## Non-negotiable native QA still open

1. Run V135 in an updated Windows checkout; confirm the explicit output path under `09_SOFTWARE_DIAGNOSTICS`, preserve legacy edited CSV input and verify the active Python file paths.
2. Verify generated ULS and SLS conventional slab shell bending section uses project-adopted `0.25/0.35 Ig`, retains membrane/mass thickness/source gravity load, and matches relevant ETABS modifiers.
3. Verify X/Y empirical and Rayleigh period vs original Excel `A_w` (including the user's exact opening method), spectrum `Cd(T)`, distribution exponent and force-only MRSM scaling.
4. Verify mass source, asymmetric floor rotational inertia and 32/76/97 foundation restraint comparison with independent native solver data.
5. Verify signed initial P-Delta native analysis and correct state transfer; do not label an IS project gate as NBC §3.6.
6. Exercise Tk window search, scrolling, detail, buttons and JSON/XLSX output on the user's Windows machine. Review files locally; do not publish private project paths.

**This is a presentation, source-data and report-path fix, not a numerical code equivalence certificate.**
