# Read-only ETABS gravity restraint and rigid-end preflight

Source: [gravity_native_equivalence_preflight.py](../../../../components/validation/gravity_native_equivalence_preflight.py)

Reports source ETABS six-degree-of-freedom restraint metadata, omitted points in the primary 32-node case, and frame rigid-end-offset candidates for stiffness review. It does **not** transform 44 omitted supports into validated free nodes or establish that 1,367 rigid-end zones are equivalent to OpenSees element stiffness.

Evidence is exported separately with source identity and unresolved blockers; never modify EDB, original model JSON, or load distributions to force a reaction fit. The native ETABS API and matching analyzed model remain necessary for structural equivalence.
