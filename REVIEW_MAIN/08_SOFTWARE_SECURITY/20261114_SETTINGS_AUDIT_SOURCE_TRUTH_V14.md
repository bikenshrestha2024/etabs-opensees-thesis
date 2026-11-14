# Settings audit source-truth correction V14 — 2026-11-14

**Source-level finding:** `components/validation/settings_audit.py::audit` always returned `Production ShellMITC4 uses source gross in-plane stiffness` as the value of **Elastic wall effective stiffness**. The audit did not load and inspect the actual generated shell section assignments, ETABS wall stiffness modifiers or material tangent model before making that statement. The value could therefore be stale or inaccurate. This matters because the settings audit appears in V135 `Open items` and in the NBC settings panel's **Current model audit** tab.

**Correction:** The existing audit now reports `CURRENT GENERATED WALL EI NOT EXTRACTED BY THIS AUDIT`, status `ACTION REQUIRED` and explicit NBC 105:2025 Table 3-1 cracked/uncracked wall reference factors (0.50/0.70 and 0.80/0.90 for ULS/SLS). This is a documentation/evidence correction, **not** a change in physical shell stiffness or a claim that gross stiffness is appropriate.

**Conventional RC slab:** Compare *recorded config* `slab_bending_factor` and `slab_bending_factor_sls` against the separately project-adopted IS 16700:2023 Table 5 values `0.25/0.35`. Distinguish `CONFIG FACTOR DISAGREES WITH PROJECT ADOPTION`, `CONFIG VALUE MISSING / INVALID` and `VERIFY GENERATED ETABS AND OPENSEES SHELL SECTION`. Even matching config numbers do not prove a generated model's native shell plate/bending modifier, mass or diaphragm representation.

**Robustness:** Invalid JSON, `null`, NaN, absent configuration or missing source text cannot crash the read-only settings audit. The GUI warns when slab configuration values are non-finite.

**Tests:** `python -m unittest discover -s tests -p "test_settings_audit_source_truth_v14.py" -v` exercises absent config, matching/mismatching slab values, NaN/null and invalid JSON. All original EDB, authoritative project Excel, historical outputs and native numerical assignment scripts remain unchanged.

**Outstanding engineering gates:** Actual wall and slab in-plane/plate stiffness, asymmetric floor mass inertia, 32/76/97 reaction comparison, MESH_04/08/16 gravity transfer, signed P-Delta and fully calibrated NLTHA. This reference audit cannot close any of those gates.
