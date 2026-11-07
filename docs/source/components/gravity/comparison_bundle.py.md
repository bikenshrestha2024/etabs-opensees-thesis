# Gravity evidence bundle — source guide

Source: [comparison_bundle.py](../../../../components/gravity/comparison_bundle.py)

Read-only tool. Packages actual assembled ETABS→OpenSees source-export audit files and existing OpenSees gravity-result JSON, with optional independently exported ETABS JSON. Each copied source receives a SHA256 fingerprint, including oversize files that were not included in the ZIP. Does **not** run either solver or silently assume matching loading.

Outputs: `Gravity_ETABS_OpenSees_Evidence.zip`, `Gravity_ETABS_OpenSees_Evidence/EVIDENCE_MANIFEST.json`, copied source audits, and direct numeric CSVs for OpenSees nodes, support reactions and 12-component beam local end actions (when recorded).

The GUI **Bundle gravity evidence ZIP** button supplies the source export, run folder and optional ETABS results. The ETABS JSON structure is preserved verbatim for independent normalization, without guessing field names, model correspondence or units. Missing data are explicitly inventoried. Source limits: loads, member force directions and stiffness/section properties must still be validated against the live ETABS case.

The archive export is a data capture step, NOT a pass/fail engineering equivalence test. See [gravity comparison instructions](../../../review/GRAVITY_ETABS_COMPARISON.md). Regression: [verify_gravity_comparison_bundle.py](../../../../tests/verify_gravity_comparison_bundle.py).
