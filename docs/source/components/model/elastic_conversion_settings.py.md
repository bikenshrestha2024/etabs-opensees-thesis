# Elastic ETABS comparison settings

The [implementation](../../../../components/model/elastic_conversion_settings.py) binds ETABS frame and shell section and object modifiers to the assembled solver inputs for each configured stiffness state. It consumes native metadata extracted by the ETABS adapter and does not open ETABS. Native effective stiffness factors are the products of the property and object factors. Reviewed JSON overrides may further select explicit section or object values.

Frame areas use m², inertias m⁴, rigid offsets m and modulus kN/m². Independently verified shear areas are required for the shear-flexible formulation. A shear-flexible member with end releases or a nonzero rigid offset is rejected. The shell approximation uses the source thickness and records any transverse shear mismatch. Mass and gravity remain in their own load ledgers.

The [rebuild audit](../../../validation/20261120_GRAVITY_REACTION_REBUILD.md) documents the setup and the ten-step native OpenSees comparison. The [unit tests](../../../../tests/test_elastic_conversion_settings.py) verify settings precedence, offset limits and source modifier handling.
