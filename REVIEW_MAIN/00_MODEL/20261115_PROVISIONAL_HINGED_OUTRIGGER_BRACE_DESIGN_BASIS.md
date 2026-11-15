# Engineering Design-Basis Decision DB-OUT-2026-11-15-01
## Provisional pin-ended outrigger diagonals for the 25-storey thesis model

| Field | Adopted record |
| --- | --- |
| Date | 15 November 2026 (Nepal) |
| Project | *Time history analysis of damped outrigger system in high rise building with asymmetric plan* |
| Decision owner | Researcher — affirmative instruction: "for now I will follow as hinged braces and move forward" |
| Source case | Latest 25-storey ETABS to OpenSeesPy export; original EDB and all exports remain read-only |
| Design assumption | **Retain existing ETABS pin-ended steel outrigger diagonal braces** as the current idealized truss model |
| Acceptance | **PROVISIONAL_DESIGN_BASIS — NOT PHYSICALLY VERIFIED** |
| Permitted work | Export/topology, model identity, gravity, elastic/modal/ESM/MRSM *diagnostic* comparisons and explicitly labelled exploratory nonlinear runs under existing software gates |
| Prohibited inference | Do **not** infer the real connections are pins; do **not** classify all members as braces, equate source/preview/solver tags, auto-enable reviewed NLTHA or claim calibrated nonlinear brace behavior |
| Revision trigger | Connection drawing/release evidence, native model comparison, non-axial forces, mechanism/instability, materially important sensitivity, BRB/FVD device details, or physically unrepresentative cyclic behavior |

### 1. Exact yes/no finding and limits

**YES, conditionally**, for *individual steel diagonal members that are intentionally idealized as pin-ended, two-force members in a triangulated outrigger truss*. The idealization carries axial tension/compression and develops the outrigger system's core-restraint action through coupled chord forces, bracing and axial reaction in engaged exterior columns. This **does not** hinge the *entire outrigger assembly*. The structural adequacy depends on retaining its truss geometry, top/bottom chord and panel-zone load path, core-to-steel and perimeter-column interfaces, diaphragm compatibility and connection axial/shear transfer.

**NO** to assuming every chord, coupling beam, RC member, belt connection, cap-truss connection or device link has negligible moment capacity. Member label, vertical level, diagonal orientation or an ETABS BRACE category is not proof of a truly pinned or axial-only connection.

A *mathematical idealization* is legitimate for a research model if it is explicitly stated, consistently applied to M0–M6 and tested against alternatives. It is **not evidence of project detailing or experimental validation**. This working decision retains currently modelled releases instead of redesigning them without drawings or changing source objects.

### 2. Structural mechanics and what the hinges do

With pin-ended diagonal truss members, their dominant small-displacement axial stiffness is approximately

`k_axial = EA/L`

and local axial force is `N = EA/L * delta_axial` in the elastic small-strain limit. Transverse end moments carried *by the ideal brace* are zero, but the truss's overall flexural resistance is **not** zero: bracing/chord equilibrium creates an axial force couple. The RC core rotates laterally; the outrigger resists rotation by transferring axial force to exterior columns (tension/compression), thereby changing global drift and overturning distribution. Geometric nonlinearity, P-Delta effects, member buckling and joint eccentricities require separate treatment.

Hinging the *diagonal* is not identical to hinging the *core-to-outrigger interface*, or releasing every chord in a frame model. The actual gusset/embedded plate connection may transfer transverse shear, some moment, secondary bending from eccentricity, or cyclic pinching. If loads are not applied at truss joints, pure pin-ended idealization can omit local bending. The axial-only simplification may change frame action, buckling resistance, bending redistribution, stiffness, natural periods, roof drift, base reactions and FVD relative velocity. A 3D stability and non-axial-force audit is essential.

### 3. Source-backed engineering references and accurate interpretation

