# U15 / L048 — Dvorkin & Bathe (1984): source-specific shell benchmarks

**Full reference.** Dvorkin, Eduardo N., and Bathe, Klaus-Jürgen (1984). “A continuum mechanics based four-node shell element for general non-linear analysis.” *Engineering Computations*, **1**(1), 77–88. DOI: https://doi.org/10.1108/eb023562. Original private upload: `dvorkin1984(1).pdf` (13 uploaded pages: publisher cover + 12 article pages). The PDF first-page header directly confirms authors, volume/issue/pages and DOI. Publisher subscription notice appears on cover: **do not redistribute**. PDF's “cited by 359” was a historical footer on a file downloaded 2012-11-07, **not a contemporary citation count**. Original uploaded file SHA256 **NOT CALCULATED** in this GitHub review; verify locally with `LITERATURE/tools/audit_private_pdf_uploads.py` before using a hash as provenance.

## Source interpretation and applicability
- **pp. 77–79 (uploaded pp. 2–4):** generalized four-node nonflat continuum-mechanics shell with independent/mixed treatment of transverse shear and large displacement/rotation with small strain. It aims to avoid transverse shear locking and spurious zero-energy modes. It is not an OpenSees `ShellMITC4` program listing and does not establish identical ETABS implementation, drilling freedom, constraint transformation or section law.
- **p. 79 (uploaded p. 4), observations (1)–(3):** six rigid body modes, approximate Kirchhoff-Love thin-shell limit and no spurious zero-energy modes in their formulation; transverse shear stress accuracy explicitly depends on mesh and distortion. The *element formulation* is being benchmarked; project interface/load mapping is separate.
- **p. 81 (uploaded p. 6), Fig. 4:** membrane, bending, transverse-shear and twisting patch tests. In a shell-to-beam patch, compare both nodal forces **and moments**, not only the force sum.
- **p. 82 (uploaded p. 7), Figs. 5/6 and Tables 1/2:** cantilever bending, distorted mesh and local transverse shear; authors explicitly note poor computed transverse shear stress under some distorted meshes. Thus do not use stress peaks at singular corners as a global convergence target.
- **p. 83 (uploaded p. 8), Fig. 7 and Tables 3/4:** simply-supported plate and frequency benchmarks with consistent mass matrix; normalized center plate displacements `u3_FEM/u3_thin_plate`: nondistorted **0.995**, distorted **0.992** for *the authors' exact problem*. This is NOT an expected ratio for the user's 150-mm conventional slab with different edge conditions.
- **p. 84 (uploaded p. 9), Fig. 14:** stiffened plate assembled with **nine shell elements and three two-node beam elements**; shell/beam connector rotations are explicitly discussed. This is the closest small source example to the user's slab–frame interface, but does not verify ETABS constraints.
- **p. 85 (uploaded p. 10), Tables 6–7:** pinched cylinder refinement; reported `w_FEM/w_analytical` **0.51** (5×5 mesh, 130 DOFs), **0.83** (10×10, 510), **0.96** (20×20, 2020). Demonstrates mesh convergence needs explicit response and boundary conditions, **not** permission to claim 4/8/16 building mesh convergence from cell counts.
- **p. 85 (uploaded p. 10), conclusion:** authors explicitly state that formal mathematical convergence study remained useful. Do not cite the paper as universal convergence proof.

## Reproducible tests to implement without altering production model
| Test | Model/load source | Critical checks | Output |
|---|---|---|---|
| S01 rigid body modes | Paper p. 79/81, unconstrained undistorted and distorted single quads | Six rigid modes; no spurious positive/zero-energy modes, element-specific DOF mapping | eigenvalue log, geometric check, version |
| S02 membrane/bending/shear/twist patch | Paper Fig. 4, p. 81 | Analytical displacement and rotations, equilibrium of transverse *nodal forces and moments*, orientation and mesh distortion | per-DOF nodal results and error |
| S03 cantilever | Paper Figs. 5/6, pp. 82–83 | Tip deflection/rotations and resultant member forces vs Bernoulli/Mindlin benchmark; shear stress only at smooth non-singular locations | response and convergence |
| S04 plate displacement/frequency | Paper Fig. 7, pp. 82–83 | Consistent mass, support constraints, analytic deflection/modes, distorted mesh | normalized displacement and eigenfrequencies |
| S05 stiffened plate with beam | Paper Fig. 14, p. 84 | Shared interface DOF, shell-to-beam rotational coupling, beam end forces, displacement compatibility | shell+frame force/moment ledger |
| S06 pinched cylinder | Paper Tables 6/7, p. 85 | Mesh convergence with full source geometry/loads; do not compare unlike element formulations using count alone | w response vs mesh |

**Engineering bridge to ETABS/OpenSees thesis:** add standalone `S05` with one 6-m bay slab, beam at the edge, wall/column line supports and gravity UDL. Run one case with shared nodes, another with documented interpolation constraint mapping, then compare work-conjugate nodal translations/rotations, shell edge resultant forces/moments and bottom reactions. Confirm source ETABS auto-edge constraint settings separately. Afterwards fix all source geometry, loads, stiffness and restraints and compare the building `MESH_04/08/16`. A six-DOF rigid diaphragm constrains in-plane motion only; it does not substitute for vertical shell bending and joint compatibility.

## Acceptance labels
- `BIBLIOGRAPHY_VERIFIED_FROM_UPLOAD`: yes (authors/year/journal/DOI).
- `ORIGINAL_UPLOAD_SHA_VERIFIED`: **no**, pending private local hash.
- `FORMULATION_SOURCE_IDENTIFIED`: yes.
- `SHELL_PATCH_BENCHMARK_REPRODUCED_IN_OPENSEES`: **no**.
- `ETABS_SLAB_TO_FRAME_LOAD_PATH_EQUIVALENT`: **no**.
- `MESH_04_08_16_FULL_BUILDING_CONVERGED`: **no**.
- `NLTHA_SHELL_MODEL_ACCEPTED`: **no**.

**Supplementary sources, not substitutions:** Bathe & Dvorkin (1985) L041, official OpenSees ShellMITC4/ElasticMembranePlateSection commands, CSI ETABS auto-edge constraints / wall auto-mesh, and ASME V&V guidance. Quantitative model-specific acceptance criteria must be independent of arbitrary paper example outcomes.
