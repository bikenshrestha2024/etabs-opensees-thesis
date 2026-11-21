# NBC 105 __main__.py — local command-line adapter

**Source:** [components/nbc105/__main__.py](../../../../components/nbc105/__main__.py)

**Function:** `python -m components.nbc105` exposes `--list` or `--clause`, `--operation` and `--json`. It calls the isolated clause dispatcher; it does not reinterpret or duplicate NBC numerical formulas.

**Outputs:** JSON to standard output and exit code 0 for a valid reference calculation. Incorrect input produces an error to standard error and exit code 2. No upload, ETABS mutation, hidden output files or native solver execution.

**Safety and correctness:** The CLI never returns an engineering acceptance decision. It preserves `CODE_CALCULATION_ONLY_NOT_BUILDING_ACCEPTANCE`; the actual project requires native modelling, calibrated stiffness/masses and full source/solver evidence.

**Regression:** `tests/test_nbc105_module_dispatch.py`. Source standard is the user's uploaded NBC 105:2025 (second revision), Clauses 1–10.

## Local Annex A/B CLI

`python -m components.nbc105 --annex B --operation seismic_link_rotation_limit_rad --json '{"link_length_m":1.6,"mp_kNm":100,"vp_kN":100,"orientation":"horizontal","section_type":"I"}'` evaluates the scoped seismic I-link reference limit. `--annex A --operation rc_wall_detailing_minima` requires all RC wall geometry and reinforcement inputs in mm, MPa and fractional ratios. `--audit` still exits 2 while source/annex/native compliance remains incomplete. No native model is modified.