**R-OUT-01 — primary specialist design guide.** Choi, H. S.; Ho, G.; Joseph, L.; Mathias, N., *Outrigger Design for High-Rise Buildings: An Output of the CTBUH Outrigger Working Group*. Council on Tall Buildings and Urban Habitat, first published 2012, Routledge edition 2014 (hardback 2017). ISBN 978-0-939493-34-0 (paperback). Relevant **book-printed** sections:
- §2.2, *Load Transfer Paths in Outrigger Systems*, printed **p. 27**: core rotation opposed through perimeter-column axial force couple; system response depends on core/outtrigger flexural and shear stiffness plus engaged column axial stiffness. Also addresses differential shortening and belt-truss diaphragm-mediated load path.
- §2.8, *Load Path from Connections*, printed **pp. 34–36**, notably **p. 35** and Fig. 2.4: reversed large forces must pass through the core and perimeter connection; steel-to-concrete connection design is nontrivial, and a steel diagonal may deliver vertical and horizontal force components to embedded plates.
- §3.5, Jin Mao Building example, printed **pp. 60–61**, Figs. 3.39–3.40: temporary erection pins in slotted holes were later **locked with bolts/connection plates**. Temporary pin details do **not** justify assuming an operational connection always remains an ideal pin.

**Inference:** supports treating steel outrigger *truss diagonals* as an axial-force structural mechanism under a clearly idealized truss model; **does not state universal pin releases or validate this building's six-DOF ETABS release assignments**.

**R-OUT-02 — outrigger numerical study.** Gunda, P.; Anthugari, V. (2022), "Optimization of location of outrigger system in tall buildings of different aspect ratios," *Materials Today: Proceedings* **52**, pp. **588–598**, DOI **10.1016/j.matpr.2021.10.034** (online October 22, 2021). Printed **p. 589**, §2: one-storey steel outrigger truss with **ISWB450 top/bottom chords** and **300×300×15 mm square tube diagonal members**; compares seismic roof displacement, drift and overturning responses across building aspect ratios. This is an example of separate chord/diagonal modeling. **It does not document that all its ETABS frame members were assigned pin-end releases; do not cite it as proof of that detail.**

**R-OUT-03 — finite-element mechanics reference.** Shrikhande, M., *Finite Element Method and Computational Structural Dynamics*, PHI Learning, ISBN **978-81-203-4995-7**. Uploaded edition's Chapter 2, §§2.2–2.5, **pp. 32–66**, covers one-dimensional finite-element modeling, assembly, boundary conditions and Euler–Bernoulli beam/beam-column members. This supports choosing consistent stiffness/DOFs for axial members versus flexural members; **it is not outrigger-specific hinge design guidance**.

**R-OUT-04 — supplementary seismic modeling book.** Agarwal, P. & Shrikhande, M., *Earthquake Resistant Design of Structures*, PHI, 2006. The uploaded scan's contents list Chapters 11–12 and 19 on structural dynamics, seismic idealization and multi-storey RC modeling. **Not a direct endorsement of outrigger end hinges.**

**Not applicable as hinge justification:** Dvorkin & Bathe (1984), "A continuum mechanics based four-node shell element for general non-linear analysis," *Engineering Computations* 1(1), pp. 77–88, DOI **10.1108/eb023562**, and Bathe & Dvorkin (1985), "A four-node plate bending element based on Mindlin/Reissner plate theory and a mixed interpolation," *International Journal for Numerical Methods in Engineering* 21, pp. 367–383. They address **shell/plate elements**, not outrigger brace end releases. Cite them for appropriate slab/wall FE formulation and mesh verification, not for the pin decision.

**Native command interpretation references:**
- CSI ETABS cFrameObj GetReleases/SetReleases API, six local end DOFs U1/U2/U3/R1/R2/R3 with optional partial-fixity springs: https://docs.csiamerica.com/help-files/etabs-api-2016/html/967eb7da-6e42-0708-a4e9-00a61d506575.htm (SetReleases interface as a check on stored arrays).
- OpenSees 3D elasticBeamColumn end-release syntax and torsion: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/elasticBeamColumn.html
- OpenSees CorotationalTruss axial formulation: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/CorotationalTruss.html

