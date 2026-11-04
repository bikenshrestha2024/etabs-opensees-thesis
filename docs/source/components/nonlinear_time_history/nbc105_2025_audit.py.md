# nbc105_2025_audit.py — official NBC NLTHA metadata checks

**Source:** [nbc105_2025_audit.py](../../../../components/nonlinear_time_history/nbc105_2025_audit.py).

**Purpose:** Enforce user-supplied period/scale/record orientation consistency with NBC 105:2025, §9.3.2, without fabricating a spectral match, native solver run or project-level approval.

**Inputs:** reviewed T1 in both plan axes, Tn90 periods from cumulative translational participation, ULS R_mu/Omega_u, independently fitted paired scale factors, shared actual scale, record digitization dt, integration dt, source evidence SHA256, seismological record review and XY/YX.

**Outputs:** structured JSON numeric/suite metadata screen (never `DESIGN PASS`). A seven-pair suite requires an explicit code interpretation rather than blindly choosing maximum/average.

**Validation:** `tests/verify_nbc105_2025_nltha.py`, and manual verification of spectrum target, periods, gravity, P-Delta, inherently torsional response, wall hysteresis and accepted full histories.

**Code clauses:** §9.3.2.1–9.3.2.4, §9.3.3 and §5.5.3; official source https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf.

[Research review](../../../00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md)
