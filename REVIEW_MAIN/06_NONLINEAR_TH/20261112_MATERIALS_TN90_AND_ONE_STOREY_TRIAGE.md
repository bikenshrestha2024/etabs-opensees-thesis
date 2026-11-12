# 2026-11-12 NLTHA case review — missing production material file, short transient, 1st-storey E-SFI probe

**Status: NUMERICAL RESEARCH PATH IMPROVED; FULL BUILDING NLTHA PHYSICAL VALIDATION OPEN.**
The source 25-storey ETABS EDB, original reference Excel, previously saved 0.1-second run and all output archive data are NOT overwritten by these commits.

## Verified user-reported observations

- Isolated nonlinear building exploratory **ULS YX** with Hector Mine record: 0.1000 s achieved of 45.29 s complete record, 21 finite accepted history rows, minimum/maximum dt 0.005 s, local solve output status `COMPLETED_TRUNCATED_TRIAL`, `energy_balance_status=PASS` for this diagnostic, no first-step divergence. Peak roof Ux=0.000117685 m, Uy=0.000111195 m; max story drift X=3.72178e-6, Y=4.22043e-6. This is 0.22% of full-record physical time; observed maxima are NOT full-run demands.
- Initial 20 nonlinear eigenperiods listed: first three 2.211471682 / 1.540590680 / 1.023394633 seconds. The list has no independent cumulative modal mass thresholds and therefore does not identify directional Tn90. ULS/SLS and selected material/nonlinear stiffness affect modal response.
- Selected `ZERO damping (diagnostic)` yields all inspected `initial_damping_ratios=0.0`. It is NOT 2.5% / 5% physical model damping and not a reason to set design damping to zero.
- `variant_id=UNASSIGNED`: no approved M0-M6 structural scenario identity has been established by the material trial.
- Readiness window showed `nonlinear_parameters_reviewed=False`, empty `nonlinear_materials_file` and zero `nonlinear_wall_fsam_tags` **in the exported production configuration**. These are not contradictory to the exploratory `Research_Material_Assignment_V161.json`, because that second path makes a separate isolated model and creates PEER-based dynamic materials on the fly.
- Main `NLTHA` runner correctly rejects the readiness *template* and requires model-bound evidence. Approving a checklist without project-specific material, rebar, FSAM and geometry evidence would not establish calibration.

## Engineering judgment

**Production materials:** not missing from the entire program, but **not provided as independently reviewed project-specific assignments** in the production nonlinear builder. Never set `nonlinear_parameters_reviewed=True` or auto-approve the readiness JSON based only on an exploratory smoke test. The isolated drafting command prepares a research copy without changing project identity. The historical wall FSAM ratios based on two curtains of 20 mm at 200 mm are unverified layout assumptions; do not report them as EDB rebar extraction.

**One literature paper:** use `PEER_2015_12_SINGLE_SOURCE` for specimen concrete, web reinforcement steel and transferred frame material strengths, with `cR1=18.5/20=0.925` and `cR2=0.0015`. The alternative `PUBLISHED_REFERENCE` was deliberately a MIXED-source research model; it is not the requested one-paper baseline. Other modeled pieces still require distinct references: E-SFI-MVLEM-3D element mechanics (2023), FSAM patch alpha/nu and rho, actual project reinforcement/confinement, steel brace Fy/b/E, dampers and BRBs. Do not fabricate one-paper numerical values for parameters the PEER report never tabulated.

**First-storey test:** a physically exact whole first floor cannot be obtained by simply truncating a 25-storey high-rise; the missing 24-storey gravity forces, axial effects, shear/moment coupling, boundary conditions and diaphragm constraints fundamentally change the mechanics. A conservative new diagnostic therefore selects **one real first-storey wall QUAD**, and tests its E-SFI/FSAM implementation with fixed lower edge and an artificial low-amplitude static load. This is a material/element implementation smoke test, not a whole-floor dynamic result. The next physically meaningful step is a verified one-storey **subassembly** with source-matched roof/interface gravity, columns, beams, walls, coupling and diaphragm boundary transfer.

