# Literature-to-thesis verification and implementation matrix (2026-11-14)

**Scope:** Maps original uploaded PDFs U01–U15, indexed in [UPLOAD_INVENTORY_20261114.md](UPLOAD_INVENTORY_20261114.md), to the project's five outstanding engineering and software questions. This is a verification plan, not a claim that the source work has validated the user's structure. Prefer NBC 105:2025 for seismic design. IS 16700 project-adopted exceptions are separately recorded in the governing code matrix.

| Workstream | Applicable uploaded references | What literature actually supports | Engineering implementation / test | Unresolved status |
|---|---|---|---|---|
| Exact 32/76/97 ETABS/OpenSees support reactions | U03 Schwer 2005, U09 Schwer 2006 (V&V framework), U04 García/Rea 2019 (workflow poster) | Confidence requires independent verification; converter does NOT automatically prove node matching | Export source six-DOF restraint table, analytical mesh, auto-edge constraints, mapped OpenSees equation reduction; compare all **76 source support coordinates** and reaction vectors, including 44 zero-Rz ETABS points; then test 32 and 97 diagnostics separately | **BLOCKED**: uploaded studies do not specify ETABS mesh restraints or a correct project fix. Need official CSI/solver docs and case files |
| ShellMITC4 slab-to-frame/wall vertical loads | U05 Bathe/Dvorkin 1985; U15 Dvorkin/Bathe 1984 (patch tests, Fig.4; stiffened plate, Fig.14; plate displacement, Tables 3/4; cylinder refinement, Tables 6/7); U03/U09 V&V; U04 poster (elastic slab workflow) | Mixed-interpolation four-node plate formulations can be benchmarked; plate numerical accuracy alone does not establish interface compatibility or application of rigid diaphragms | Analytical simply supported/slab patch test; identical loads/moments; conforming beam/wall edge nodes; shell local axes, real plate thickness/stiffness; MESH_04/08/16 deflection, beam/wall force, reaction sensitivity | **BLOCKED**; paper does not prescribe an automated ETABS-to-OpenSees gravity load conversion |
| Hinged brace / conventional outrigger / belt / cap truss | U06 Xing 2021; U07 Alhaddad 2020 | Outrigger effects depend on layout, relative core/frame stiffness, restraint and damping; simplified single-outrigger optimization cannot calibrate current SHS brace joints | Source ETABS frame 1308 local I/J My/Mz/R1 releases, end offsets, nonlinear model, torque/axial; compare axial, shear, torsion, end moments and displacements with elastic beams and axial-only truss candidates under a small isolated model | **BLOCKED**; no automatic member conversion or zero-torsion J warranted by papers |
| Nonlinear wall materials / first-step X failure | U08 Kolozvari 2018; U12 PEER 2015/12; U13 Kolozvari 2021; U14 Kolozvari 2023; U10 Charney 2008; U11 PEER TBI 2017 | FSAM, ConcreteCM, SteelMPF, shear-flexure interaction and experimentally tested nonplanar walls provide reproduction targets; nonlinear Rayleigh damping may produce artificial forces | Reproduce selected publication specimens with published parameters; then project wall opening, coupling beams, boundary confinement/axial ratio and single panel X/Y/XY trials; run ZERO motion first; audit wall localForce and damping energies before full NLTHA | **BLOCKED** until actual project steel/concrete reinforcement, section axial loads and FSAM material calibration |
| GUI, immutable evidence, source governance | U01 Wilkinson 2016, U02 Nobile 2025, U03 Schwer 2005, U04 García/Rea poster, U09 Schwer 2006 | FAIR metadata, explicit reproducibility and separate solver-vs-real-world evidence; no particular Python widget/UI implementation is prescribed | Stable source/solver tag mapping, one canonical stage index, filename/sha/provenance, nonblocking GUI with logs, status per run, paper citations with local source locators and independent benchmarks | **PARTIAL**: repository software tests; native GUI and project evidence acceptance outstanding |
| Modal ULS 2026-11-14 | U03/U09 V&V, U11 PEER TBI, U01 reproducibility, U15 shell element frequency Table 4 (formulation-specific benchmark only) | Independent modal response verification, explicit model provenance; do not mistake numerical mass participation for model equivalence | Compare Rayleigh X/Y periods to same-state ETABS, inspect positive eigenvalues and X/Y mode shape and torsional coupling, record basis mass in kN–m–s; check modal participation and 33 Hz cut-off | **NUMERICALLY COMPLETED; PHYSICAL VERIFICATION OPEN** |

## Newly received U15 (Dvorkin & Bathe 1984): additional shell verification evidence

