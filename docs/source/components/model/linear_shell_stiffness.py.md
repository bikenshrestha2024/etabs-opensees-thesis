# Linear elastic ShellMITC4 source-modifier wall model

This module is used **only** when \`linear_shell_stiffness_policy\` is
\`TABULATED_REVIEWED_THIN_SHELL\` and \`mode="elastic"\` in
\`components/model/assembly.py\`. It does not change nonlinear wall
materials, ground-motion records, gravity loads, support conditions,
mass ledgers or source geometry.

## Engineering decision

Original ETABS v23 ULS screenshots (2026-11-08) establish that
\`Wall 600\` Shell-Thin has:
- \`f11=f22=f12=0.5\`: membrane/in-plane behavior
- \`m11=m22=m12=0.1\`: plate/out-of-plane bending
- \`v13=v23=1.0\`: transverse shear
- mass and weight factors = 1.0
- original thickness = 0.600 m.

\`Slab 150\` has membrane = 1.0; plate = 0.25; transverse shear = 1.0;
mass and weight = 1.0. This is *property-level screenshot evidence*,
NOT verification that every ETABS object-level modifier is unity.
The source EDB must be re-exported to verify property and object
modifiers before marking ETABS model equivalence.

For linearly elastic 3D baseline (gravity, modal, equivalent static
and response spectrum), a wall represented using \`ShellMITC4\` with
\`ElasticMembranePlateSection\` can independently set

\`\`\`python
E_membrane = f * E_gross
E_plate = m * E_gross
Ep_modifier = E_plate/E_membrane = m/f
ops.section("ElasticMembranePlateSection",secTag,
            E_membrane, nu, original_thickness, 0.0, Ep_modifier)
ops.element("ShellMITC4",eleTag,n1,n2,n3,n4,secTag)
\`\`\`

For Wall 600: \`E_membrane=0.5 E\`, \`E_plate=0.1 E\`,
\`Ep_modifier=0.2\`, \`h=0.600 m\`. For Slab 150:
\`E_membrane=E\`, \`E_plate=0.25 E\`,
\`Ep_modifier=0.25\`, \`h=0.150 m\`.

**CRITICAL limitation verified from OpenSees C++ source**:
\`ElasticMembranePlateSection::getSectionTangent()\` computes the
transverse shear stiffness using \`G*5/6*(Ep/Em)\`.
Consequently, the section's *effective transverse shear modifier*
is \`m\`, not the independently assigned ETABS \`v13=v23=1\`.
For Wall 600 it is 0.1, and for Slab 150 it is 0.25.
This formulation is therefore **NOT an exact reproduction of all
ten CSI shell modifiers**, even though it faithfully reproduces the
uniform membrane and plate-bending blocks. Thin-shell behavior may be
insensitive to that difference for particular results, but it must
be demonstrated with patch and mesh sensitivity tests, not assumed.

The module therefore **fails closed by default** whenever source
transverse shear differs from the section's actual shear. Researchers
may consciously select the following *diagnostic* config:

\`\`\`json
{
  "linear_shell_stiffness_policy": "TABULATED_REVIEWED_THIN_SHELL",
  "linear_shell_transverse_shear_policy": "ALLOW_REVIEWED_THIN_SHELL_APPROX",
  "linear_shell_modifiers_by_property": {
    "Wall 600": {
      "f11": 0.5, "f22": 0.5, "f12": 0.5,
      "m11": 0.1, "m22": 0.1, "m12": 0.1,
      "v13": 1.0, "v23": 1.0,
      "mass": 1.0, "weight": 1.0
    },
    "Slab 150": {
      "f11": 1.0, "f22": 1.0, "f12": 1.0,
      "m11": 0.25, "m22": 0.25, "m12": 0.25,
      "v13": 1.0, "v23": 1.0,
      "mass": 1.0, "weight": 1.0
    }
  }
}
\`\`\`

This is an **illustrative JSON fragment**, not a complete
\`OpenSees_Complete_Model_Config_V118.json\`; merge these keys into
the existing config *without removing other settings*. The converter
requires one explicit vector for **every shell property actually used**
(e.g. any other wall thickness, outrigger wall or slab property).
It blocks missing properties, nonuniform in-plane/bending factors,
missing inputs, non-unity mass/weight factors and nonlinear use.
Do not copy Wall 600 factors to all other walls.

**After editing source config, rebuild the export**. An existing
\`OpenSees_Complete_Model_Data_V118.json\` has a SHA-256 of the config;
a run with mismatched hash is intentionally rejected. Better: start
with a separate isolated copy of the source export.

The runtime creates \`Linear_Shell_Stiffness_Audit.json\` with per-property
actual effective factors and the non-exact transverse-shear flag.

## Required mechanical checks for the 25-storey validation model

1. Verify native ETABS source property **and object** modifiers, and
   shell local axes. CSI says object and property factors multiply.
2. Test isolated membrane \`Nx-Nx\`, \`Ny-Ny\`, in-plane shear, bending
   \`Mx-My\`, transverse shear and density, with each reference
   section before the full building. The current shear approximation
   must be characterized separately.
3. Run full-gravity \`1.0DL+1.0LL\` (including assigned roof live),
   *not* 0.3 live. Confirm applied load / support reaction equilibrium.
4. Compare the unchanged 76 ETABS support points by node and by
   independently verified wall-pier/column foundation region. The
   97-support continuous wall base remains a sensitivity run.
5. Compare diaphragm-displacement patterns, vertical displacements,
   columns, walls and elastic modal periods / cumulative mass.
6. Compare ESM and MRSM using the **same ETABS ULS model** with the
   same mass source, boundary conditions, geometry, stiffness and
   load combinations. Do not silently apply cracking factors twice.
7. Only after establishing elastic equivalence, develop the separate
   E-SFI-MVLEM-3D nonlinear wall model with calibrated physical
   reinforcement/confinement and member models; do **not** automatically
   multiply nonlinear fiber material moduli by elastic ULS factors.

If a strict \`v13=v23=1\` reproduction is necessary, it requires a
shell formulation whose section tangent separately controls membrane,
bending and transverse shear, and independent element-level tests.
The standard OpenSees \`ElasticMembranePlateSection\` alone cannot
represent it. Do not pretend that a wall-element rename solves this.

**References**
- OpenSees \`ShellMITC4\`:
  https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html
- OpenSees \`ElasticMembranePlateSection\`:
  https://openseespydoc.readthedocs.io/en/latest/src/elasticMembranePlateSection.html
- OpenSees section **actual implementation**:
  https://github.com/OpenSees/OpenSees/blob/master/SRC/material/section/ElasticMembranePlateSection.cpp
- CSI ETABS modifiers and section/object multiplication:
  https://docs.csiamerica.com/help-files/etabs/Menus/Define/Property_Stiffness_Modification_Factors_Form.htm
- CSI wall membrane stiffness mapping:
  https://web.wiki.csiamerica.com/wiki/spaces/etabs/pages/1474670

**Test:** \`python tests/verify_linear_shell_stiffness.py\`

## 2026-11-27 — independent shear layered-shell qualification candidate

**Literature:** Lu, X., Xie, L., Guan, H., Huang, Y., Lu, X. (2015), *A shear wall element for nonlinear seismic analysis of super-tall buildings using OpenSees*, Finite Elements in Analysis and Design 98, 14–25, https://doi.org/10.1016/j.finel.2015.01.006. This supports multilayer shell modeling, not the derived artificial elastic layer moduli. CSI's Shell-Thin neglects transverse shear deformation (https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2001188/Shell%2BFAQ); matching a finite shear modulus in MITC4 therefore does not demonstrate thin-shell equivalence.

**Derivation:** for three equal thickness layers with midpoint coordinates (-h/3, 0, h/3), symmetric outer factor a=9m/8 and middle factor b=3f-2a give A=f Q h, B=0 and D=m Q h^3/12. Reject nonpositive factors and unequal membrane/bending/shear modifier groups. Use a common out-of-plane modulus Gout=c v G, with c explicitly 1 or 5/6; no implicit ETABS shear correction. Source https://github.com/OpenSees/OpenSees/blob/master/SRC/material/section/LayeredShellFiberSection.cpp integrates direct shear and uses negative curvature in fiber strains, so recorded bending resultants are compared to -D curvature. https://openseespydoc.readthedocs.io/en/latest/src/PlateFromPlaneStress.html documents the wrapper. Numerical layers are not physical concrete layers. No mass or gravity changes; zero material density for independent nodal mass ledger use.

**Execution:** `python -m unittest tests.verify_linear_shell_stiffness` for analytical checks, `python -m tests.native_layered_shell_patch native_layered_shell_results` with conda-forge OpenSees Tcl on PATH for native component checks. Each patch independently assembles a model, imposes kinematic fields using SP penalty constraints, checks native Gauss point forces versus measured strains in all eight section components, and archives raw output and native logs. Three mesh densities (1,2,4) check consistency under prescribed fields, not load-controlled plate convergence. No production assembly caller or new default. Actual EDB/analysis workbook unavailable; ETABS equivalence, P-Delta, full gravity and nonlinear use remain unqualified. Preserve 32 physical supports, 44 mesh points, two 12 m X walls, full 1D+1L and separate NBC seismic weight.
