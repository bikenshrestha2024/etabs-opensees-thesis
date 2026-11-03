# 30 — Fluid viscous damper experimental calibration

This is a **measured-data fitting pipeline**. It is intentionally disabled when no laboratory/manufacturer time-history data are available. The existing material catalog includes example K/Cd/alpha inputs, not device-specific experimental force loops.

Prepare a CSV with exact columns time_s, displacement_m, force_kN and optionally velocity_m_s. Minimum 40 chronological observations, finite values, time starting at zero, units kN–m–s. It is better to include multiple displacement amplitudes and frequencies and independent test cycles.

Run from Spyder-compatible repository root:

    python 30_CALIBRATE_FVD_FROM_TEST.py "D:/Thesis/FVD_Test/measured.csv" --output "D:/Thesis/FVD_Test/Calibrated"

The script solves the Maxwell equation dF/dt=K*(v-sign(F)*(|F|/Cd)^(1/alpha)) with scipy.integrate.solve_ivp Radau and fits K, Cd, alpha with scipy.optimize.least_squares. It evaluates both possible load-cell force sign conventions and chooses the smaller held-out RMSE, recording the choice.

**Limitations:** The split is time-based within ONE test, not independent experimental validation. K/Cd/alpha are often non-identifiable from one frequency/amplitude; compare independent load cycles and mechanical capacities. The model fitted to actual displacement and total force may not represent connection flexibility, temperature, relief valves, air entrainment or actual high-rate device response. A fit is not authorization to use it in building NLTHA. No actual experimental CSV is supplied in the repository, so no experimental calibration is asserted or computed in this commit.

References: [ViscousDamper material](https://opensees.berkeley.edu/wiki/index.php/ViscousDamper_Material), [twoNodeLink](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/TwoNodeLink.html). FVD RC context: Korkmaz & Kircil (2026), DOI 10.3390/buildings16040711.
