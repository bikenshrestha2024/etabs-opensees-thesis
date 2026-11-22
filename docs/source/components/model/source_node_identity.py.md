# ETABS source node identity and coincident-point ambiguity

[Implementation](../../../../components/model/source_node_identity.py) · [Unit tests](../../../../tests/test_source_node_identity_conversion.py)

This module protects the **physical identity** of distinct ETABS source point objects when the OpenSees wall/slab mesher creates nodes using an XYZ lookup (rounding to eight decimals). Previously `_mesh_areas` created a mapping with a dict comprehension: when two distinct source tags shared the same XYZ, **the later tag silently replaced the earlier one**. Consequently a shell corner or an interior frame cut could be attached to the wrong original node, bypassing the source's separate joint, release, interface or multipoint-constraint meaning.

`unique_coordinate_lookup(source_nodes)` performs the same coordinate matching when source nodes are unique. If it encounters different source tags with the same rounded XYZ, it fails early with a traceable error. It **does not silently merge tags**, constrain/ground-fix nodes, add `equalDOF` or otherwise guess the ETABS physical relationship. Source geometry with intentionally coincident but independent nodes needs explicit native joint connectivity/constraint evidence and a reviewed conversion procedure before the source can be meshed safely.

`audit_node_map_identity(topology["node_map"])` is read-only and reports source/solver point coordinates, coordinate collisions, reused solver tags and incomplete source coordinate evidence. The [native gravity equivalence preflight](../validation/gravity_native_equivalence_preflight.py.md) now includes `source_node_identity_audit`. A clean unique-tag audit is **not** proof of equivalent native analytical mesh/auto-edge constraints or source point reaction attribution.

## Case and numerical scope

- 32 physical foundation support joints + 44 shear-wall mesh points remain separate classes. Coincident source points are **not** evidence for adding physical foundation supports.
- Full gravity comparison remains **100% dead + 100% live** (`GRAVITY_1.0D_1.0L`). Seismic mass is separate, governed by NBC 105:2025 §5.2 Table 5-1. The helper does not change load factors.
- The previously rebuilt ETABS-elastic 32-support maximum gravity reaction error remains **768.045 kN**, **not solved or re-evaluated** by this change.
- No private ETABS EDB or source full-model analysis was run to establish whether the specific current study export has coincident distinct tags.
- Diagnostic status: `SOURCE_NODE_IDENTITY_UNIQUE_NOT_NATIVE_VERIFIED`, `COINCIDENT_DISTINCT_SOURCE_NODES_REQUIRE_NATIVE_REVIEW`, `NONUNIQUE_SOURCE_TO_SOLVER_TAGS_REQUIRE_NATIVE_REVIEW`, `SOURCE_NODE_COORDINATES_INCOMPLETE` or `SOURCE_NODE_MAP_UNAVAILABLE`.

Use `python -m unittest -v tests.test_source_node_identity_conversion` locally for synthetic source/assembly verification. Native ETABS/OpenSees 3D joint connectivity, source node releases/MPCs and same-model reaction comparison must be checked independently.
