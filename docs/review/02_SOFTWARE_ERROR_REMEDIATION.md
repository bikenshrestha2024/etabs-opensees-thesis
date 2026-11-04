# Error remediation register — November 4, 2026

This is an **actual GitHub-source and CI regression** report, not a declaration that a complex 25-storey nonlinear model has passed. Based on current main, **Soil C remains the primary matched spectral target**, eight horizontal earthquake pairs, simultaneous XY and YX, source Acc(g), additional spectral multiplier 1.0, and Path unit factor 9.80665 for kN-m-s. Do not reinterpret the 0.33–3 source matching factor as the postmatching OpenSees scale.

## Verified fixes

| Identifier | Severity | Source | Verified correction | Test |
|---|---|---|---|---|
| SW-01 | P1 | `full_record_gate.py:verify_accepted_history` | Numeric strings such as `"NaN"`, `"inf"`, `""` or arbitrary strings can no longer bypass the accepted-history finite-value check | `tests/verify_full_record_gate.py` |
| SW-02 | P1 | `full_record_gate.py:verify_numeric_accepted_row`, `building_exploratory.py:capture`, `runner_and_gui.py:record_accepted` | Detect every invalid accepted-state recorder before writing it into the response history, rather than waiting for full-record completion | `tests/verify_full_record_gate.py` + CI syntax |
| SW-03 | P1 | `full_record_gate.py:compare_time_step_results` | Refuse missing/invalid source SHA256, missing/nonpositive accepted-step evidence, non-finer comparison steps, and invalid user tolerances | `tests/verify_full_record_gate.py` |
| SW-04 | P2 | `full_record_gate.py:write_accepted_history_gate` | Create the target parent directory before emitting a JSON gate report | Static review + CI |
| SW-05 | P2 | Legacy test fixtures | Replace time-only fixtures with actual timestamp+response channels to preserve the stricter recorder contract | Successful GitHub Actions regression |

## Important limits of fixes

- These changes prevent a numerical **false-positive** acceptance of invalid recorder outputs. They do not guarantee all unqueried element states are finite or that a solver converged to the physically correct solution.
- The 2026-11-04 V168 first X-direction wall failure remains **UNRESOLVED**. Previously observed `localForce` nonfinite at solver tags 110280 and 112778 (source AREA:354 and AREA:482) is evidence *after* the solver failure, not proof of causal initiation.
- The active research material builder uses literature/conceptual RC/FSAM templates. It must not be promoted to project-calibrated THESIS_NLTHA without actual frame bar coordinates, confinement, core wall-opening layout, cyclic material/element benchmarks and documented reviewer evidence.
- Native OpenSeesPy/E-SFI material responses, OpenSees solver version compatibility and full-record XY/YX performance have **not** been executed in the GitHub Actions Python quality job.
- Your saved original and matched earthquake files remain local: GitHub only stores exact source fingerprints, declared target basis and metadata.

## Engineering next checks (in exact order)

1. Collect fresh model export, current frame/wall section schedules, wall/opening manifest, and element map. Preserve their input SHA256.
2. Rebuild and preflight the geometry; correlate failed X-only source AREA:354/482 with tags in **that exact** exported build (old solver numbers may change).
3. Perform independent FSAM wall-panel cyclic tests in the actual installed OpenSeesPy build and numerical sensitivity (mesh, timestep, material parameters).
4. Reproduce ZERO, X, Y then XY/YX probes with all sources and options fixed; record last accepted and first failed step, element/nodal responses and solver retries. Do not call a 0.005s successful probe full NLTHA.
5. Verify gravity balance, modal X/Y 90% participation, damping modes and device Rayleigh exclusion, and NBC 105 §9.3.2.2 matching interval for latest T1/Tn90.
6. Recover real original SeismoMatch scale logs; resolve Gorkha 322.94s versus original 120s and the Loma Prieta 0.005s component difference.
7. Only with successful source-calibrated frames/core/FVD/BRB and **full-record** ULS/SLS XY/YX outputs may M0–M6 results be compared.

## Run available tests on Windows (Spyder/conda-forge Python 3.12)

```powershell
git pull origin main
python tests/verify_full_record_gate.py
python tests/verify_wall_geometry_preflight.py
python tests/verify_wall_openings.py
python tests/verify_project_wall_material_gate.py
python tests/verify_failure_evidence.py
python tests/verify_v168_diagnostics.py
```

**Statuses:** Python regression `PASS` is a statement about the tested software contracts. OpenSees native solver/calibration is `NOT RUN`. NBC project design compliance is `NOT ESTABLISHED`.

Sources: [NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf), [OpenSees E-SFI-MVLEM-3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html), [OpenSees UniformExcitation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html), [PEER 2015/12](https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf).
