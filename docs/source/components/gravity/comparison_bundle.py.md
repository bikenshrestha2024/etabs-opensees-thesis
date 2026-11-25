# Gravity evidence bundle — source guide

Source: [comparison_bundle.py](../../../../components/gravity/comparison_bundle.py)

Read-only tool. Packages actual assembled ETABS→OpenSees source-export audit files and existing OpenSees gravity-result JSON, with optional independently exported ETABS JSON. Each copied source receives a SHA256 fingerprint, including oversize files that were not included in the ZIP. Does **not** run either solver or silently assume matching loading.

Outputs: `Gravity_ETABS_OpenSees_Evidence.zip`, `Gravity_ETABS_OpenSees_Evidence/EVIDENCE_MANIFEST.json`, copied source audits, and direct numeric CSVs for OpenSees nodes, support reactions and 12-component beam local end actions (when recorded).

The GUI **Bundle gravity evidence ZIP** button supplies the source export, run folder and optional ETABS results. The ETABS JSON structure is preserved verbatim for independent normalization, without guessing field names, model correspondence or units. Missing data are explicitly inventoried. Source limits: loads, member force directions and stiffness/section properties must still be validated against the live ETABS case.

The archive export is a data capture step, NOT a pass/fail engineering equivalence test. See [gravity comparison instructions](../../../review/GRAVITY_ETABS_COMPARISON.md). Regression: [verify_gravity_comparison_bundle.py](../../../../tests/verify_gravity_comparison_bundle.py).
# Workbook evidence and archive layout

The Gravity GUI publishes the expanded evidence under `06_REVIEW/Gravity_Evidence` and its versioned archive under `07_EXPORT_ZIP/Gravity_Evidence_Upload`. The publisher verifies the staged ZIP CRC before publication. The organized archive is versioned and reads the selected saved case and its digest-matched comparison when available. Current slab formula manifests bind model data, config and workbook digests. Older manifests can still be included as `legacy_config_bound` evidence.

The primary 32-support scorecard accepts workbook-derived vertical reaction screening when the original workbook SHA and every saved OpenSees reaction and ETABS point mapping agree. An unsolved 76-support sensitivity case is optional for the primary package. Source fixity, local reaction differences and overall ETABS equivalence remain independent checks.