The specialist guide is the primary outrigger source, the numerical outrigger paper is contextual support, and the textbooks support discretization/general mechanics. **No supplied source certifies these exact ETABS connection details.**

### 4. Adopted classification policy — source identity is never guessed

| Thesis display family/role | Member meaning | Interim pin rule |
| --- | --- | --- |
| BR — brace parent family | Ordinary steel axial brace | Pin-ended diagonal idealization allowed if the source member is genuinely a diagonal axial brace |
| CO — conventional outrigger | Core-to-perimeter outrigger system members | **Only source-verified diagonals** may take pin-ended axial assumption; chord/core/column interfaces still need their real stiffness |
| BT — belt truss | Perimeter belt system members | Pin-ended individual diagonal allowed if truss geometry/diaphragm path is preserved; **do not release whole perimeter lateral path by default** |
| CT — cap truss | 25th-storey cap system members | Same conditional brace idealization; roof level alone does **not** decide the physical end condition |
| B/C | Concrete/steel beams and columns | No blanket pin releases; retain their source moment/axial properties |
| SW/FL | RC wall/slab | No brace release assumptions |
| BRB/FVD | Buckling-restrained brace / fluid viscous damper | Device-specific link/hysteresis, deformation capacity, reference testing and damping model; **not an ordinary hinge steel brace substitute** |

The available November 15 report flagged **112 ETABS frame unique IDs** (example **ETABS 1308 / topology preview 25049**) matching the importer's specialized hinged-brace pattern. These **are not solver errors**, and the old warning text `solver tag pending assembly` identifies a report-generation stage, not failed assembly. Source ETABS ID, topology tag and assembled OpenSees integer element IDs are distinct. PR #79 added `hinged_brace_release_review` with raw release arrays and assembled segment tags to aid review in a *new* export.

Record roles using only exact ETABS source object IDs, not inferred category, storey, diagonal geometry, or a solver tag. Treat role assignment as display/provenance, not constitutive-model calibration.

### 5. What the software currently does — preserve honest status

**Existing source:** `components/model/assembly.py` validates a special `BRACE` release pattern with no translations released, both R2 and R3 rotational DOFs released at I and J, at least one R1 release, no partial-fixity spring; other release patterns are rejected until explicitly implemented.

**Elastic branch:** `elasticBeamColumn` with bending `-releasey/-releasez` and torsional J set to zero for this brace pattern. The resulting effective member's **axial and global frame response require benchmarking**, with rotational nullity, zero torsional transfer and any transverse-load behavior checked.

**Exploratory nonlinear branch:** conditionally `corotTruss` with `Steel01` axial law for hinged-brace members. This captures an **idealized axial, geometric-nonlinear** member; **it does not by itself reproduce cyclic compression buckling, local SHS wall degradation, brace fracture, project-specific steel hardening, or joint hysteresis**. Exploratory output must be so labeled.

**Reviewed nonlinear branch:** explicitly raises on `hinged_brace` without qualified formulation. This safety gate **stays ON**: adopting the pin decision does not satisfy nonlinear material or connection calibration.

**Decision is not permission** to suppress the warnings, set `nonlinear_parameters_reviewed=true`, fabricate `nonlinear_materials_file`, fill FSAM tags, or change `M0-M6` device configurations. It authorizes continuing valid preliminary analysis under their existing acceptance labels, **not calling completed full NLTHA**.

### 6. Minimum tests to progress toward accepted quantitative results

