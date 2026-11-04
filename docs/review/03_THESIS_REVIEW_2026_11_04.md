# Thesis engineering review: evidence and workflow

Reviewed baseline: `66c5c971ea297dc9d7fb0499b871a6204297913d` (GitHub main). This is a targeted source review, not a line-by-line semantic review of the repository. The automated inventory parsed 160 active Python modules; parsing does not establish physical correctness. See `00_ACTIVE_CODE_ENGINEERING_REVIEW.md` for the earlier reviewed modules and open issues.

## What the analyses establish

The supplied modal log reports separate ULS and SLS runs, with horizontal cumulative modal mass percentages exceeding 90% in both directions. This is a modal coverage result for the identified model, not evidence that member strength, wall material, or nonlinear time histories are validated. Compare ETABS and OpenSees model identity, mass, stiffness, restraints and P-Delta state before interpreting differences.

Gravity reaction equilibrium checks global force balance. It does not by itself prove that floor and wall loads reach the intended beams, that wall openings are correctly connected, or that seismic mass is correct. Independently compare load-pattern totals, element actions, story masses and reactions against the same ETABS case; assess slab mesh refinement and diaphragm constraints.

## Nonlinear path and outstanding evidence

1. Preserve an immutable ETABS export and analysis configuration with source hashes. Inspect core web/flange connectivity, openings, floor and beam support paths, restraints and local axes. The axis-aligned opening screen is not a complete geometric or coupling-beam validation.
2. Use measured or documented project rebar coordinates, ties, steel and concrete properties, and region-specific wall reinforcement to construct frame sections and FSAM panels. Published specimen cards are useful benchmarks and sensitivity cases; they do not establish this building's material calibration.
3. Test isolated frame sections, wall panels and the corner/opening assembly under relevant cyclic axial, shear and flexural loading; compare against independently documented data. Verify actual FVD force-velocity-stroke response and BRB cyclic/buckling assumptions, connection properties and damping allocation.
4. Reproduce the prior first-step failure using fresh isolated ZERO, X, Y and XY cases, saving last accepted state, failed-step diagnostics and exact model and motion hashes. A nonfinite wall response after failure is a localization clue, not proof of cause. Do not reuse a contaminated domain as a new case.
5. Verify nonlinear gravity and initial modes, time-step sensitivity, damping and record provenance, then execute full-duration ULS/SLS XY/YX cases. Linear time-history results are useful comparison evidence but are not, by themselves, a prerequisite for the equations of nonlinear time integration. Any additional code/project requirements must be reviewed independently.
6. Compare outrigger alternatives only after controlling geometry, mass, record pairs, orientations, gravity assumptions and output definitions. Record configuration, location, device properties, failed cases and separately report ULS and SLS demands. An optimum cannot be determined from incomplete analyses.

## Code findings in this review

* `components/nonlinear_time_history/full_record_gate.py`: the time-step comparison accepted string-valued step sizes but compared the original strings. Scientific notation could cause a valid finer run to be rejected. This review changes the comparison to numeric values and adds a regression test.
* The same function previously compared only model and paired-record hashes, which cannot distinguish XY from YX for the same record pair. It now requires matching nonempty `limit_state`, `orientation` and `diagnostic_excitation`. These fields must be supplied by comparison callers. This is a case-identity screen, not proof that all damping, solver, scaling, geometry or output settings match; these remain necessary provenance checks.
* `variant_comparison.py` compares recorded metadata and numerical gates, not independent physical verification. Its response aggregation and XY/YX governing rule must be examined against the official code and the project's approved interpretation. A metadata match is not proof of calibration or of an actual optimal arrangement.
* `research_building_materials.py` retains a project material qualification gate. Source code reports research templates rather than project-calibrated wall/frame materials. Preserve that distinction; a published experimental specimen cannot fill missing project reinforcement or confinement evidence.

## Sources and meaning

* [NBC 105:2025, DUDBC](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf) governs the project seismic checks; review the original text and code applicability, including reported cross-reference ambiguity, rather than treating a software label as compliance.
* [Kolozvari, López and Massone (2023), E-SFI-MVLEM-3D documentation](https://kkolozvari.github.io/E-SFI-MVLEM-3D/) describes the four-node wall formulation and specimen comparisons. Its published specimens do not independently validate this building's openings, reinforcement or loading history.
* [OpenSees E-SFI-MVLEM-3D documentation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html) defines the element inputs, FSAM fibers, node ordering and recorders.
* [OpenSees UniformExcitation documentation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html) states that nodal responses are relative; absolute floor acceleration requires the appropriate ground acceleration to be added in matching units and directions.
* [PEER 2015/12](https://peer.berkeley.edu/publications/2015-12) documents shear-flexure interaction modeling and its experimental background. The repository's `docs/00_RESEARCH_REFERENCES.md` supplies further material and device citations and transfer restrictions.

## Verification and limitations

The time-step gate regression and selected solver-free wall geometry, opening, material gate, failure evidence, variant comparison, nonlinear code-audit and acceleration tests passed in the local Windows Python environment. These are software checks, not a native full-building run. No full earthquake history, independent specimen reproduction or design-code certification was completed in this review. The first-step nonlinear failure is unresolved.

