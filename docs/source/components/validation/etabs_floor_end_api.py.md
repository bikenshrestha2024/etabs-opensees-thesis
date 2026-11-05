# ETABS signed joint source guide

Module: `components/validation/etabs_floor_end_api.py`.

Inputs: existing loaded ETABS EDB path, independently reviewed ETABS perimeter node IDs, ULS or SLS, a centered-mass static load case and one explicitly chosen result step. Output: signed U1/U2 displacements in metres, with identical case and step for every point. The module uses `Results.JointDispl`, restores prior ETABS output selection and display units, and does not save or modify the EDB.

Numerical source and physical caveats: a user-verified centered-CM flag documents an assumption; it does not establish that the ETABS load case actually applies through the mass centre. Cross-case, missing, duplicate and spectrum-envelope result values must not be treated as comparable. The historical ETABS 2016 API signature is used; native Windows ETABS v23 verification remains NOT RUN. Model and result comparisons must use corresponding OpenSees nodes, stiffness state and load case. The source file remains private and read-only.

Tests: `tests/verify_etabs_floor_end_api.py`. CLI: `extract_torsion_data.py`. Further usage: `docs/validation/floor_end_extraction/README.md`.