1. **Source/identity gate (P0):** In the current regenerated export, extract 112 source `GetReleases` arrays, original category/section and geometry, core-wall/column joint connections, and original insertion/local axes. Count and reconcile source BR/CO/BT/CT across all storeys. No unlabeled guessed CT.
2. **Single diagonal elastic gate (P0):** compare an isolated steel SHS member under +N/-N, imposed translations/rotations and transverse perturbation in ETABS and OpenSees. Evaluate axial `EA/L`, end force/moment transfer, strain energy, zero/near-zero modes and geometric stiffness; determine whether released beam formulation is equivalent to intended two-force member.
3. **Outrigger subassembly gate (P0):** apply known core rotation plus exterior-column translation/axial restraint to a core-to-perimeter assembly; check column tension/compression couple and opposing core moment, member axial force, diaphragm participation and no missing load path/mechanism. Compare pinned vs finite joint-rotational-stiffness cases, preserving geometry/material/source loads. Include one CO, BT and CT physical group where present. Predefine engineering acceptance thresholds **before** judging results.
4. **Elastic whole-building gate (P1):** preserve original support/mass/gravity source identity; compare ETABS vs OpenSees gravity reactions (32 vs 76/97 separately), ULS/SLS eigenperiods and mass participation, roof displacement, base/storey shears, drift/torsion, brace axial forces and connection transfer. Distinguish 1.0D+1.0L gravity study from current 1.0D+0.3L seismic-mass/preload factors.
5. **Nonlinear brace/device gate (P1):** source-specific SHS compression buckling, local buckling, cyclic stress degradation and fracture needs; FVD `K,C_d,alpha` and installation stroke; BRB core area, yield, hardening, overstrength; cyclic test or carefully defined literature transfer with sensitivity, no invented manufacturer specification. Separate device vs ordinary brace. Review whether the pin idealization is compatible with device end articulations.
6. **Thesis modeling sensitivity gate (P1):** run at least axial pinned, semi-rigid connection and moment-carrying alternative for representative outrigger assemblies **only if physically plausible**. Compare `T1_X/T1_Y`, drift, torsion, core overturning, column axial forces, outrigger force, damper stroke/velocity/energy and P-Delta stability. This is a **modeling uncertainty study**, not a forced conclusion that pinned is always better.
7. **NBC / time-history gate (P2):** NBC 105:2025 governs seismic design; approved signed P-Delta initial states, source-matched ground-motion pairs in both XY/YX orientations and complete M0–M6 record duration require their existing separate native evidence. A local one-bay trial is not an accepted global run.

These are **future acceptance tests**. None is represented as already passed by the current design-basis decision or source-only CI.

### 7. Research reporting language (pasteable methodology)

> The steel diagonal members of the outrigger trusses were idealized as pin-ended, primarily axial-force members for the baseline comparative study. This idealization follows classical truss action, in which the outrigger restrains core rotation through a system of truss-member axial forces and the axial resistance of engaged perimeter columns. The specialist CTBUH *Outrigger Design for High-Rise Buildings* guide describes the core-to-perimeter load-transfer mechanism and emphasizes that the connection, panel-zone and diaphragm load paths must remain represented. Consequently, the pin assumption was applied to the designated diagonal members only; it was not taken as evidence that all chords, wall connections, perimeter connections, belt or cap connections were physically hinged. The current model uses the source ETABS member releases consistently across the baseline configurations. Connection-rotational-stiffness sensitivity, native ETABS–OpenSees member equivalence, and cyclic brace stability and material calibration remain separate validation tasks. Results derived before those gates are satisfied are identified as provisional or exploratory and not as completed performance-based seismic acceptance.

### 8. Review status and document lineage

- **USER_ADOPTED / PROVISIONAL** — retain hinged diagonal-brace idealization to continue elastic validation and approved exploratory investigations.
- **SOURCE_MECHANISM_DOCUMENTED** — specialist outrigger load-path reference and FEM text cited with limited claims.
- **ETABS_SOURCE_RELEASES_RECORDED** — detailed revised report path available *after regenerating source export*; no fabricated arrays.
- **MEMBER_EQUIVALENCE_NOT_VERIFIED / CONNECTION_NOT_VERIFIED / NONLINEAR_NOT_CALIBRATED / NATIVE_NOT_RUN** — not promoted by this documentation.
- This record supplements `REVIEW_MAIN/00_MODEL/20261115_AREA_HINGED_BRACE_AND_MESH_EVIDENCE.md`. It does not amend original ETABS source files, original member release values, solver numerical formulations, M0–M6 scenarios or previously stored results.
