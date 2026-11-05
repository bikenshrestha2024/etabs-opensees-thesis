# Source guide — components/validation/torsion_check.py

**Role:** Independent, pure-Python NBC 105:2025 §§5.4.2.1–5.4.2.2 plan irregularity screen on the **same-floor opposite-end horizontal displacement** values for a centre-of-mass lateral loading case.

**Units:** end_a_m and end_b_m [m, signed displacement]; output ratio dimensionless. Thresholds strict `>1.5` and `>2.5`. Ratio defined on magnitudes for compatible signed increments; avoid mixing total preloaded and seismic-only values or different modes/cases.

**Dependencies:** Python standard library only. `check_floor_end_torsion` is pure; `check_torsional_irregularity` checks ULS/SLS case, direction and storey identity and rejects duplicates. Its status flags are **not** a structural design certificate or a substitute for physical displacement source mapping.

**Error handling:** Nonfinite displacement rejected, missing physical pairing/CM-load evidence → NOT EVALUATED, both zero → NOT EVALUATED, near-zero one end → UNBOUNDED and design acceptance blocked. Extreme torsion >2.5 blocks acceptance, but diagnostic run results are preserved.

**Source:** [Official NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf) printed p.34, Figure 5-3 and §§5.4.2.1–5.4.2.2. **Not** a `max/mean` formula.

**Tests:** `tests/verify_nbc105_torsion_check.py`. No native ETABS/OpenSees integration was run; optional standalone CLI `torsion_check.py` reads user-mapped CSV and writes a review CSV without changing model files. See root `validation_checklist.md`.