**Periods:** separate (a) §5.1.1 equivalent static Rayleigh period, (b) §5.1.3 adopted ESM design period, (c) actual nonlinear initial-tangent eigenperiods, and (d) the period of the first inspected mode for which **90% directional effective mass** has genuinely accumulated. The last inspected 20th mode is not Tn90 by definition. A new `Nonlinear_Initial_Modal_Audit.json` uses actual OpenSees modalProperties and can report Tn90X/Y **null** when criterion not met. Do not substitute the 2.211-second first eigenperiod for the existing ESM/Rayleigh calculation.

## Implementation

| Path | Change | Evidence |
|---|---|---|
| `components/nonlinear_time_history/material_draft.py` | Preserve same PEER ConcreteCM and SteelMPF transition; no source editing, unapproved draft | `tests/verify_peer_material_draft_isolation.py` |
| `components/ui/building_exploratory_gui.py` | PEER single-source default, material provenance note, one-QUAD launch button | GUI Windows native test needed |
| `components/model/readiness_gui.py` | Separate production missing assignment from exploratory card; add isolated research draft action | GUI Windows native test needed |
| `components/nonlinear_time_history/one_storey_wall_probe.py` | Source-hashed first-storey wall panel; separate artificial static probe; failure evidence | `tests/verify_one_storey_wall_probe.py`; native E-SFI solver test pending |
| `components/nonlinear_time_history/building_exploratory.py` | Save nonlinear initial eigenperiod/cumulative modal mass source and Tn90X/Y audit | `tests/verify_initial_nonlinear_period_audit.py` |
| `components/inputs/analysis_autofill.py` | Fail closed on mismatched elastic source/model numeric fingerprint for auto Tn/damping calibration | Modal source rerun on Windows pending |

## References

1. **Kristijan Kolozvari, Kutay Orakcal and John W. Wallace (2015)**, *Shear-Flexure Interaction Modeling for Reinforced Concrete Structural Walls and Columns under Reversed Cyclic Loading*, **PEER Report 2015/12**, Pacific Earthquake Engineering Research Center, Berkeley, December. Appendix B.3, printed pp. 90–91. DOI: **none verified; do not invent**. https://peer.berkeley.edu/publications/2015-12 . Full report: https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf .
2. **Kristijan Kolozvari, Carlos N. López and Leonardo M. Massone (2023)**, *Efficient Three-dimensional Shear-flexure Interaction Model for Reinforced Concrete Walls*, **Engineering Structures** 294, 116700, DOI: **10.1016/j.engstruct.2023.116700**, https://doi.org/10.1016/j.engstruct.2023.116700 . The command and required 24-DOF model: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html .
3. **Kolozvari and Wallace (2016)**, *Practical Nonlinear Modeling of Reinforced Concrete Structural Walls*, **Journal of Structural Engineering** 142(12), DOI **10.1061/(ASCE)ST.1943-541X.0001492**. Contextual modeling limitations only; numerical baseline NOT taken from this paper.
4. **NBC 105:2025** §7.3 modal effective mass and §8.1.1 nonlinear analysis/damping requirements. Use project-specific numerical and code approval gates.

## Next empirical proof, not done automatically

Use Windows OpenSeesPy with the E-SFI fork/binary to execute the new one-QUAD probe; upload `One_Storey_Wall_Probe_Inputs.json` and `One_Storey_Wall_Probe_Result.json`. Once stable, compare a complete PEER reference specimen with original cyclic experimental data using consistent constituent parameters and actual specimen dimensions; calibrate only if error and curves justify it. Then implement a true 1-storey frame+wall subassembly with cut interface loads and eventually the whole 25-storey model with XY/YX motions, real materials and complete 45.29-second histories. Keep sensitivity as one parameter at a time, source baseline unmodified, paper-unknown candidates labeled analyst choices.