The original publisher PDF supplies **six-rigid-mode, zero-energy-mode and mixed-interpolation patch tests (pp. 79–81)**, plus **stiffened plate / 3 shell+beam example (p. 84)** and **mesh-convergence numbers (p. 85)**. In the authors' simply supported plate example `u3_FEM/u3_thin-plate` was 0.995 on an undistorted mesh and 0.992 on a distorted mesh (p. 83). These are source-specific reference responses **not** automatic targets for the user's ETABS-to-OpenSees floor. Their pinched-cylinder ratios improved 0.51→0.83→0.96 under 5×5→10×10→20×20 refinement (p. 85); this reinforces the requirement to compare responses, not just cell counts. Full independent formulation + figure crosswalk: [DVORKIN_BATHE_1984_SHELL_BENCHMARKS.md](DVORKIN_BATHE_1984_SHELL_BENCHMARKS.md).

**Correct code action:** implement the isolated stiffened-plate/shell-beam DOF/force patch first; confirm physical shell edge load and moment equilibrium and absence of spurious modes; do NOT import the 1984 reported ratios as a pass/fail threshold for 4/8/16. Keep source-specific references to uploaded pages without publicly publishing the subscription PDF.

## Core literature interpretation
- U05 (1985) derives plate bending/mixed interpolation and provides example numerical results: it does not guarantee ETABS and OpenSees have equivalent shell-to-frame constraints.
- U06 (2021) optimized three *single-outrigger* systems under wind/seismic excitations: use only as a **sensitivity/prior source**, not proof of M0–M6 high-rise optimum or damper calibration.
- U07 (2020) reviews structural topology and size: relevant for differentiating chords, diagonals, belt/cap trusses but no authority to make all brace elements pin-ended or tension-only.
- U08 (2018) discusses MVLEM, SFI-MVLEM, FSAM, ConcreteCM and SteelMPF and cyclic experiments; do not substitute specimen dimensions, bar grades or cyclic fits for project material files.
- U13 (2021) reports useful U-shaped wall multidirectional tests but notes reduced accuracy in diagonal-loading local strain/shear-lag behavior. This is directly relevant to the user's asymmetric core and XY/YX analysis.
- U14 (2023) reports an E-SFI-MVLEM-3D computational formulation and 3 experimental wall benchmarks; it does not directly resolve a non-finite localForce at user's wall element tags.
- U10 Charney 2008 demonstrates potential artificial Rayleigh damping in yielding systems; audit Rayleigh coefficients and treatment of added device damping.
- U11 PEER TBI is design/research guidance; project governing seismic code is **NBC 105:2025**, not PEER/ASCE as an unlabelled replacement.
- U01 provides FAIR principles for not only data but algorithms and workflows; model/source and output provenance should be machine-readable, not a ZIP without case identity.
- U04 is the user-supplied CEO poster and displays an ETABS → two Excel inputs → OpenSees conversion process, including RC beams/fibers, MVLEM wall, rigid diaphragm, P-Delta and recorders. It is a feature comparison, not a data source supporting numerical acceptance.

## Evidence hierarchy / completion definitions
```text
SOURCE_IDENTIFIED
  -> FORMULATION_REPRODUCED (standalone element/material test)
  -> NUMERICAL_VERIFICATION (mesh/time-step convergence, independent analytical check)
  -> PROJECT_INPUTS_RECONCILED (native ETABS geometry/loads/restraints/material provenance)
  -> PROJECT_PHYSICAL_VALIDATION (experimental transferability and quantified limitations)
  -> ENGINEERING_ACCEPTANCE (applicable NBC criteria independently reviewed)
```
If any step is missing, retain a `BLOCKED` or `REVIEW` state, not a guessed PASS. A 40-mode eigen solve, all six ESM case solver completions, or global force equilibrium may support **numerical verification**, but none certifies source-equivalent engineering acceptance.

## Additional official technical documents required (not supplied in this intake)
- CSI ETABS releases, shell auto-mesh/edge constraint and diaphragm/OAPI documentation (version-specific).
- OpenSees `ShellMITC4`, `ElasticMembranePlateSection`, `E-SFI-MVLEM-3D`, `FSAM`, `ConcreteCM`, `SteelMPF`, `rigidDiaphragm`, `equalDOF`, `elasticBeamColumn`, `truss/corotTruss`, `rayleigh` official reference pages.
- Authenticated NBC 105:2025 complete code and applicability notes; source Vs30 evidence for Kirtipur high-rise.
- Project ETABS source EDB, original material/rebar assignments, matching model/solver SHA; non-public originals must remain private.
- Reproducible 32/76/97 signed reaction ledger and 4/8/16 exact source-matched gravity cases.
