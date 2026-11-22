# Read-only ETABS gravity restraint and rigid-end preflight

Source: [gravity_native_equivalence_preflight.py](../../../../components/validation/gravity_native_equivalence_preflight.py)

Reports source ETABS six-degree-of-freedom restraint metadata, omitted points in the primary 32-node case, and frame rigid-end-offset candidates for stiffness review. It does **not** transform 44 omitted supports into validated free nodes or establish that 1,367 rigid-end zones are equivalent to OpenSees element stiffness.

Evidence is exported separately with source identity and unresolved blockers; never modify EDB, original model JSON, or load distributions to force a reaction fit. The native ETABS API and matching analyzed model remain necessary for structural equivalence.


## 2026-11-15 — source/assembled support topology discrimination

`assess` now inspects both the original `OpenSees_Element_Connectivity.json` source object element graph and the assembled `OpenSees_Complete_Model_Data_V118.json` `frames` and `shells`. For every original support it records `source_frame_incidence`, `source_unassigned_frame_incidence`, `source_shell_incidence`, `solver_frame_incidence`, `solver_shell_incidence`, and `assembled_support_class` in the existing `SOURCE_SUPPORT_DOF_VS_PRIMARY32.csv` and JSON. If input graphs are absent, writes **CONNECTIVITY_NOT_IN_EXPORT**, never zero. A summary counts source restraints released by the 32-point diagnostic that become **SHELL_ONLY** nodes in the actual OpenSees assembled wall mesh. **This is diagnostic and does not replace any source point restraint or change solver behavior.**

Case evidence: the November 15 project has 44 source-restrained zero ETABS FZ points omitted by the 32 diagnostic. **All 44** have two sectionless source `BEAM` line segments, no connected assembled frame, and two connected assembled **wall-shell mesh cells**. This is a confirmed connectivity/presentation difference that demands ETABS **internal analysis element** reaction export (JointReact ObjectElm versus Element), original CSI wall auto-edge mesh constraints and wall-base reactions. Do not assume 44 points should be free or falsely call 76-ETABS equivalent based on equal total gravity. Source review `REVIEW_MAIN/01_GRAVITY/20261115_FULL_76_SUPPORT_REACTIONS_AND_NATIVE_DISCREPANCY.md`; solver-free unit tests `tests/test_gravity_support_topology_evidence.py`. Reference CSI Wall Auto Mesh Options https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Wall_Auto_Mesh_Options.htm and API JointReact https://docs.csiamerica.com/help-files/etabs-api-2016/html/2f434351-3116-da4d-ad8f-5e26ed6e51a2.htm.


## 2026-11-22 — physical support role and ambiguous source-node evidence

The preflight output now labels original source-point roles as `PHYSICAL_FOUNDATION_SUPPORT_USER_CONFIRMED`, `SHEAR_WALL_MESH_POINT_USER_CONFIRMED_NATIVE_EDGE_PENDING` **only if assembled wall-shell incidence and zero frame incidence corroborate it**, or `NONPRIMARY_POINT_ROLE_NEEDS_NATIVE_TOPOLOGY_REVIEW` if the assembled graph cannot establish that role. The 44 user-confirmed extra base points are **not 44 independent physical foundation supports**. The older field `released_in_primary32` describes *an OpenSees scenario restraint operation*, not the physical count of ETABS foundations. The native analytical `@LC` edge constraints and correct force recovery still need ETABS evidence.

`source_node_identity_audit` additionally reports duplicate source coordinate groups, reused solver tags and incomplete original joint coordinates. `SOURCE_NODE_IDENTITY_UNIQUE_NOT_NATIVE_VERIFIED` means this particular static check found no collisions; it is **not** a native stiffness/mesh agreement. [Source identity helper](../model/source_node_identity.py.md) · [full conversion audit](../../../../REVIEW_MAIN/02_MODEL/20261122_NATIVE_ETABS_OPENSEES_CONVERSION_AUDIT.md). `1.0D+1.0L` gravity and NBC 105:2025 §5.2 Table 5-1 seismic mass remain different purposes; this helper never changes their load factors.
