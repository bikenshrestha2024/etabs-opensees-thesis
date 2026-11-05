# One ETABS source model → one limit state (2026-11-05)

For the current apple-to-apple validation, **Ultimate-labelled ETABS source EDB → ULS only; Service-labelled EDB → SLS only**. The ESM GUI defaults to the state inferred from `OpenSees_Element_Connectivity.json.source_edb` (or the source section-assignment audit). The state selector now offers ULS and SLS, not mixed Both. Selecting the opposite state is reverted with a visible warning; programmatic import and calculation independently reject it.

This protects (1) `SCALING SUMMARY` workbook selection, (2) directional first-story effective wall index, (3) Rayleigh preliminary period and its matched stiffness, (4) story-weight inputs, (5) output folder and report label, and (6) direct ETABS API comparison mapping from accidental ULS/SLS mixing. Separate models should be opened/exported independently; never reuse Ultimate stiffness, periods or response-spectrum results for a Service run.

**Illustration:**
- Source `ULTIMATE LOAD - NEPAL - 3 ... .EDB`: ESM ULS model, ULS workbook, ULS Rayleigh X/Y, ULS ETABS modal/RSA results, ULS outputs only.
- Source `SERVICE LOAD - NEPAL - 3 ... .EDB`: ESM SLS model, SLS workbook, SLS Rayleigh X/Y, SLS ETABS modal/RSA results, SLS outputs only.

Use `12_EQUIVALENT_STATIC.py` and choose the exact ULS or SLS model export. An unlabelled or doubly labelled EDB is **not** authenticated by this filename check; verify the source manually. The source-state check only gates contradictory labels; it does **not** establish that the ULS/SLS analysis stiffness, mass, geometric loads or results truly correspond. Confirm model hash, ETABS load-case definition, diaphragm geometry, cracked stiffness, self-weight and seismic mass, eigenperiod and CQC/force-scaling basis through separate ETABS/OpenSees validation. Do not present software PASS as proof of nonlinear model equivalence.

The initial filename state is a UI default where no source EDB state is available; no automatic approval is granted.

**Status:** synthetic regression in `tests/verify_esm_source_state_isolation.py`, plus existing ESM and COM mock tests. Native Windows ETABS and OpenSees validation remains outstanding. Historical Both-state logic remains present for future explicitly redesigned workflows but is not exposed by the current single-model ESM selector.
