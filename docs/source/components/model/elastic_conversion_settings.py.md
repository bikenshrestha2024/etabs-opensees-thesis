# Elastic ETABS comparison settings

The [implementation](../../../../components/model/elastic_conversion_settings.py) binds ETABS frame and shell section and object modifiers to the assembled solver inputs for each configured stiffness state. It consumes native metadata extracted by the ETABS adapter and does not open ETABS. Native effective stiffness factors are the products of the property and object factors. Reviewed JSON overrides may further select explicit section or object values.

Frame areas use m², inertias m⁴, rigid offsets m and modulus kN/m². Independently verified shear areas are required for the shear-flexible formulation. A shear-flexible member with end releases or a nonzero rigid offset is rejected. The shell approximation uses the source thickness and records any transverse shear mismatch. Mass and gravity remain in their own load ledgers.

The [rebuild audit](../../../validation/20261120_GRAVITY_REACTION_REBUILD.md) documents the setup and the ten-step native OpenSees comparison. The [unit tests](../../../../tests/test_elastic_conversion_settings.py) verify settings precedence, offset limits and source modifier handling.

## 2026-11-22 — Missing native rigid end-zone source coverage

The full-run **768.045 kN** residual followed a real ETABS-elastic stiffness conversion and ten-step OpenSees analysis, **not** the older gross-shell 3041.266-kN case. See [the latest source and offset audit](../../../validation/20261122_REBUILT_ELASTIC_768KN_RESIDUAL_AUDIT.md). In the user's MESH_04 source metadata, 1200 of 1367 frame objects have nonzero ETABS rigid end offsets, all with rigid factor 1.0: 750 beam objects and 450 column objects. These belong to the same three native-shear `ElasticTimoshenkoBeam` sections in `20261121_native_gravity_uls.json`, which has no explicit `end_offsets_m` assignments.

`audit_native_end_offset_coverage(options, frames, metadata)` now reports **source-known / source-unavailable / exact-configured / unmodeled / source-mismatched** rigid-zone object counts by section and source-selected shear-flexible conflict count. `compile_settings` persists this per state under `native_end_offset_coverage`. The model-build report and gravity console show coverage warnings when native source offsets are omitted. The checker **does not apply loads, masses, offsets, fixities, modify frame stiffness or certify a native solver result**. A fully matched explicit input is still only **input-source match**, not validated ETABS frame bending/shear equivalence. The existing shear-flexible+nonzero-offset guard remains active because that joint formulation is unqualified.

New focused regression suite: `python -m pytest -q tests/test_elastic_end_offset_source_coverage.py tests/test_elastic_conversion_settings.py`. Project-native full gravity and 32-support local reaction acceptance remain outstanding.
