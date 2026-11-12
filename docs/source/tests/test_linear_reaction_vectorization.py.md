# Source guide: tests/test_linear_reaction_vectorization.py

**Purpose:** deterministic no-native-OpenSees regression tests for the optional vector reaction API in `components/shared/response_recorders.py`.

**Inputs:** in-memory fake six-DOF support reactions and fake OpenSees API `reactions()` and `nodeReaction(node, dof=None)`. Force values interpreted as kN and support moments as kN·m. No ETABS source files, ground motions or material properties are read.

**Checks:** six-component vector resultants numerically match baseline six scalar nodeReaction calls; reaction and base-shear sign conventions remain unchanged; invalid short reaction vectors and empty support selections fail explicitly. Each invocation must call OpenSees reactions() before querying nodal resultants.

**Side effects:** none except unit test stdout. The tests do not perform time integration or reconstruct a 37,776-equation OpenSees system.

**Run:** `python -m unittest discover -s tests -p 'test_linear_reaction_vectorization.py' -v`

**Engineering gate:** passing fake API tests is insufficient to assert native OpenSees performance, wall model equivalence, or full-record completion. Run identical XY/YX paired traces (baseline, optimized) and compare every output at every accepted sample before changing production defaults.

**External API reference:** https://openseespydoc.readthedocs.io/en/stable/src/nodeReaction.html (nodeReaction(nodeTag) returns all DOFs if dof omitted; requires preceding reactions() call).

**Provenance:** added 2026-11-12 based on user-supplied Kobe LTH partial-batch evidence and active `components/shared/response_recorders.py`. No change to physical model assumptions.
